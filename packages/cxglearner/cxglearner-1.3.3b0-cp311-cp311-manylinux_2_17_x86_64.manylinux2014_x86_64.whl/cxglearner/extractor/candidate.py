import os
import pickle
import random
from logging import Logger
from typing import Optional, Union, Any, Tuple
from copy import deepcopy
from tqdm import tqdm
import traceback

import torch
import ffrecord
from torch.cuda import device_count

from ..config.config import Config
from ..encoder.encoder import Encoder
from ..utils.file_loader import determine_dataset_name, create_cache_dir, FileReader, convert_dataset_suffix, merge_candidates, convert_ffrecord
from ..utils.predefine import CANDIDATE_SUFFIX, CONSTRUCTIONS_FILE_NAME
from ..utils.utils_extractor import normalize_freq_to_score, get_forbid_slots, LRUCache, patch_batch_to_sentences, rpt_hyper_debug, compose_slots
from .pruner import CandidatePruner, prune_handler
from ..utils.multi_processor import SpawnMultiProcessor as spawn_multi_processor
from ..utils.multi_processor import mp_dynamic_device_data, mp_allocate_data
from ..utils import misc
from ..utils.utils_lm import create_learner_index
from ..lm.association.association import Association
from .beam_search import HighPrecisionSearch, HighRecallSearch, TradeOffSearch


class BaseCandidate(object):
    def __init__(self, config: Config, logger: Logger, encoder: Optional[Encoder] = None,
                 cache_dir: Optional[os.PathLike] = './cache'):
        self.logger = logger
        self.config = config
        self.worker_num = config.extractor.worker_num
        self.allow_cuda = config.extractor.allow_cuda
        self.num_per_gpu = config.extractor.number_per_gpu
        self.gpu_indices = config.extractor.gpu_indices
        self.gpu_cpu_ratio = config.extractor.gpu_cpu_ratio
        self.dataset_path = determine_dataset_name(
            config, config.lm.dataset_path, logger, CANDIDATE_SUFFIX)
        self.candidate_path = config.extractor.candidate_path
        self.seq_length = config.lm.seq_length
        self.seed = config.experiment.seed
        self.mp_mode = config.extractor.mp_mode
        self.pruner_mode = config.extractor.pruner
        if encoder is not None:
            self.encoder = encoder
        else:
            self.encoder = Encoder(config, logger)
        self.ava_levels = {x: i for i, x in enumerate(encoder.ava_levels)}
        # Create cache dir
        self.cache_dir = create_cache_dir(cache_dir, config.experiment.name)
        # Check parallel params & Mp Mode
        self.check_parallel_and_device()
        self.check_pruner_mode()
        self.check_mp_mode(self.mp_mode)

    def build_and_save(self, check_data: Optional[bool] = True) -> None:
        """
        Generate the candidate constructions (pattern) from the given corpus.
        Start workers_num processes and each process deals with a part of data.
        """
        data_num = FileReader(convert_dataset_suffix(self.dataset_path), check_data).n
        self.logger.info("Starting %d workers for generating candidates ... " % self.worker_num)
        self.worker(self, data_num, worker_num=self.worker_num)

        # Merge candidates.
        candidate_num = merge_candidates(
            self.candidate_path, self.worker_num, self.logger, self.cache_dir)
        self.candidate_path = convert_ffrecord(
            self.candidate_path, candidate_num, self.logger, remove_old_file=False)
        self.logger.info("The candidate generation is complete, with a total of `{}` candidates "
                         "available.".format(candidate_num))

    def prune_and_save(self, candidate_path: Union[str, os.PathLike], remove_middle_files: Optional[bool] = True
                       ) -> None:
        candidate_path = convert_dataset_suffix(candidate_path)
        if not os.path.exists(candidate_path):
            err_msg = f"The candidate file `{candidate_path}` cannot be found, " \
                      f"you can call `self.build_and_save()` first."
            self.logger.error(err_msg)
            raise Exception(err_msg)

        middle_file_path, record_path = candidate_path, None
        for strategy, kwargs in self.pruner_mode.items():
            kwargs['logger'] = self.logger
            kwargs['config'] = self.config
            kwargs['encoder'] = self.encoder
            kwargs['cache_dir'] = self.cache_dir
            if record_path is None:
                record_path = middle_file_path
            middle_file_path = prune_handler[strategy].prune(
                middle_file_path, **kwargs)
            if remove_middle_files and record_path != candidate_path:
                os.remove(record_path)
                self.logger.info("The intermediate files `{}` have been deleted due to `remove_middle_files` has "
                                 "been set to True.")
        # Normalize and generate final constructions file
        normed_path = normalize_freq_to_score(middle_file_path)
        if os.path.exists(middle_file_path):
            dst_file_path = os.path.join(
                self.cache_dir, CONSTRUCTIONS_FILE_NAME)
            os.rename(normed_path, dst_file_path)

    @spawn_multi_processor
    def worker(self, proc_id: int, worker_num: int, data_num: int, encoder: Encoder) -> None:
        raise NotImplementedError

    def check_parallel_and_device(self) -> None:
        if not self.allow_cuda:
            if self.gpu_indices is not None and len(self.gpu_indices) > 0:
                self.logger.warning("Though you have set `gpu_indices`, it will be ignored and CUDA won't be used "
                                    "due to your `allow_cuda` setting being false.")
                self.gpu_indices = None
            if self.num_per_gpu > 0:
                self.logger.warning("Though you have set `number_per_gpu`, it will be ignored due to your `allow_cuda` "
                                    "setting being false.")
                self.num_per_gpu = 0
            if self.gpu_cpu_ratio > 0:
                self.logger.warning("Though you have set `gpu_cpu_ratio`, it will be ignored due to your `allow_cuda` "
                                    "setting being false.")
                self.gpu_cpu_ratio = 0.
            else:
                gpu_devices_num = device_count()
                if self.gpu_indices is not None and (len(self.gpu_indices) > gpu_devices_num or
                                                     max(self.gpu_indices) >= gpu_devices_num):
                    self.logger.warning("The `gpu_indices` seems to be set incorrectly, it does not match "
                                        "the number of physical devices, "
                                        "so the settings will be ignored. Please check.")
                    self.allow_cuda, self.gpu_indices = False, None

    def check_mp_mode(self, mp_mode: str) -> None:
        if mp_mode not in ["high-precision", "high-recall", "trade-off"]:
            error_prompt = "The `mp_mode` seems to be set incorrectly, it can only be selected in [high-precision, " \
                           "high-recall, trade-off], please check the document."
            self.logger.error(error_prompt)
            raise Exception(error_prompt)

    def check_pruner_mode(self) -> None:
        pruner_mode = deepcopy(self.pruner_mode)
        for strategy in pruner_mode:
            if strategy not in prune_handler.keys():
                self.logger.warning("There is no pruner named `{}`, ignored. Please ensure it has been "
                                    "registered.".format(strategy))
                del self.pruner_mode[strategy]

    def get_item(self, reader: ffrecord.FileReader, indices: Union[int, list]) -> Any:
        if isinstance(indices, list):
            data = reader.read(indices)
            samples = [pickle.loads(b) for b in data]
            return samples
        else:
            data = reader.read_one(indices)
            sample = pickle.loads(data)
            return sample


class Candidate(BaseCandidate):
    """
    Search for candidate constructions from the given corpus (generated via Encoder.Dataset).
    Each data consists of sentences with multi-level slots.
    """

    def __init__(self, config: Config, logger: Logger, encoder: Optional[Encoder] = None,
                 cache_dir: Optional[Union[os.PathLike, str]] = './cache'):
        super(Candidate, self).__init__(config, logger, encoder, cache_dir)
        self.instance_count = 0
        self.process_num = 0
        self.refer_num, self.beam_size = config.extractor.ref_num, config.extractor.beam_size
        self.length_range = [config.extractor.min_length,
                             config.extractor.max_length]
        self.forbid_slots = get_forbid_slots(self.encoder)

    @spawn_multi_processor
    def worker(self, proc_id: int, worker_num: int, data_num: int) -> None:
        """
        Exploit multithreading to process the corpus and search for candidate patterns.
        """
        # Prepare
        misc.set_seed(self.seed)
        device = torch.device('cpu')
        if self.allow_cuda:
            start, end, device = mp_dynamic_device_data(data_num, proc_id, worker_num, self.gpu_indices, self.num_per_gpu, self.gpu_cpu_ratio)
        else:
            start, end = mp_allocate_data(data_num, proc_id, worker_num)

        torch.cuda.set_device(device)
        self.generate_candidates(proc_id, start, end, device)

    def generate_candidates(self, proc_id: int, start: int, end: int, device: torch.device) -> None:
        association = LRUCache()
        if os.path.exists("{}/candidate-tmp-".format(self.cache_dir) + str(proc_id) + ".pt"):
            os.remove("{}/candidate-tmp-".format(self.cache_dir) +
                      str(proc_id) + ".pt")
            self.logger.warning('[WARNING] Detect [%s] has been stored in cache dir, automatically Remove.' % (
                "{}/candidate-tmp-".format(self.cache_dir) + str(proc_id) + ".pt"))
        if os.path.exists("{}/candidate-tmp-".format(self.cache_dir) + str(proc_id) + "-counter.txt"):
            os.remove("{}/candidate-tmp-".format(self.cache_dir) +
                      str(proc_id) + "-counter.txt")
        candidate_writer = open(
            "{}/candidate-tmp-".format(self.cache_dir) + str(proc_id) + ".pt", "ab")
        reader = FileReader(convert_dataset_suffix(self.dataset_path))
        # Prepare Association
        asso_handler = Association(
            self.config, self.logger, device, self.encoder)
        # Processing
        reserved_part = None
        for index in tqdm(range(start, end), desc='Processing with proc {}'.format(proc_id), position=proc_id):
            candidates = []
            try:
                current_batch = self.get_item(reader, index)
                sentences, reserved_part = patch_batch_to_sentences(
                    current_batch, reserved_part)
                for sentence in sentences:
                    candidate, association = self.candidate_search(
                        sentence, association, asso_handler)
                    candidates.extend(candidate)
            except Exception as e:
                self.logger.error(
                    "proc {} error occurred in line - {}: {}".format(proc_id, index, e))
                traceback.print_exc()
                continue
            for cand in candidates:
                pickle.dump(cand, candidate_writer)
                self.process_num += 1
            # self.candidate_visualize(candidates) # Keep this feature only during the development stage.
        # Accomplish
        reader.close()
        candidate_writer.close()
        candidate_counter_writer = open(
            "{}/candidate-tmp-".format(self.cache_dir) + str(proc_id) + "-counter.txt", "w")
        candidate_counter_writer.write(str(self.process_num) + '\n')
        candidate_counter_writer.close()

    def candidate_search(self, sentence: list, association: LRUCache, asso_handler: Association) -> Tuple[list, dict]:
        candidates = []
        sentence, ww_masks = sentence
        ww_masks, _ = create_learner_index(sentence, [], ww_masks)
        if len(ww_masks) < self.length_range[0]:
            return candidates, association
        for index in range(len(ww_masks) - self.length_range[0]):
            if self.mp_mode == 'high-precision':
                beam_search = self.high_precision_search(
                    association, asso_handler, sentence, ww_masks, index)
            elif self.mp_mode == 'high-recall':
                beam_search = self.high_recall_search(
                    association, asso_handler, sentence, ww_masks, index)
            else:  # Trade-off
                beam_search = self.trade_off_search(
                    association, asso_handler, sentence, ww_masks, index)
            association = beam_search.association_cache
            pruned_candidates = CandidatePruner.prune(beam_search.candidates)
            candidates.extend(pruned_candidates)
        return candidates, association

    def rpt_debug(self, dataset_path: Optional[Union[str, os.PathLike]] = None,
                  model_path: Optional[Union[str, os.PathLike]] = None, factor: Optional[int] = 10,
                  seed: Optional[int] = None) -> None:
        rpt_debug_kwargs = deepcopy(self.config.extractor.rpt_debug)
        if seed is not None:
            misc.set_seed(seed)
        if rpt_debug_kwargs is None:
            err_msg = "To enable debugging mode, please set parameter `rpt_debug` / `rptDebug`."
            if self.logger is not None:
                self.logger.error(err_msg)
            else:
                print(err_msg)
            return None
        fit_num = rpt_debug_kwargs.pop("fit_num", 10)
        # Acquire examples
        collect_sentences = []
        reader = FileReader(convert_dataset_suffix(
            self.dataset_path if dataset_path is None else dataset_path))
        reserved_part = None
        for index in range(reader.n):
            try:
                if len(collect_sentences) > fit_num * factor:
                    break
                current_batch = self.get_item(reader, index)
                sentences, reserved_part = patch_batch_to_sentences(
                    current_batch, reserved_part)
                for sentence in sentences:
                    collect_sentences.append(sentence)
            except Exception as e:
                self.logger.error(
                    "Error occurred in line - {}: {}".format(index, e))
                traceback.print_exc()
                continue
        reader.close()
        collect_sentences = list(filter(lambda x: len(
            x[0]) >= self.length_range[1], collect_sentences))
        max_length = min(fit_num, len(collect_sentences))
        sentences = random.choices(collect_sentences, k=max_length)
        if model_path is None:
            asso_handler = Association(
                self.config, self.logger, torch.device("cpu"), self.encoder)
        else:
            asso_handler = Association(self.config, self.logger, torch.device("cpu"), self.encoder,
                                       model_path=model_path)
        rpt_hyper_debug(sentences, self.length_range, asso_handler, self.logger, **{**rpt_debug_kwargs,
                                                                                    **{"beam_size": self.beam_size,
                                                                                       "encoder": self.encoder}})

    def high_recall_search(self, association: LRUCache, asso_handler: Association, sentence: list, ww_masks: list,
                           index: int) -> HighRecallSearch:
        beam_search = HighRecallSearch(self.config, association, asso_handler, self.forbid_slots, self.length_range,
                                       self.ava_levels, seed=self.seed)
        for level in self.ava_levels:
            nslots = compose_slots(
                sentence, ww_masks[index], self.ava_levels, level)
            deter_slot = nslots[0]
            if deter_slot in self.forbid_slots:
                continue
            beam_search.recursive_search(nslots if len(nslots) < 2 else [tuple(nslots)], 1, sentence, ww_masks, index,
                                         len(ww_masks))
        return beam_search

    def high_precision_search(self, association: LRUCache, asso_handler: Association, sentence: list, ww_masks: list,
                              index: int) -> HighPrecisionSearch:
        beam_search = HighPrecisionSearch(self.config, association, asso_handler, self.forbid_slots, self.length_range,
                                          self.ava_levels, seed=self.seed)
        beam_search.recursive_search(
            [], 0, sentence, ww_masks, index - 1, len(ww_masks), score=beam_search.init_score)
        return beam_search

    def trade_off_search(self, association: LRUCache, asso_handler: Association, sentence: list, ww_masks: list,
                         index: int) -> TradeOffSearch:
        beam_search = TradeOffSearch(self.config, association, asso_handler, self.forbid_slots, self.length_range,
                                     self.ava_levels, seed=self.seed)
        beam_search.recursive_search([], 0, sentence, ww_masks, index - 1, len(ww_masks), score=beam_search.init_score,
                                     beam_size=len(self.ava_levels))
        return beam_search

    def candidate_visualize(self, candidates: list):
        # Prototype verification
        for index, candidate in enumerate(candidates):
            candidate_token = '--'.join(
                self.encoder.convert_ids_to_tokens(candidate))
            print('[{}]: {}'.format(index+1, candidate_token))
        print('')
