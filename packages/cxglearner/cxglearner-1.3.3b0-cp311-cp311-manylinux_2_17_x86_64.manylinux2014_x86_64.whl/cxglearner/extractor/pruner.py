import os
import abc
import six
from math import ceil
from typing import Union, Optional
from functools import reduce
import operator

import cytoolz as cy
import torch
import numpy as np

from ..utils.file_loader import get_pruner_prefix, get_name_wosuffix, get_data_nums, write_ffrecord_file, read_ffrecord_file
from ..utils.predefine import FREQUENCY_PRUNER_SUFFIX, FFR_FILE_SUFFIX, VERTICAL_PRUNER_SUFFIX, HORIZONTAL_PRUNER_SUFFIX
from ..utils.utils_extractor import mp_candidate_counter, vis_frequency_figure, generate_slots_graph, clustering_vertical_candidates
from ..utils.utils_extractor import prune_vertical_coarse, prune_vertical_fine, vh_prune_debug, clustering_horizontal_candidates, prune_horizontal


class CandidatePruner(object):
    @staticmethod
    def prune(candidates: Union[dict, list], prune_num: Optional[int] = 1) -> list:
        pruned_candidates, INNER_FLAG = [], False
        if isinstance(candidates, list):
            INNER_FLAG = True
            candidates = {0: candidates}
        for depth in candidates:
            seq, probs = zip(*candidates[depth])
            if prune_num == 1:
                if len(seq) > 1:
                    index = np.argmax(np.array(probs))
                else:
                    index = 0
                if INNER_FLAG:
                    pruned_candidates.append([seq[index], probs[index]])
                else:
                    pruned_candidates.append(seq[index])
            else:
                pnum = min(prune_num, len(probs))
                _, index = torch.topk(torch.from_numpy(
                    np.array(probs, dtype=np.float32)), k=pnum)
                if INNER_FLAG:
                    pruned_candidates.extend(
                        [[seq[idx], probs[idx]] for idx in index])
                else:
                    pruned_candidates.extend([seq[idx] for idx in index])
        return pruned_candidates

    @staticmethod
    def prune_level_precision(batched_data: list, ava_level: dict, depth: int, minimum_length: int) -> bool:
        batch_len = len(batched_data)
        level_num = len(ava_level)
        if depth == minimum_length:
            refer_num = level_num ** depth
        else:
            refer_num = level_num
        if batch_len == refer_num:
            return True
        else:
            return False

    @staticmethod
    def prune_level_tradeoff(batched_data: list, ava_level: dict, depth: int, minimum_length: int) -> bool:
        batch_len = len(batched_data)
        level_num = len(ava_level)
        if depth == minimum_length:
            refer_num = level_num ** depth
        else:
            refer_num = level_num ** 2
        if batch_len == refer_num:
            return True
        else:
            return False


@six.add_metaclass(abc.ABCMeta)
class PrunerTemplate(object):
    @abc.abstractmethod
    def prune(self, data) -> Union[str, os.PathLike]:
        """
        an abstract method of pruner
        """


class FreqPruner(PrunerTemplate):
    @staticmethod
    def prune(candidate_path: Union[str, os.PathLike], **kwargs) -> Union[str, os.PathLike]:
        useless_args = ['encoder', 'config', 'cache_dir']
        for arg in useless_args:
            if arg in kwargs.keys():
                del kwargs[arg]
        logger = kwargs.pop("logger", None)
        hard_freq = kwargs.pop("hardFreq", None)
        soft_freq = kwargs.pop("softFreq", None)
        worker_num = kwargs.pop("workerNum", 1)
        debug_mode = kwargs.pop("debug", False)
        prune_file_path = get_pruner_prefix(get_name_wosuffix(candidate_path)) + FREQUENCY_PRUNER_SUFFIX + \
            FFR_FILE_SUFFIX
        if os.path.exists(prune_file_path):
            info_msg = f"The frequency pruning process may have been completed, obtain directly from `{prune_file_path}`."
            warn_msg = "If frequency pruning needs to be re-processed, please stop and manually clear the cache files."
            if logger is not None:
                logger.info(info_msg)
                logger.warning(warn_msg)
            else:
                print(info_msg + '\n' + warn_msg)
            return prune_file_path
        if hard_freq is None and soft_freq is None:
            err_msg = "The parameters `softFreq` and `hardFreq` cannot be both `None`. Please check."
            if logger is not None:
                logger.error(err_msg)
            raise ValueError(err_msg)
        if hard_freq is None:
            hard_freq = 0
        if soft_freq is None:
            soft_freq = 0
        if logger is not None:
            logger.info(">> Frequency Pruning")
        else:
            print(">> Frequency Pruning")
        if len(kwargs) > 0:
            if logger is not None:
                logger.warning(f"The following parameters: `{kwargs}` are not applicable "
                               f"for this pruner.")
            else:
                print(
                    f"The following parameters: `{kwargs}` are not applicable for this pruner.")
        if not os.path.exists(candidate_path):
            err_msg = f"The candidate file `{candidate_path}` seems not exists, please check."
            if logger is not None:
                logger.error(err_msg)
            raise Exception(err_msg)
        pre_total_num = get_data_nums(candidate_path, logger=logger)
        counter_dict = mp_candidate_counter(
            candidate_path, worker_num=worker_num)
        info_msg = "Loading complete, start reducing procedure."
        if logger is not None:
            logger.info(info_msg)
        else:
            print(info_msg)
        if isinstance(counter_dict, list):
            counter_dict = cy.merge_with(sum, counter_dict)
        counter_max, counter_min = max(counter_dict, key=counter_dict.get), min(
            counter_dict, key=counter_dict.get)
        counter_mean = sum(counter_dict.values()) / len(counter_dict)
        info_msg = "There are a total of `{}` candidates. The unique candidate has a total of `{}`, with the highest " \
                   "frequency being `{}`and the lowest frequency being `{}`.".format(
                       pre_total_num, len(counter_dict), counter_dict[counter_max], counter_dict[counter_min])
        if logger is not None:
            logger.info(info_msg)
        else:
            print(info_msg)
        if debug_mode:
            vis_frequency_figure(counter_dict)
        # Determine the pruned frequency threshold
        freq_threshold = max(hard_freq, ceil(counter_mean * soft_freq))
        pruned_candidates = list(cy.itemfilter(
            lambda x: x[1] > freq_threshold, counter_dict).items())
        info_msg = f"We apply `{freq_threshold}` as the frequency pruning threshold. After pruning, there are " \
                   f"`{len(pruned_candidates)}` remaining candidate constructions."
        if logger is not None:
            logger.info(info_msg)
        else:
            print(info_msg)
        write_ffrecord_file(prune_file_path, pruned_candidates, logger)
        return prune_file_path


class VerticalPruner(PrunerTemplate):
    @staticmethod
    def prune(candidate_path: Union[str, os.PathLike], **kwargs) -> Union[str, os.PathLike]:
        useless_args = []
        for arg in useless_args:
            if arg in kwargs.keys():
                del kwargs[arg]
        logger = kwargs.pop("logger", None)
        config = kwargs.pop("config", None)
        encoder = kwargs.pop("encoder", None)
        worker_num = kwargs.pop("workerNum", 1)
        comb_operator = kwargs.pop("operator", "intersection")
        debug = kwargs.pop("debug", None)
        cache_dir = kwargs.pop("cache_dir", './cache')
        # Combination operator
        if comb_operator not in ['intersection', 'union']:
            warn_msg = "The parameters `operator` seems incorrect, we will use `intersection` instead."
            if logger is not None:
                logger.warning(warn_msg)
            else:
                print(warn_msg)
            comb_operator = set.intersection
            comb_opstr = "intersection"
        else:
            comb_opstr = comb_operator
            if comb_operator == "intersection":
                comb_operator = set.intersection
            else:
                comb_operator = set.union
        # Prune mode
        fine_grained_mode = kwargs.pop("fineGrained", False)
        coarse_grained_mode = kwargs.pop("coarseGrained", False)
        if (isinstance(fine_grained_mode, bool) and not fine_grained_mode) and (isinstance(coarse_grained_mode, bool)
                                                                                and not coarse_grained_mode):
            warn_msg = f"The parameters `fineGrained` and `coarseGrained` are both set to `False`, so `vertical` " \
                       f"pruning step does not need to do anything and will be skipped."
            if logger is not None:
                logger.warning(warn_msg)
            else:
                print(warn_msg)
            return candidate_path
        prune_file_path = get_pruner_prefix(get_name_wosuffix(candidate_path)) + VERTICAL_PRUNER_SUFFIX + \
            FFR_FILE_SUFFIX
        if os.path.exists(prune_file_path):
            info_msg = f"The vertical pruning process may have been completed, obtain directly from `{prune_file_path}`."
            warn_msg = "If vertical pruning needs to be re-processed, please stop and manually clear the cache files."
            if logger is not None:
                logger.info(info_msg)
                logger.warning(warn_msg)
            else:
                print(info_msg + '\n' + warn_msg)
            return prune_file_path
        # Pre-defined
        min_length = config.extractor.min_length
        if logger is not None:
            logger.info(">> Vertical Pruning")
        else:
            print(">> Vertical Pruning")
        if len(kwargs) > 0:
            if logger is not None:
                logger.warning(f"The following parameters: `{kwargs}` are not applicable "
                               f"for this pruner.")
            else:
                print(
                    f"The following parameters: `{kwargs}` are not applicable for this pruner.")
        if not os.path.exists(candidate_path):
            err_msg = f"The candidate file `{candidate_path}` seems not exists, please check."
            if logger is not None:
                logger.error(err_msg)
            raise Exception(err_msg)
        # Generate slots graph
        slots_graph, candidate_mapper = generate_slots_graph(
            candidate_path, worker_num, logger)
        # Read all candidates
        candidates = read_ffrecord_file(
            candidate_path, desc="Loading candidates")
        # Gather vertical candidate groups
        vertical_group = clustering_vertical_candidates(slots_graph, candidates, candidate_mapper, min_length,
                                                        logger, worker_num, cache_dir)
        vertical_cluster, vertical_graph = vertical_group
        # Coarse-grained pruning
        if isinstance(coarse_grained_mode, bool) and coarse_grained_mode:
            coarse_grained_mode = dict()
        if isinstance(coarse_grained_mode, dict):
            coarse_worker_num = coarse_grained_mode.pop(
                "workerNum", worker_num)
            coarse_results = prune_vertical_coarse(candidates, coarse_grained_mode, vertical_graph, logger,
                                                   worker_num=coarse_worker_num)
            if coarse_worker_num > 1:  # Fork Multi-processor
                coarse_pruned_index = reduce(
                    operator.concat, [res[0] for res in coarse_results])
                coarse_pruned_candidates = reduce(
                    operator.concat, [res[1] for res in coarse_results])
            else:
                coarse_pruned_index, coarse_pruned_candidates = coarse_results
            info_msg = "After coarse-grained pruning, `{}` candidates will be pruned.".format(
                len(coarse_pruned_candidates))
            if logger is not None:
                logger.info(info_msg)
            else:
                print(info_msg)
        else:
            coarse_pruned_index, coarse_pruned_candidates = None, None
        # Fine-grained pruning
        if isinstance(fine_grained_mode, bool) and fine_grained_mode:
            fine_grained_mode = dict()
        if isinstance(fine_grained_mode, dict):
            if config is None:
                err_msg = "If fine-grained pruning is required, the `config` that used to construct the `Association`" \
                          " module cannot be `None`."
                if logger is not None:
                    logger.error(err_msg)
                raise Exception(err_msg)
            if encoder is None:
                err_msg = "If fine-grained pruning is required, the `encoder` that used to construct the `Association`"\
                          " module cannot be `None`."
                if logger is not None:
                    logger.error(err_msg)
                raise Exception(err_msg)
            fine_worker_num = fine_grained_mode.pop("workerNum", worker_num)
            fine_results = prune_vertical_fine(fine_worker_num, candidates, config, fine_grained_mode, encoder,
                                               vertical_cluster, logger)
            if fine_worker_num > 1:  # Spawn Multi-processor
                fine_pruned_index = reduce(
                    operator.concat, [res[0] for res in fine_results])
                fine_pruned_candidates = reduce(
                    operator.concat, [res[1] for res in fine_results])
            else:
                fine_pruned_index, fine_pruned_candidates = fine_results
        else:
            fine_pruned_index, fine_pruned_candidates = None, None
        info_msg = "After fine-grained pruning, `{}` candidates will be pruned.".format(
            len(fine_pruned_candidates))
        if logger is not None:
            logger.info(info_msg)
        else:
            print(info_msg)
        # Combination
        if isinstance(fine_grained_mode, dict) and isinstance(coarse_grained_mode, dict):
            pruned_index = list(
                reduce(comb_operator, [set(coarse_pruned_index), set(fine_pruned_index)]))
            pruned_candidates = list(reduce(
                comb_operator, [set(coarse_pruned_candidates), set(fine_pruned_candidates)]))
            pruned_index.sort(reverse=True)
            info_msg = "After applying `{}` operator over multi-grained pruning, `{}` candidates will be " \
                       "pruned, remaining `{}` candidates.".format(comb_opstr, len(pruned_candidates),
                                                                   len(candidates) - len(pruned_candidates))
            if logger is not None:
                logger.info(info_msg)
            else:
                print(info_msg)
        elif isinstance(fine_grained_mode, dict):
            pruned_index, pruned_candidates = fine_pruned_index, fine_pruned_candidates
        else:  # coarse-grained case
            pruned_index, pruned_candidates = coarse_pruned_index, coarse_pruned_candidates
        if debug:
            if encoder is None:
                err_msg = "If debug mode is required, the `encoder` that used to parse candidates cannot be `None`."
                if logger is not None:
                    logger.error(err_msg)
                raise Exception(err_msg)
            vh_prune_debug(pruned_candidates, vertical_graph,
                           encoder, logger, ver_or_hor="ver")
        # Prune & Save
        for index in pruned_index:
            del candidates[index]
        write_ffrecord_file(prune_file_path, candidates, logger)
        return prune_file_path


class HorizontalPruner(PrunerTemplate):
    @staticmethod
    def prune(candidate_path: Union[str, os.PathLike], **kwargs) -> Union[str, os.PathLike]:
        useless_args = ["config"]
        for arg in useless_args:
            if arg in kwargs.keys():
                del kwargs[arg]
        logger = kwargs.pop("logger", None)
        encoder = kwargs.pop("encoder", None)
        worker_num = kwargs.pop("workerNum", 1)
        map_level = kwargs.pop("mapper", None)
        debug = kwargs.pop("debug", None)
        # Prune args
        min_freq = kwargs.pop("minFreq", 1)
        prune_file_path = get_pruner_prefix(get_name_wosuffix(
            candidate_path)) + HORIZONTAL_PRUNER_SUFFIX + FFR_FILE_SUFFIX
        if os.path.exists(prune_file_path):
            info_msg = f"The horizontal pruning process may have been completed, obtain directly from `{prune_file_path}`."
            warn_msg = "If horizontal pruning needs to be re-processed, please stop and manually clear the cache files."
            if logger is not None:
                logger.info(info_msg)
                logger.warning(warn_msg)
            else:
                print(info_msg + '\n' + warn_msg)
            return prune_file_path
        if logger is not None:
            logger.info(">> Horizontal Pruning")
        else:
            print(">> Horizontal Pruning")
        if len(kwargs) > 0:
            if logger is not None:
                logger.warning(f"The following parameters: `{kwargs}` are not applicable "
                               f"for this pruner.")
            else:
                print(
                    f"The following parameters: `{kwargs}` are not applicable for this pruner.")
        if not os.path.exists(candidate_path):
            err_msg = f"The candidate file `{candidate_path}` seems not exists, please check."
            if logger is not None:
                logger.error(err_msg)
            raise Exception(err_msg)
        # Generate slots graph
        slots_graph, candidate_mapper = generate_slots_graph(
            candidate_path, worker_num, logger)
        # Read all candidates
        candidates = read_ffrecord_file(
            candidate_path, desc="Loading candidates")
        # Level mapper
        if map_level is None:
            level_mapper = list(range(len(encoder.ava_levels)))
        else:
            level_mapper = []
            for level in map_level:
                if level not in encoder.ava_levels:
                    warn_msg = f"There is no level named `{level}`, so it will be ignored. Please check."
                    if logger is not None:
                        logger.warning(warn_msg)
                    else:
                        print(warn_msg)
                    continue
                else:
                    level_mapper.append(encoder.ava_levels.index(level))
        # Gather vertical candidate groups
        horizontal_group = clustering_horizontal_candidates(slots_graph, candidates, candidate_mapper, encoder,
                                                            level_mapper, logger, worker_num)
        horizontal_cluster, horizontal_graph = horizontal_group
        results = prune_horizontal(
            candidates, min_freq, horizontal_graph, logger, worker_num=worker_num)
        if worker_num > 1:  # Fork Multi-processor
            pruned_index = reduce(operator.concat, [res[0] for res in results])
            pruned_candidates = reduce(
                operator.concat, [res[1] for res in results])
        else:
            pruned_index, pruned_candidates = results
        pruned_index.sort(reverse=True)
        info_msg = "After horizontal pruning, `{}` candidates will be pruned, remaining `{}` candidates.".format(
            len(pruned_candidates), len(candidates) - len(pruned_candidates))
        if logger is not None:
            logger.info(info_msg)
        else:
            print(info_msg)
        if debug:
            if encoder is None:
                err_msg = "If debug mode is required, the `encoder` that used to parse candidates cannot be `None`."
                if logger is not None:
                    logger.error(err_msg)
                raise Exception(err_msg)
            vh_prune_debug(pruned_candidates, horizontal_graph,
                           encoder, logger, ver_or_hor="hor")
        # Prune & Save
        for index in pruned_index:
            del candidates[index]
        write_ffrecord_file(prune_file_path, candidates, logger)
        return prune_file_path


prune_handler = {
    'freq': FreqPruner,
    'vertical': VerticalPruner,
    'horizontal': HorizontalPruner
}
