import os
import abc
from typing import List, Optional, Dict
from logging import Logger
from copy import deepcopy

import numpy as np
import numba
import torch
from multiprocessing.managers import BaseManager, BaseProxy

from ..config.config import Config
from ..utils.predefine import LEARNER_SUFFIX, MP_LEARNER_UNPACK_FILE_NAME_FFR_TEMPLATE, FFR_FILE_SUFFIX, SYMSEM_DISTANCS_FILE_NAME
from ..utils.file_loader import convert_dataset_suffix, determine_dataset_name
from ..utils.utils_learner import compute_vocab_cost, parallel_unpack_corpus, build_mdlgraph, read_corpus_for_fsk, build_mdlgraph_hybrid
from ..utils.utils_learner import DEFAULT_SYNSEM_CHUNK_SIZE, compute_contrastive_loss, acquire_candidate_hidden, generate_sem_clusters
from ..utils.utils_learner import CUML_ACCELERATOR, calculate_chunk_indices, compute_syntactic_dist, dict_dummy_writer, generate_soft_labels
from sklearn.metrics.pairwise import cosine_similarity

class BaseMetric(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, config: Config, cache_dir = './cache', **kwargs):
        self.config = config
        self.cache_dir = cache_dir
        self.hybrid = kwargs.pop("hybrid", False)
        self.logger = kwargs.pop("logger", None)
        self.parser = kwargs.pop("parser", None)
        self.do_proprocess = kwargs.pop("preprocess", False)
        self.external_kwargs = kwargs

    @abc.abstractmethod
    def compute_metrics(self, candidate_states: List) -> dict:
        pass

    def preprocess(self, states: List[bool], proc_id=-1,  **kwargs):
        if not self.do_proprocess: return
        self._preprocess(states, proc_id, **kwargs)

    @abc.abstractmethod
    def _preprocess(self, states: List[bool], proc_id=-1, **kwargs): 
        pass


class MDL_Metric(BaseMetric):
    def __init__(self, config: Config, cache_dir = './cache', **kwargs):
        # Experimental Feature
        super(MDL_Metric, self).__init__(config, cache_dir, **kwargs)
        vocab_range = self.parser.vocab_range
        self.vocab_cost = compute_vocab_cost(vocab_range)

    def compute_metrics(self, candidate_states: List) -> dict:
        candidate_states = np.array(candidate_states, dtype=np.int32)

        # Compute construction cost
        selected_candidates_idx = np.array(list(self.cxs_candidates.keys()))[candidate_states.astype(np.bool_)]
        n_selected = sum(candidate_states)
        cost = -sum(self.candidates_cost[idx] for idx in selected_candidates_idx)
        cost = cost / n_selected

        # Compute coverage and overlap
        delta=self.mdl_graph.diff_update(candidate_states)
        coverage, overlap = self.mdl_graph.avg_metrics

        return {
            'cost':cost,
            'coverage': coverage,
            'overlap': overlap,
        }
        
    def _preprocess(self, states: List[bool], proc_id=-1, **kwargs):
        ex_kwargs = deepcopy(self.external_kwargs)
        dataset_path = ex_kwargs.pop("datasetPath", None)
        batch_size = ex_kwargs.pop("batchSize", 100)
        worker_num = ex_kwargs.pop("workerNum", 8)
        
        if dataset_path is None:
            dataset_path = convert_dataset_suffix(
                determine_dataset_name(self.config, self.config.lm.dataset_path, self.logger, suffix=LEARNER_SUFFIX),
                self.logger)
        if not os.path.exists(dataset_path):
            err_info = f"The dataset file `{dataset_path}` cannot be found, please check."
            if self.logger is not None: self.logger.error(err_info)
            raise Exception(err_info)
        self.dataset_path = dataset_path
        if not self.hybrid:
            # all the data in the dataset in one mdlgraph
            unpacked_files = parallel_unpack_corpus(dataset_path, worker_num, cache_dir=self.cache_dir,
                                                logger=self.logger, check_data=True)
            # Build MDLGraph
            self.mdl_graph = build_mdlgraph(self.parser, unpacked_files, np.array(states, dtype=np.int16), 500, worker_num, self.logger,cache_dir=self.cache_dir)
            # Preprocess fsk score
            token_size = self.parser.encoder.token_size
            lex_size = self.parser.encoder.lex_size
            vocab_fsk = np.zeros((token_size))
            vocab_fsk[:lex_size] = 1
            corpus = read_corpus_for_fsk(dataset_path)
            vocab_map = np.zeros((token_size-lex_size, lex_size), dtype=np.int8)
            fsk = compute_fsk(corpus, vocab_map, vocab_fsk, lex_size)
            self.cxs_candidates = {**self.parser.cxs_decoder, **self.parser.added_cxs_decoder}
            self.candidates_cost = [np.sum(np.log(pow(fsk[slot]+1,-1)) for slot in candidate) for candidate in self.cxs_candidates.values()]
        else:
            # each worker process a part of the data in the dataset, and they are in different mdlgraph
            if proc_id == -1:
                unpacked_files_path = parallel_unpack_corpus(dataset_path, worker_num, cache_dir=self.cache_dir,
                                                    logger=self.logger, check_data=True)
                token_size = self.parser.encoder.token_size
                lex_size = self.parser.encoder.lex_size
                vocab_fsk = np.zeros((token_size))
                vocab_fsk[:lex_size] = 1
                corpus = read_corpus_for_fsk(dataset_path)
                vocab_map = np.zeros((token_size-lex_size, lex_size), dtype=np.int8)
                fsk = compute_fsk(corpus, vocab_map, vocab_fsk, lex_size)
                self.cxs_candidates = {**self.parser.cxs_decoder, **self.parser.added_cxs_decoder}
                self.candidates_cost = [np.sum(np.log(pow(fsk[slot]+1,-1)) for slot in candidate) for candidate in self.cxs_candidates.values()]
                torch.save(self.candidates_cost, os.path.join(self.cache_dir, "candidates_cost.pt"))
            else:
                parser = kwargs['parser']
                unpacked_files_path = os.path.join(self.cache_dir, MP_LEARNER_UNPACK_FILE_NAME_FFR_TEMPLATE.format(proc_id))
                states = np.array(states, dtype=np.int16)
                self.mdl_graph = build_mdlgraph_hybrid(parser, [unpacked_files_path], states, 500, proc_id, logger=self.logger, cache_dir=self.cache_dir)
                # Preprocess fsk score
                self.cxs_candidates = {**self.parser.cxs_decoder, **self.parser.added_cxs_decoder}
                self.candidates_cost = torch.load(os.path.join(self.cache_dir, "candidates_cost.pt"))


class SynSem_Metric(BaseMetric):
    def compute_metrics(self, candidate_states: List) -> dict:
        kwargs = deepcopy(self.external_kwargs)
        need_cluster = kwargs.pop("needCluster", False)
        worker_num = kwargs.pop("workerNum", 1)
        # kwargs['seed'] = self.config.experiment.seed
        selected_candidates = np.array(list(self.cxs_candidates.keys()))[np.array(candidate_states)]
        dist_info = self.syntactic_dists if need_cluster else self.soft_labels
        cont_loss = compute_contrastive_loss(selected_candidates, self.cxs_hidden_states, dist_info,
                                             self.similarity, self.hmap_states, self.back_hmap_states, self.logger,
                                             worker_num, self.cache_dir, **kwargs)
        return {
            'cont': cont_loss
        }

    def _preprocess(self, states: List[bool], proc_id=-1, **kwargs):
        print("Preprocessing for SynSem Metric ...")
        kwargs = deepcopy(self.external_kwargs)
        worker_num = kwargs.pop("workerNum", 1)
        need_cluster = kwargs.pop("needCluster", False)
        use_cuda = kwargs.pop("useCuda", True) if torch.cuda.is_available() else False
        chunk_size = kwargs.pop("chunkSize", DEFAULT_SYNSEM_CHUNK_SIZE)
        info_msg = "Starting %d workers to preprocess data for SynSem Metric ... " % worker_num
        if self.logger is not None: self.logger.info(info_msg)
        else: print(info_msg)
        # Generate hidden states of construction candidates.
        self.cxs_candidates = {**self.parser.cxs_decoder, **self.parser.added_cxs_decoder}

        cxs_hidden_states = acquire_candidate_hidden(self.config, self.parser, worker_num=worker_num,
                                                     **{**{"logger": self.logger}, **kwargs})
        if worker_num > 1: cxs_hidden_states = torch.cat(cxs_hidden_states)
        self.cxs_hidden_states = cxs_hidden_states
        if need_cluster:
            # Dimensionality reduction and clustering for hidden states.
            hmap_states, init_clusters = generate_sem_clusters(cxs_hidden_states, need_umap=True, n_jobs=worker_num,
                                                               random_state=self.config.experiment.seed, logger=self.logger)
            self.hmap_states, self.init_clusters = hmap_states, init_clusters
            # Normal hmap -> np.ndarry
            if CUML_ACCELERATOR: self.back_hmap_states = np.array(self.hmap_states.tolist())
            else: self.back_hmap_states = self.hmap_states
            self.similarity = None
        else:
            self.hmap_states = None
            self.back_hmap_states = None
            similarity = torch.from_numpy(cosine_similarity(cxs_hidden_states))
            chunk_indices = calculate_chunk_indices(similarity.shape[0], chunk_size)
            if chunk_size > 1 and use_cuda:
                if chunk_size > torch.cuda.device_count():
                    err_msg = "`chunkSize` cannot be greater than gpu_nums={}".format(torch.cuda.device_count())
                    if self.logger is not None:
                        self.logger.error(err_msg)
                    raise ValueError(err_msg)
                self.similarity = [similarity[chunk_indices[cid]:chunk_indices[cid+1]].to("cuda:{}".format(cid))
                                   if cid < chunk_size - 1 else similarity[chunk_indices[cid]:].to("cuda:{}".format(cid))
                                   for cid in range(chunk_size)]
            else:
                if use_cuda:
                    self.similarity = similarity.cuda()
                else:
                    self.similarity = similarity

        # Syntactic relations computation.
        syn_dist_worker_num = kwargs.pop("distWorker", 1)
        ignore = kwargs.pop("ignoreInput", False)
        compute_flag = True
        if os.path.exists(os.path.join(self.cache_dir, SYMSEM_DISTANCS_FILE_NAME + FFR_FILE_SUFFIX)) and not ignore:
            # https://stackoverflow.com/questions/63893634/how-to-use-multiprocessing-with-input-function-and-avoid-eoferror-eof-when-r
            import sys
            sys.stdin = open(0)
            hkey = input("Detected cached syntax distance file, do you want to use it directly? (y/n):")
            if hkey in ['y', 'Y']: compute_flag = False

        if compute_flag:
            syntactic_dists = compute_syntactic_dist(self.parser, logger=self.logger, worker_num=syn_dist_worker_num,
                                                     cache_dir=self.cache_dir, **kwargs)
            dict_dummy_writer(os.path.join(self.cache_dir, SYMSEM_DISTANCS_FILE_NAME +FFR_FILE_SUFFIX),
                              len(self.cxs_candidates), syntactic_dists)
            info_msg = f"The syntax distance file is cached " \
                       f"at {os.path.join(self.cache_dir, SYMSEM_DISTANCS_FILE_NAME + FFR_FILE_SUFFIX)}"
            self.syntactic_dists = os.path.join(self.cache_dir, SYMSEM_DISTANCS_FILE_NAME + FFR_FILE_SUFFIX)
            if self.logger is not None: self.logger.info(info_msg)
            else: print(info_msg)
        else:
            self.syntactic_dists = os.path.join(self.cache_dir, SYMSEM_DISTANCS_FILE_NAME + FFR_FILE_SUFFIX)
        if not need_cluster:
            soft_labels = generate_soft_labels(self.syntactic_dists, self.cxs_hidden_states.shape[0])
            chunk_indices = calculate_chunk_indices(soft_labels.shape[0], chunk_size)
            if chunk_size > 1 and use_cuda:
                self.soft_labels = [soft_labels[chunk_indices[cid]:chunk_indices[cid + 1]].to("cuda:{}".format(cid))
                                   if cid < chunk_size - 1 else soft_labels[chunk_indices[cid]:].to("cuda:{}".format(cid))
                                   for cid in range(chunk_size)]
            else:
                if use_cuda:
                    self.soft_labels = soft_labels.cuda()
                else:
                    self.soft_labels = soft_labels
        else:
            self.soft_labels = None
        info_msg = "The preprocessing process for SynSem metric has been completed."
        if self.logger is not None: self.logger.info(info_msg)
        else: print(info_msg)


class Metric_Proxy(BaseProxy):
    _exposed_ = ('compute_metrics',)

    def compute_metrics(self, candidate_states: List):
        self._callmethod('compute_metrics', (candidate_states,))


class MetricManager(BaseManager):
    pass


def initialize_proxy_class(cls, args, kwargs):
    met_obj = cls(*args, **kwargs)
    return met_obj


default_metrics = {
    "mdl": MDL_Metric,
    "synsem": SynSem_Metric
}


def register_metrics(logger: Optional[Logger] = None, **metric_group):
    for metric_name, metric_handler in metric_group.items():
        if metric_name in default_metrics:
            warn_msg = f"The name of the metric handler to be registered, `{metric_name}`, conflicts with a " \
                       f"built-in method and will be ignored."
            if logger is not None: logger.warning(warn_msg)
            else: print(warn_msg)
            continue
        if not isinstance(metric_handler, BaseMetric):
            warn_msg = f"The desired registration method `{metric_name}` does not seem to inherit from the abstract " \
                       f"base class `BaseMetric` and will be ignored. Please check the documentation."
            if logger is not None: logger.warning(warn_msg)
            else: print(warn_msg)
            continue
        default_metrics[metric_name] = metric_handler


@numba.jit(nopython=True, parallel=True)
def compute_fsk(corpus, vocab_map, vocab_fsk, lex_size):
    for s_idx in numba.prange(len(corpus)):
        sentence = corpus[s_idx]
        for i_idx in numba.prange(len(sentence)):
            items = sentence[i_idx]
            for i in range(1, len(items)):
                vocab_map[items[i]-lex_size][items[0]] = 1
    for i in numba.prange(len(vocab_map)):
        vocab_fsk[i+lex_size] = np.sum(vocab_map[i])
    return vocab_fsk
