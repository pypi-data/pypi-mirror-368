import os
import time
import random
from logging import Logger
from typing import Union, Optional
from tqdm import tqdm
from math import ceil
import scipy.io as sio
import traceback
import pickle

from ..utils.file_loader import merge_dataset, create_cache_dir, count_lines, get_name_wosuffix, convert_ffrecord, find_split_line, shuffle_coprpus
from ..utils.file_loader import merge_shuffled_corpus, mp_allocate_data
from ..utils.predefine import SHUFFLED_SUFFIX, LEARNER_SUFFIX, BACKGROUND_SUFFIX, CANDIDATE_SUFFIX
from ..utils.multi_processor import MultiProcessor as multi_processor
from ..utils.utils_lm import par_wwindex_seq
from ..utils import misc


WATCH_DOG_THRESH = 60 * 60  # 60 minutes


class BaseDataset(object):
    """
    Base class for creating datasets. It contains methods for building, shuffling, and splitting datasets, as well as
    utilities for managing dataset-related processes.
    """
    def __init__(self, config, logger: Logger, encoder, cache_dir: os.PathLike = './cache'):
        """
        Initializes the BaseDataset object.
        """
        self.logger = logger
        self.worker_num = config.encoder.worker_num
        self.corpus_path = config.experiment.corpus_path
        self.dataset_path = config.lm.dataset_path
        self.seq_length = config.lm.seq_length
        self.seed = config.experiment.seed
        self.do_lower_case = config.lm.do_lower_case
        # Copy Encoder
        self.encoder = encoder
        # Create cache dir
        self.cache_dir = create_cache_dir(cache_dir, config.experiment.name)
        # Whether to split & shuffle Dataset
        self.background_ratio = config.encoder.back_ratio
        self.search_ratio = config.encoder.search_ratio
        self.shuffle_flag = config.encoder.corpus_shuffle
        # Check ratio
        self.check_ratio()
        if self.shuffle_flag:
            self.shuffle = True
            self.corpus_path = self.shuffle_corpus(self.cache_dir)
        else: self.shuffle = False
        if self.background_ratio >= 0:
            self.split_line_back = self.obtain_split_line(self.background_ratio)
        else: self.split_line_back = None
        if self.search_ratio >= 0:
            self.split_line_candidate = self.obtain_split_line(self.background_ratio + self.search_ratio)
        else:
            self.split_line_candidate = None

    def build_and_save(self) -> None:
        """
        Builds the dataset from the specified corpus and saves it to disk. The process is managed by multiple worker
        processes, each handling a portion of the data. Depending on the configuration, the corpus may be split into
        background and candidate datasets, and optionally shuffled.
        """
        if hasattr(self, 'lines_num'): lines_num = self.lines_num
        else: lines_num = count_lines(self.corpus_path)
        if self.split_line_back is not None:
            self.logger.info("The settings indicate the need to split the corpus, so it will be processed in two stages.")
            self.logger.info(">> Stage 1 : Process background corpus")
            background_dataset_path = get_name_wosuffix(self.dataset_path, self.logger) + '{}.pt'.format(BACKGROUND_SUFFIX)
            self.logger.info("Starting %d workers for building background datasets ... " % self.worker_num)
            self.worker(self, self.split_line_back, 0, worker_num=self.worker_num)
            # Merge background datasets.
            background_dataset_num = merge_dataset(background_dataset_path, self.worker_num, self.cache_dir)
            # Convert background 2 FFRecord
            convert_ffrecord(background_dataset_path, background_dataset_num, self.logger)
            self.logger.info(">> Stage 2 : Process candidate corpus")
            candidate_dataset_path = get_name_wosuffix(self.dataset_path, self.logger) + '{}.pt'.format(CANDIDATE_SUFFIX)
            self.logger.info("Starting %d workers for building candidate datasets ... " % self.worker_num)
            if self.split_line_candidate is not None:
                self.worker(self, self.split_line_candidate - self.split_line_back, self.split_line_back + 1,
                            worker_num=self.worker_num)
            else:
                self.worker(self, lines_num - self.split_line_back - 1, self.split_line_back + 1,
                            worker_num=self.worker_num)
            # Merge candidate datasets.
            candidate_dataset_num = merge_dataset(candidate_dataset_path, self.worker_num, self.cache_dir)
            # Convert candidate 2 FFRecord
            convert_ffrecord(candidate_dataset_path, candidate_dataset_num, self.logger)
            if self.split_line_candidate is not None:
                self.logger.info(">> Stage 3 : Process learner corpus")
                learner_dataset_path = get_name_wosuffix(self.dataset_path, self.logger) + '{}.pt'.format(LEARNER_SUFFIX)
                self.logger.info("Starting %d workers for building leaner datasets ... " % self.worker_num)
                self.worker(self, lines_num - self.split_line_candidate - 1, self.split_line_candidate + 1,
                            worker_num=self.worker_num)
                # Merge learner datasets.
                learner_dataset_num = merge_dataset(learner_dataset_path, self.worker_num, self.cache_dir)
                # Convert learner 2 FFRecord
                convert_ffrecord(learner_dataset_path, learner_dataset_num, self.logger)
            if self.shuffle_flag: os.remove(self.corpus_path)
        else:
            self.logger.info("Starting %d workers for building datasets ... " % self.worker_num)
            self.worker(self, lines_num, 0, worker_num=self.worker_num)
            # Merge datasets.
            dataset_num = merge_dataset(self.dataset_path, self.worker_num)
            # Convert 2 FFRecord
            convert_ffrecord(self.dataset_path, dataset_num, self.logger)

    @multi_processor
    def worker(self, proc_id: int, worker_num: int, lines_num: int, base_start: int) -> None:
        """
        A worker function to be run in a separate process. It processes a subset of the corpus data.
        """
        raise NotImplementedError

    def obtain_split_line(self, corpus_ratio: float) -> int:
        """
        A worker function to be run in a separate process. It processes a subset of the corpus data.
        """
        if hasattr(self, 'lines_num'): lines_num = self.lines_num
        else: lines_num = count_lines(self.corpus_path)
        if corpus_ratio <= 0. or corpus_ratio >= 1.:
            self.logger.error("The `back_ratio` seems to be set incorrectly. Please check.")
        back_lines_num = ceil(lines_num * corpus_ratio)
        split_num = find_split_line(self.corpus_path, back_lines_num, lines_num)
        if split_num is None:
            self.logger.error("Due to the inability to handle the aforementioned errors, "
                              "the program terminates. Please check the corpus data file.")
            raise Exception("Due to the inability to handle the aforementioned errors, "
                            "the program terminates. Please check the corpus data file.")
        else: return split_num

    def check_ratio(self):
        base_ratio = 0.
        if self.background_ratio >= 0.: base_ratio += self.background_ratio
        if self.search_ratio >= 0.: base_ratio += self.search_ratio
        if base_ratio > 1.:
            err_msg = "The sum of `backRatio` and `searchRatio` cannot be greater than `1`, please check."
            if self.logger is not None:
                self.logger.error(err_msg)
            raise ValueError(err_msg)

    def shuffle_corpus(self, predix_cache: Optional[Union[os.PathLike, str]]= './cache/') -> str:
        """
        Shuffles the corpus and saves the shuffled version to disk.
        """
        lines_num = count_lines(self.corpus_path)
        self.lines_num = lines_num
        corpus_base_name = get_name_wosuffix(self.corpus_path, self.logger)
        shuffled_path = corpus_base_name + '{}.pt'.format(SHUFFLED_SUFFIX)
        self.logger.info("Starting %d workers for shuffling corpus ... " % self.worker_num)
        # Shuffle datasets.
        shuffle_coprpus(self.corpus_path, lines_num, predix_cache, self.seed, worker_num=self.worker_num)

        # Merge corpus
        merge_shuffled_corpus(self.worker_num, shuffled_path, predix_cache, self.seed)
        self.logger.info("The shuffled corpus is saved at %s" % shuffled_path)
        self.lines_num = count_lines(shuffled_path)
        return shuffled_path


class Dataset(BaseDataset):
    """
    Construct dataset for GPT series model from the given corpus.
    Each document consists of multiple sentences,
    and each sentence occupies a single line.
    Documents in corpus must be separated by empty lines.
    """
    def __init__(self, config, logger, encoder, cache_dir: Union[str, os.PathLike] = './cache'):
        """
        A class to represent the dataset for GPT series model.
        """
        super(Dataset, self).__init__(config, logger, encoder, cache_dir)
        self.instance_count = 0
        self.process_num = 0
        self.short_seq_prob = config.lm.short_seq_prob

    @multi_processor
    def worker(self, proc_id: int, worker_num: int, lines_num: int, base_start: int) -> None:
        """
        Worker function to process parts of the dataset in parallel.
        """
        # Prepare
        misc.set_seed(self.seed)
        self.process_num = 0
        document = []
        pos = 0
        start, end = mp_allocate_data(lines_num, proc_id, worker_num)
        if os.path.exists("{}/dataset-tmp-".format(self.cache_dir) + str(proc_id) + ".pt"):
            os.remove("{}/dataset-tmp-".format(self.cache_dir) + str(proc_id) + ".pt")
            self.logger.warning('[WARNING] Detect [%s] has been stored in cache dir, automatically Remove.' % ("{}/dataset-tmp-".format(self.cache_dir) + str(proc_id) + ".pt"))
        if os.path.exists("{}/dataset-tmp-".format(self.cache_dir) + str(proc_id) + "-counter.txt"):
            os.remove("{}/dataset-tmp-".format(self.cache_dir) + str(proc_id) + "-counter.txt")
        dataset_writer = open("{}/dataset-tmp-".format(self.cache_dir) + str(proc_id) + ".pt", "ab")
        with open(self.corpus_path, mode="r", encoding="utf-8") as f:
            while pos < base_start + start:
                f.readline()
                pos += 1
            for _ in tqdm(range(base_start + start, base_start + end),  desc='Processing with proc {}'.format(proc_id), position=proc_id):
                line = f.readline()
                if not line.strip():
                    # Build instances from documents.
                    try: instances = self.build_instances(document, proc_id)
                    except:
                        self.logger.error("proc {} error occurred in line - {}: {}".format(proc_id, _, traceback.print_exc()))
                        continue
                    document = []
                    # Save instances.
                    for instance in instances:
                        pickle.dump(instance, dataset_writer)
                        self.process_num += 1
                    continue

                if len(line.strip()) > 0:
                    document.append(line.strip())
            if len(document) > 0:
                try: instances = self.build_instances(document, proc_id)
                except:
                    self.logger.error("proc {} error occurred in line - {}: {}".format(proc_id, _, traceback.print_exc()))
                    instances = []
                for instance in instances:
                    pickle.dump(instance, dataset_writer)
                    self.process_num += 1
        dataset_writer.close()
        dataset_counter_writer = open("{}/dataset-tmp-".format(self.cache_dir) + str(proc_id) + "-counter.txt", "w")
        dataset_counter_writer.write(str(self.process_num) + '\n')
        dataset_counter_writer.close()

    def build_instances(self, document: list, proc_ids: int) -> list:
        """
        Build instances from a given document.
        """
        max_num_tokens = self.seq_length - 2
        target_seq_length = max_num_tokens
        if random.random() < self.short_seq_prob:
            target_seq_length = random.randint(4, max_num_tokens)
        instances = []
        chunk_buffer = []
        current_chunk = []
        elements, segs, ww_mask = None, [], None
        current_length = 0
        i = 0
        watchdog = time.time()

        while i < len(document):
            if time.time() - watchdog > WATCH_DOG_THRESH:
                # Exception log (watch dog)
                time_id = time.time()
                with open('{}/watchdog-error-proc-{}-log-{}.txt'.format(self.cache_dir, proc_ids, time_id), 'w', encoding='utf-8') as err_fp:
                    err_fp.write('Proc: {}, err_line: {}, cur_chunk: {}, err_duration: {}s\n'.format(proc_ids, len(document), len(chunk_buffer), time.time() - watchdog))
                sio.savemat('{}/watchdog-error-proc-{}-data-{}.mat'.format(self.cache_dir, proc_ids, time_id), {'err_data': document})
                break
            segment = document[i]
            if not elements:
                elements = self.encoder.encode(segment, need_mask=True)
                if isinstance(elements, tuple): elements, ww_mask = elements
                else: ww_mask = None
                if elements is None:
                    self.logger.warning("Proc: {}, cannot encode sentence `{}`".format(proc_ids, segment))
                    i += 1
                    continue
            if current_length + len(elements) >= target_seq_length:
                complement_length = target_seq_length - current_length
                if complement_length > 0 and complement_length != len(elements):
                    element_comp_ids = elements[:complement_length]
                    elements = elements[complement_length:]
                    if ww_mask is not None:
                        wwmask_comp, ww_mask = par_wwindex_seq(ww_mask, complement_length)
                        current_chunk.append((element_comp_ids, wwmask_comp))
                    else: current_chunk.append(element_comp_ids)
                    current_length += len(element_comp_ids)
                else:
                    if ww_mask is not None: current_chunk.append((elements, ww_mask))
                    else: current_chunk.append(elements)
                    segs.append(current_length + len(elements))
                    i += 1
                    elements, ww_mask = None, None

                chunk_buffer.append([current_chunk, segs])
                current_chunk, segs = [], []
                current_length = 0
                target_seq_length = max_num_tokens
                if random.random() < self.short_seq_prob:
                    target_seq_length = random.randint(4, max_num_tokens)
                continue

            if ww_mask is not None: current_chunk.append((elements, ww_mask))
            else: current_chunk.append(elements)
            current_length += len(elements)
            segs.append(current_length)
            elements, ww_mask = None, None
            i += 1
        if current_chunk: chunk_buffer.append([current_chunk, segs])

        for chunk in chunk_buffer:
            chunk_content, split_ids = chunk
            if isinstance(chunk_content[0], list): src_ids, ww_mask = chunk_content[0], None
            else: src_ids, ww_mask = chunk_content[0]
            for idx in range(1, len(chunk_content)):
                if isinstance(chunk_content[idx], list): cur_chunk_src, cur_chunk_wwmask = chunk_content[idx], None
                else: cur_chunk_src, cur_chunk_wwmask = chunk_content[idx]
                curlen = len(src_ids)
                if cur_chunk_wwmask is not None: ww_mask += [[ww[0] + curlen, ww[1] + curlen] for ww in cur_chunk_wwmask]
                src_ids += cur_chunk_src
            result = []
            for element in src_ids:
                result.append(tuple([self.encoder.convert_ids_to_tokens(ele) for ele in element]))
            if ww_mask is not None: instances.append([src_ids, split_ids, ww_mask])
            else: instances.append([src_ids, split_ids])
        return instances
