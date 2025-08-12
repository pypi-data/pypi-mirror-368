import pickle
import os
import random
from typing import Union, Tuple, Optional, List, Type, Any, Dict
from tqdm import tqdm
from collections import Counter
from logging import Logger
from functools import reduce
from collections import OrderedDict
import traceback
from copy import deepcopy
from itertools import chain

from ffrecord import FileReader
import cytoolz as cy
import matplotlib.pyplot as plt
import torch
from torch.cuda import device_count
import networkx as nx
import cytoolz as cy
import numpy as np
from sklearn.utils import murmurhash3_32

from .multi_processor import MultiProcessor, SpawnMultiProcessor, mp_allocate_data, mp_dynamic_device_data
from .utils_ds import PGraph, CTree
from .file_loader import get_pruner_prefix, get_name_wosuffix
from .predefine import SLOTS_GRAPH_FOR_PRUNER_SUFFIX, PT_FILE_SUFFIX, NORMALIZED_FREQ_SUFFIX, FFR_FILE_SUFFIX, MP_TEMPO_FILE_VERTICAL_PRUNE_CLUSTER
from .file_loader import read_ffrecord_file, write_ffrecord_file


try:
    import mmh3
    MMH3_fLAG = True
except:
    MMH3_fLAG = False

try:
    import ruptures as rpt
    RUPTURES_FLAG = True
except:
    RUPTURES_FLAG = False


FORBID_SLOTS = ['<PUNCT>', '<-RRB->', '<-LRB->', '<.>', '<,>', '<``>', '<"">', "<''>", '<:>', '<$>', '<#>',
                '.', ',', '!', ';', ':', '[', ']', '(', ')', '{', '}', 'Ġ(', 'Ġ)',
                '#', "\\", "$", "%", "&", "'", "(", ")", "*", "+", "-", "/", '"',
                'Ġ#', "Ġ!", "\\", "Ġ$", "Ġ%", "Ġ&", "Ġ'", "Ġ*", "Ġ+", "Ġ,", "Ġ-", "Ġ.", 'Ġ"', "Ġ/",
                'Ġ[', 'Ġ]',  'Ġ{', 'Ġ}']
RECOMMAND_CAPACITY = 10_000
SAMPLE_FORMAT = [6, 12, 15, 30]
SAMPLE_COLUMNS = ["Index", "TokID", "Token", "Logit"]
PELT_MODELS = ["l1", "l2", "rbf"]
PENEALTY = [0, 10]


def get_forbid_slots(encoder):
    return encoder.convert_tokens_to_ids(FORBID_SLOTS)


def patch_batch_to_sentences(current_batch: list, reserved_part: Union[list, None]) -> Tuple[list, Union[list, None]]:
    sentences, wm_masks, reserved_new = [], [], []
    sentence, split_indices, ori_wm_masks = current_batch
    split_indices = [0] + split_indices

    def align_wmmasks(wmmask: list, start_idx: int) -> list:
        for i, x in enumerate(wmmask):
            wmmask[i][0] = x[0] - start_idx
            wmmask[i][1] = x[1] - start_idx
        return wmmask

    def obtain_submasks(wwmask: list, start: int, end: int) -> list:
        new_masks = []
        for mask in wwmask:
            if mask[1] < start:
                continue
            if mask[0] >= end:
                break
            new_masks.append(mask)
        return new_masks

    for spidx in range(1, len(split_indices)):
        sub_sentence = sentence[split_indices[spidx-1]: split_indices[spidx]]
        sub_wwmasks = deepcopy(obtain_submasks(
            ori_wm_masks, split_indices[spidx-1], split_indices[spidx]))
        if spidx == 1 and reserved_part is not None:
            reserve_sentence, reserve_wmmask = reserved_part
            sub_sentence = reserve_sentence + sub_sentence
            sub_wwmasks = reserve_wmmask + \
                align_wmmasks(sub_wwmasks, - len(reserve_sentence))
        else:
            sub_wwmasks = align_wmmasks(sub_wwmasks, split_indices[spidx-1])
        sentences.append(sub_sentence)
        wm_masks.append(sub_wwmasks)
    coupled_batch = list(zip(sentences, wm_masks))
    if split_indices[-1] < len(sentence):
        reserve_sentence_new = sentence[split_indices[-1]:]
        reserve_wwmasks_new = obtain_submasks(
            ori_wm_masks, split_indices[-1], len(sentence))
        reserve_wwmasks_new = align_wmmasks(
            reserve_wwmasks_new, split_indices[-1])
        reserved_new = [reserve_sentence_new, reserve_wwmasks_new]

    if not reserved_new:
        reserved_new = None
    return coupled_batch, reserved_new


def compose_slots(sentence: list, cur_index: list, level_map: dict, level: str) -> list:
    if len(cur_index) == 1:
        return [sentence[cur_index[0]][level_map[level]]]
    else:
        if level in ['lexical']:
            return [sentence[idx][level_map[level]] for idx in cur_index]
        else:
            return [sentence[cur_index[0]][level_map[level]]]


def compute_murmurhash(key: Union[int, str, np.ndarray, list], seed: Optional[int] = 0, need_key: bool = False) -> Union[int, Tuple[int, str]]:
    if isinstance(key, list):
        key = '-'.join([str(ele) for ele in key])
    if MMH3_fLAG:
        hash_func = mmh3.hash128
    else:
        hash_func = murmurhash3_32
    hash_code = hash_func(key, seed=seed)
    if not need_key:
        return hash_code
    else:
        return hash_code, key


def forbid_detector(sentence: list, ww_mask: list, ava_levels: dict, forbid_list: list) -> bool:
    FORBID_FLAG = False
    for level in ava_levels:
        if compose_slots(sentence, ww_mask, ava_levels, level)[0] in forbid_list:
            FORBID_FLAG = True
            break
    return FORBID_FLAG


def flatten_slots(slots: Union[list, tuple]) -> list:
    """
    Flatten a nested list for lexical level components.
    e.g., [(1, 2), 3, (4, 5, 6)] ---> [1, 2, 3, 4, 5, 6]
    """
    if len(slots) < 1:
        flattened = list()
    elif len(slots) == 1:
        if isinstance(slots[0], tuple):
            flattened = list(slots[0])
        else:
            flattened = slots
    else:
        flattened = reduce(lambda x, y: (list(x) if isinstance(x, tuple) else [x] if isinstance(x, int) else x) +
                           ([y] if isinstance(y, int) else list(y)), slots)
    return flattened


class LRUCache(OrderedDict):
    def __init__(self, capacity: Optional[int] = RECOMMAND_CAPACITY):
        super(LRUCache, self).__init__()
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value
        else:
            value = None
        return value

    def set(self, key, value):
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value
        else:
            if len(self.cache) == self.capacity:
                self.cache.popitem(last=False)
                self.cache[key] = value
            else:
                self.cache[key] = value


@MultiProcessor
def mp_candidate_counter(proc_id: int, worker_num: int, candidate_path: Union[str, os.PathLike]) -> Type[dict]:
    candidate_pool = []
    candidate_reader = FileReader(candidate_path, False)
    candidate_num = candidate_reader.n
    start, end = mp_allocate_data(candidate_num, proc_id, worker_num)
    # Load candidates
    for index in tqdm(range(start, end), desc='Computing candidates with proc {}'.format(proc_id), position=proc_id):
        try:
            candidate = tuple(pickle.loads(candidate_reader.read_one(index)))
            # Avoid using murmurhash3-128
            candidate_pool.append(candidate)
        except Exception as e:
            continue
    candidate_reader.close()
    # Counter is low-efficient, we substitute with cytools
    freq = cy.frequencies(candidate_pool)
    return freq


def vis_frequency_figure(frequency: Counter) -> None:
    sorted_freq = list(frequency.values())
    plt.hist(sorted_freq, bins=100, log=True)
    plt.show()


@MultiProcessor
def construct_slots_graph(proc_id: int, worker_num, candidate_path: Union[str, os.PathLike],
                          logger: Optional[Logger] = None) -> Tuple[PGraph, Dict]:
    # Initialize a graph
    slots_graph, candidate_mapper = PGraph(logger=logger), dict()
    candidate_reader = FileReader(candidate_path, True)
    candidate_num = candidate_reader.n
    start, end = mp_allocate_data(candidate_num, proc_id, worker_num)
    # Load candidates
    for index in tqdm(range(start, end), desc='Constructing graph with proc {}'.format(proc_id), position=proc_id):
        candidate = tuple(pickle.loads(candidate_reader.read_one(index))[
                          0])  # Without frequency
        candidate_mapper[index] = candidate
        slots_graph.add_candidates(candidate, index)
    candidate_reader.close()
    return slots_graph, candidate_mapper


def clustering_vertical_candidates(graph: PGraph, candidates: List[tuple], candidate_mapper: dict, min_length: int,
                                   logger: Optional[Logger] = None, worker_num: Optional[int] = 1,
                                   cache_dir: str = './cache') -> Tuple[List[CTree], nx.DiGraph]:
    info_msg = "Building candidate networks and clusters for vertical pruning."
    if logger is not None:
        logger.info(info_msg)
    else:
        print(info_msg)
    candidates = list(dict(candidates).keys())
    # Sort by length and then filter (number of slots)
    ori_candidates = deepcopy(set(candidates))  # Without freq
    candidates.sort(key=lambda x: len(x), reverse=True)
    candidates = list(cy.filter(lambda x: len(x) > min_length, candidates))
    # candidate_mapper_inv = dict((v, k) for k, v in candidate_mapper.items())
    tempo_file_name = os.path.join(
        cache_dir, MP_TEMPO_FILE_VERTICAL_PRUNE_CLUSTER + PT_FILE_SUFFIX)
    torch.save({"graph": graph, "candidates": candidates, "mapper": candidate_mapper, "ori": ori_candidates},
               tempo_file_name)
    cluster_res = mp_clustering_vertical(
        tempo_file_name, logger, worker_num=worker_num)
    # Combination
    if worker_num > 1:
        dup_index = reduce(set.union, [set(res[1]) for res in cluster_res])
        cluster_comb = list(chain(*[res[0] for res in cluster_res]))
        clusters = list(
            cy.filter(lambda x: x.data not in dup_index, cluster_comb))
        candidate_graph = nx.compose_all([res[2] for res in cluster_res])
    else:
        clusters, _, candidate_graph = cluster_res
    try:
        os.remove(tempo_file_name)
    except Exception as e:
        if logger is not None:
            logger.error(e)
        traceback.print_exc()
    return clusters, candidate_graph


@MultiProcessor
def mp_clustering_vertical(proc_id: int, worker_num: int, tempo_file: str, logger: Optional[Logger] = None
                           ) -> Tuple[List[CTree], List[tuple], nx.DiGraph]:
    # Load tempo data
    tempo_data = torch.load(tempo_file)
    graph, sorted_candidates, candidate_mapper, reference = tempo_data["graph"], tempo_data["candidates"], \
        tempo_data["mapper"], tempo_data["ori"]
    # Ensure consistent distribution of data length allocated to each worker
    proc_candidates = sorted_candidates[proc_id::worker_num]
    # Find all groups
    clusters, dup_index, candidate_graph = [], [], nx.DiGraph()
    for i, candidate in enumerate(tqdm(proc_candidates, desc="Clustering vertical candidates with proc {}".format(
            proc_id), position=proc_id)):
        try:
            if candidate in dup_index:
                continue
            cluster, dups = graph.all_sub_candidates(
                candidate, candidate_mapper, reference)
            cluster.to_graph(candidate_graph)
            if cluster.no_childs():
                continue
            clusters.append(cluster)
            dup_index.extend(dups)
        except Exception as e:
            if logger is not None:
                logger.error(e)
            traceback.print_exc()
            continue
    return clusters, dup_index, candidate_graph


@MultiProcessor
def prune_vertical_coarse(proc_id: int, worker_num: int, candidates: List[tuple], prune_args: dict,
                          candidate_graph: nx.DiGraph, logger: Optional[Logger] = False
                          ) -> Tuple[List[int], List[tuple]]:
    start, end = mp_allocate_data(len(candidates), proc_id, worker_num)
    min_lknum = prune_args.pop("minFreq", 1)
    pruned_index, pruned_candidates = [], []
    for index in tqdm(range(start, end), desc="Pruning candidates with proc {}".format(proc_id), position=proc_id):
        candidate = candidates[index][0]  # Without freq
        if candidate not in candidate_graph:
            continue
        linked_edges = candidate_graph[candidate]
        filtered_edges = list(
            cy.filter(lambda x: x['relation'] == 'child', linked_edges.values()))
        if len(filtered_edges) > min_lknum or len(filtered_edges) == 0:
            continue
        pruned_index.append(index)
        pruned_candidates.append(candidate)
    pruned_index = pruned_index[::-1]
    return pruned_index, pruned_candidates


def prune_vertical_fine(worker_num: int, candidates: List[tuple], config, prune_args: dict, encoder,
                        candidate_cluster: List[CTree], logger: Optional[Logger] = None
                        ) -> List[Any]:
    # Parse params
    allow_cuda = prune_args.pop("allowCuda", False)
    gpu_indices = prune_args.pop("gpuIndices", None)
    num_per_gpu = prune_args.pop("numberPerGpu", 1)
    batch_size = prune_args.pop("batchSize", 1)
    # Prepare and check
    if not allow_cuda:
        if gpu_indices is not None and len(gpu_indices) > 0:
            warn_msg = "Though you have set `gpu_indices`, it will be ignored and CUDA won't be used due to your " \
                       "`allow_cuda` setting being false."
            if logger is not None:
                logger.warning(warn_msg)
            else:
                print(warn_msg)
            gpu_indices = None
        if num_per_gpu > 0:
            warn_msg = "Though you have set `number_per_gpu`, it will be ignored due to your `allow_cuda` " \
                       "setting being false."
            if logger is not None:
                logger.warning(warn_msg)
            else:
                print(warn_msg)
            num_per_gpu = 0
        else:
            gpu_devices_num = device_count()
            if gpu_indices is not None and (len(gpu_indices) > gpu_devices_num or
                                            max(gpu_indices) >= gpu_devices_num):
                warn_msg = "The `gpu_indices` seems to be set incorrectly, it does not match the number of physical" \
                    " devices so the settings will be ignored. Please check."
                if logger is not None:
                    logger.warning(warn_msg)
                else:
                    print(warn_msg)
                allow_cuda, gpu_indices = False, None
    # Launch processor to generate the graph and prune
    dominates = mp_prune_fine_dominates(config, prune_args, encoder, candidate_cluster, allow_cuda, gpu_indices,
                                        num_per_gpu, batch_size, logger, worker_num=worker_num)
    graphs = mp_generate_fine_graph(
        candidate_cluster, dominates, logger, worker_num=worker_num)
    if worker_num > 1:
        graph = nx.compose_all(graphs)
    else:
        graph = graphs
    return mp_prune_fine(candidates, graph, logger, worker_num=worker_num)


@MultiProcessor
def mp_prune_fine(proc_id: int, worker_num: int, candidates: List[tuple], candidate_graph: nx.DiGraph,
                  logger: Optional[Logger] = False) -> Tuple[List[int], List[tuple]]:
    start, end = mp_allocate_data(len(candidates), proc_id, worker_num)
    pruned_index, pruned_candidates = [], []
    for index in tqdm(range(start, end), desc="Pruning candidates with proc {}".format(proc_id), position=proc_id):
        try:
            candidate = candidates[index][0]  # Without freq
            if candidate not in candidate_graph:
                continue
            linked_edges = candidate_graph[candidate]
            filtered_edges = list(
                cy.filter(lambda x: x['relation'] != 'domby', linked_edges.values()))
            if len(filtered_edges) > 0:
                continue
            pruned_index.append(index)
            pruned_candidates.append(candidate)
        except Exception as e:
            if logger is not None:
                logger.error(e)
            else:
                print(e)
            continue
    pruned_index = pruned_index[::-1]
    return pruned_index, pruned_candidates


@MultiProcessor
def mp_generate_fine_graph(proc_id: int, worker_num: int, candidate_cluster: List[CTree], dominates: List[List],
                           logger: Optional[Logger] = None) -> nx.DiGraph:
    # TODO:Verify the mp safety for nx.DiGraph
    graph = nx.DiGraph()
    start, end = mp_allocate_data(len(candidate_cluster), proc_id, worker_num)
    for index in tqdm(range(start, end), desc='Processing graph with proc {}'.format(proc_id), position=proc_id):
        try:
            dominate = dominates[index]
            if len(list(cy.filter(lambda x: len(x) > 0, dominate))) == 0: continue
            cluster = candidate_cluster[index]
            cluster.dominates_to_graph(graph, dominate)
        except Exception as e:
            if logger is not None:
                logger.error(e)
            else:
                print(e)
            continue
    return graph


@SpawnMultiProcessor
def mp_prune_fine_dominates(proc_id: int, worker_num: int, config, prune_args: dict, encoder,
                            candidate_cluster: List[CTree], allow_cuda: bool, gpu_indices: Union[List[int], None],
                            num_per_gpu: int, batch_size: int, logger: Optional[Logger] = None
                            ) -> List[List]:
    from ..lm.association.association import Association
    # Initialization
    kwargs = {"mode": "dynamic", "refer_num": None, "beam_size": None}
    if "extractor" in config.__dict__:
        kwargs = {"mode": config.extractor.candidate_mode,
                  "refer_num": config.extractor.ref_num,
                  "beam_size": config.extractor.beam_size
                  }
    kwargs = cy.valfilter(lambda x: x is not None, kwargs)
    kwargs.update(prune_args)
    device = torch.device('cpu')
    if allow_cuda:
        start, end, device = mp_dynamic_device_data(len(candidate_cluster), proc_id, worker_num,
                                                    gpu_indices, num_per_gpu)
    else:
        start, end = mp_allocate_data(
            len(candidate_cluster), proc_id, worker_num)
    asso_handler = Association(config, logger, device, encoder)
    dominates, asso_inputs = [], []
    for index in tqdm(range(start, end), desc='Processing dominate slots with proc {}'.format(proc_id), position=proc_id):
        try:
            if len(asso_inputs) >= batch_size:
                dominates.extend(
                    asso_handler.compute_dominate_slots(asso_inputs, **kwargs))
                asso_inputs = []
            asso_inputs.append(flatten_slots(candidate_cluster[index].data))
        except Exception as e:
            if logger is not None:
                logger.error(e)
            else:
                print(e)
            traceback.print_exc()
    if asso_inputs:
        dominates.extend(
            asso_handler.compute_dominate_slots(asso_inputs, **kwargs))
    return dominates


def vh_prune_debug(pruned_candidates: List[tuple], candidate_graph: nx.DiGraph, encoder,
                   logger: Optional[Logger] = None, ver_or_hor="ver") -> None:
    from .utils_cxs import convert_slots_to_str
    pruned_debug_path = input(
        "Input a valid path for the debug file output: (s/S for skip):")
    if pruned_debug_path in ["s", "S"]:
        return
    try:
        with open(pruned_debug_path, 'w', encoding='utf-8') as debug_fp:
            for i, candidate in enumerate(tqdm(pruned_candidates, desc="Converting pruned candidates for debug")):
                debug_fp.write("[{}] {}\n".format(
                    i+1, convert_slots_to_str(candidate, encoder, logger)))
                if ver_or_hor == "ver":
                    debug_fp.write("Parents:\n")
                    for par in candidate_graph[candidate]:
                        if len(par) > len(candidate):
                            debug_fp.write("{}\n".format(
                                convert_slots_to_str(par, encoder, logger)))
                    debug_fp.write("\n")
                elif ver_or_hor == "hor":
                    debug_fp.write("Childs:\n")
                    for par in candidate_graph[candidate]:
                        debug_fp.write("{}\n".format(
                            convert_slots_to_str(par, encoder, logger)))
                    debug_fp.write("\n")
                else:
                    raise Exception(
                        "The param `ver_or_hor` can only be selected in [`ver`, `hor`], please check.")
    except Exception as e:
        if logger is not None:
            logger.error(e)
        traceback.print_exc()


def generate_slots_graph(candidate_path: Union[str, os.PathLike], worker_num: int, logger: Optional[Logger] = None
                         ) -> Tuple[PGraph, Dict]:
    worker_num = 1  # Forbid multiprocessing
    slots_graph_file_path = get_pruner_prefix(get_name_wosuffix(candidate_path)) + SLOTS_GRAPH_FOR_PRUNER_SUFFIX + \
        PT_FILE_SUFFIX
    if os.path.exists(slots_graph_file_path):
        slots_data = torch.load(slots_graph_file_path)
        slots_graph = slots_data['graph']
        candidate_mapper = slots_data['mapper']
        info_msg = f"Detecting the existence of the slot graph, load directly from {slots_graph_file_path}. " \
                   f"If you want to re-generate it, please manually delete the temporary file."
        if logger is not None:
            logger.info(info_msg)
        else:
            print(info_msg)
    else:
        slots_graph, candidate_mapper = construct_slots_graph(
            candidate_path, logger, worker_num=worker_num)
        # There are some issues in multiprocessing with nx.Graph, use worker_num=1
        if not isinstance(slots_graph, PGraph):
            slots_graph = nx.compose_all(slots_graph)
        if worker_num > 1:
            candidate_mapper = reduce(
                lambda x, y: {**x, **y}, candidate_mapper)
        torch.save({'graph': slots_graph, 'mapper': candidate_mapper},
                   slots_graph_file_path)
        info_msg = f"The slot graph is generated and saved temporarily at {slots_graph_file_path}."
        if logger is not None:
            logger.info(info_msg)
        else:
            print(info_msg)
    return slots_graph, candidate_mapper


def clustering_horizontal_candidates(graph: PGraph, candidates: List[tuple], candidate_mapper: dict, encoder,
                                     level_mapper: list, logger: Optional[Logger] = None, worker_num: Optional[int] = 1
                                     ) -> Tuple[List[CTree], nx.DiGraph]:
    info_msg = "Building candidate networks and clusters for horizontal pruning."
    if logger is not None:
        logger.info(info_msg)
    else:
        print(info_msg)
    # Gather level mapper
    mapper = mp_obtain_level_mapper(candidates, encoder, level_mapper, logger)
    # Sort by length and then filter (number of slots)
    candidates.sort(key=lambda x: len(x), reverse=True)
    cluster_res = mp_clustering_horizontal(
        graph, candidates, candidate_mapper, mapper, logger, worker_num=worker_num)
    # Combination
    if worker_num > 1:
        clusters = list(chain(*[res[0] for res in cluster_res]))
        candidate_graph = nx.compose_all([res[1] for res in cluster_res])
    else:
        clusters, candidate_graph = cluster_res
    return clusters, candidate_graph


@MultiProcessor
def mp_clustering_horizontal(proc_id: int, worker_num: int, graph: PGraph, candidates: List[tuple],
                             candidate_mapper: dict, mapper: tuple, logger: Optional[Logger] = None
                             ) -> Tuple[List[CTree], nx.DiGraph]:
    mapper_b2t, mapper_t2b = mapper
    proc_candidates = candidates[proc_id::worker_num]
    reference = set(candidates)
    # Find all groups
    cluster_groups, candidate_graph = [], nx.DiGraph()
    for i, candidate in enumerate(tqdm(proc_candidates, desc="Clustering horizontal candidates with proc {}".format(
            proc_id), position=proc_id)):
        try:
            candidate = candidate[0]  # Without freq
            clusters = graph.all_match_candidates(
                candidate, candidate_mapper, reference, mapper_b2t, mapper_t2b)
            for cluster in clusters:
                cluster.to_graph(candidate_graph)
            cluster_groups.extend(clusters)
        except Exception as e:
            if logger is not None:
                logger.error(e)
            traceback.print_exc()
            continue
    return cluster_groups, candidate_graph


def mp_obtain_level_mapper(candidates: List[tuple], encoder, level_mapper: list,
                           logger: Optional[Logger] = None) -> Tuple[Dict, Dict]:
    mapper_dict_up, mapper_dict_down = {}, {}
    slot_to_lexical = {}
    for i, candidate in enumerate(tqdm(candidates, desc="Gathering lexical slot")):
        for slot in candidate[0]:  # Without frequency
            if slot in slot_to_lexical:
                continue
            if isinstance(slot, int) and encoder.is_lexical(slot):
                lexical_slot = encoder.decode_tokens_to_str(
                    encoder.convert_ids_to_tokens(slot))
                slot_to_lexical[slot] = lexical_slot
            elif isinstance(slot, tuple):
                lexical_token = encoder.convert_ids_to_tokens(slot)
                lexical_slot = encoder.decode_tokens_to_str(lexical_token)
                slot_to_lexical[slot] = lexical_slot
    for slot_id, slot in tqdm(slot_to_lexical.items(), desc="Generating the mapping relations"):
        slot_group = encoder.encode(slot)
        if slot_group is None or len(slot_group) < 1:
            continue
        slot_group = slot_group[0]
        slot_group = [slot_group[index] for index in level_mapper]
        # Substitute lexical slot
        slot_group[0] = slot_id
        for i in range(len(slot_group)):
            if i < len(slot_group) - 1 and slot_group[i] not in mapper_dict_up:
                mapper_dict_up[slot_group[i]] = set()
                for level, element in enumerate(slot_group[i+1:]):
                    mapper_dict_up[slot_group[i]].add((element, level + 1))
            if i > 0:
                if slot_group[i] not in mapper_dict_down:
                    mapper_dict_down[slot_group[i]] = set()
                for level, element in enumerate(slot_group[:i]):
                    mapper_dict_down[slot_group[i]].add((element, level))
    return mapper_dict_up, mapper_dict_down


@MultiProcessor
def prune_horizontal(proc_id: int, worker_num: int, candidates: List[tuple], min_freq: int,
                     candidate_graph: nx.DiGraph, logger: Optional[Logger] = False
                     ) -> Tuple[List[int], List[tuple]]:
    start, end = mp_allocate_data(len(candidates), proc_id, worker_num)
    pruned_index, pruned_candidates = [], []
    for index in tqdm(range(start, end), desc="Pruning candidates with proc {}".format(proc_id), position=proc_id):
        try:
            candidate = candidates[index][0]
            if candidate not in candidate_graph:
                continue
            linked_edges = candidate_graph[candidate]
            filtered_edges = list(
                cy.filter(lambda x: x['relation'] == 'father', linked_edges.values()))
            if len(filtered_edges) > min_freq or len(filtered_edges) == 0:
                continue
            pruned_index.append(index)
            pruned_candidates.append(candidate)
        except Exception as e:
            if logger is not None:
                logger.error(e)
            traceback.print_exc()
            raise Exception(e)
    return pruned_index, pruned_candidates


def normalize_freq_to_score(candidate_path: Union[str, os.PathLike]) -> str:
    candidates = read_ffrecord_file(candidate_path, desc="Loading candidates")
    # sum_freq = sum([ele[-1] for ele in candidates])
    # candidates = [(ele[0], ele[1] / sum_freq) for ele in candidates]
    candidates = [(ele[0], ele[1]) for ele in candidates]
    save_path = get_pruner_prefix(get_name_wosuffix(candidate_path)) + NORMALIZED_FREQ_SUFFIX + \
        FFR_FILE_SUFFIX
    write_ffrecord_file(save_path, candidates)
    return save_path


def rpt_hyper_debug(sentences: List, length_range: List, asso_handler, logger: Optional[Logger] = None,
                    cache_dir: Optional[os.PathLike] = "./cache", **kwargs) -> None:
    # Collect examplars
    beam_size = kwargs.pop("beam_size", 20)
    is_visualize = kwargs.pop("visualize", False)
    encoder = kwargs.pop("encoder", None)
    if not os.path.exists(cache_dir) and is_visualize:
        err_msg = 'The `cache_dir` is not exists, please checj'
        if logger is not None:
            logger.error(err_msg)
        raise IOError(err_msg)
    examplars = []
    for sentence in sentences:
        ava_start = list(set(range(len(sentence[0]) - length_range[0])))
        start = random.choice(ava_start)
        max_length = min(length_range[1], len(sentence[0]) - start - 1)
        length = random.randint(length_range[0], max_length)
        examplar = []
        for index in range(start, start + length - 1):
            examplar.append(random.choice(sentence[0][index]))
        examplars.append([examplar, sentence[0][index + 1]])
    logits, indexes = asso_handler.compute_candidate(
        list(list(zip(*examplars))[0]), **{"rpt_debug": True})
    # Annotate the labels
    annotated, tempo_remove = [], []
    for index in range(len(examplars)):
        logit, inds = logits[index], indexes[index]
        cp, tempo_path = rpt_debug_info(logit, inds, index, examplars[index][-1], encoder, vis=is_visualize,
                                        beam_size=beam_size, cache_dir=cache_dir)
        if tempo_path is not None:
            tempo_remove.append(tempo_path)
        if cp is None:
            continue
        annotated.append([logit, cp])
    if len(annotated) < 1:
        err_msg = "Missing annotated data, please try again."
        if logger is not None:
            logger.error(err_msg)
        else:
            print(err_msg)
    # Estimate
    estimate_rpt_params(annotated, logger, **kwargs)
    # Remove
    for tempo_path in tempo_remove:
        try:
            os.remove(tempo_path)
        except Exception as e:
            if logger is not None:
                logger.error(e)
            else:
                print(e)


def rpt_debug_info(logits: torch.Tensor, inds: torch.Tensor, index: int, label: tuple,
                   encoder=None, beam_size: Optional[int] = 20, vis: Optional[bool] = False,
                   cache_dir: Optional[str] = './cache', logger: Optional[Logger] = None
                   ) -> Tuple[int, Union[None, str]]:
    split_line = "+" + "".join(["-" * ele + "+" for ele in SAMPLE_FORMAT])
    print(split_line)
    print("|" + f"Sample {index}".center(sum(SAMPLE_FORMAT) +
          len(SAMPLE_FORMAT) - 1) + "|")
    print(split_line)
    print("|" + "|".join([ele.center(SAMPLE_FORMAT[idx])
          for idx, ele in enumerate(SAMPLE_COLUMNS)]) + "|")
    for idx in range(min(logits.shape[0], beam_size)):
        out_data = [str(idx), str(int(inds[idx])),
                    "w/o" if encoder is None else encoder.convert_ids_to_tokens(int(inds[idx])), str(float(logits[idx]))]
        print("|" + "|".join([ele.center(SAMPLE_FORMAT[i])
              for i, ele in enumerate(out_data)]) + "|")
    print(split_line)
    print("|" + f"Next: {label}".center(sum(SAMPLE_FORMAT) +
          len(SAMPLE_FORMAT) - 1) + "|")
    if encoder is not None:
        print("|" + f"Next (Token): {tuple([encoder.convert_ids_to_tokens(int(ele)) for ele in label])}".center(
            sum(SAMPLE_FORMAT) + len(SAMPLE_FORMAT) - 1) + "|")
    if vis:
        tempo_path = os.path.join(cache_dir, f"sample_{index}.png")
        fig, ax = plt.subplots()
        x_tick = range(min(logits.shape[0], beam_size))
        ax.plot(x_tick, logits[:min(logits.shape[0], beam_size)].numpy())
        plt.title(f"SAMPLE {index}")
        ax.set(xticks=x_tick, xticklabels=x_tick)
        plt.savefig(tempo_path, dpi=300)
        plt.show()
        print("|" + ("Save at: " + tempo_path).center(sum(SAMPLE_FORMAT) +
              len(SAMPLE_FORMAT) - 1) + "|")
    else:
        tempo_path = None
    print("+" + "-" * (sum(SAMPLE_FORMAT) + len(SAMPLE_FORMAT) - 1) + "+")
    while True:
        change_point = input(
            f"The change point index of sample {index} (s/S for skip):")
        if change_point in ['s', 'S']:
            change_point = None
        try:
            change_point = eval(change_point)
            if change_point >= min(logits.shape[0], beam_size):
                raise Exception(
                    "The input cannot greater than beam_size, please check")
            elif change_point < 0:
                raise Exception(
                    "The input cannot lower than zero, please check")
            elif not isinstance(change_point, int):
                raise Exception(
                    f"The input can only be int type, rather than {type(change_point)}")
            break
        except Exception as e:
            if logger is not None:
                logger.error(e)
            else:
                print(e)
    return change_point, tempo_path


def estimate_rpt_params(data: List, logger: Optional[Logger] = None, **kwargs):
    if not RUPTURES_FLAG:
        err_msg = "It looks like you haven't installed the ruptures library yet. Please install it first" \
                  " using `pip install ruptures`."
        if logger is not None:
            logger.error(err_msg)
        else:
            print(err_msg)
        return
    pelt_models = kwargs.pop("pelt_models", PELT_MODELS)
    pelt_models = list(set(pelt_models).intersection(set(PELT_MODELS)))
    if len(pelt_models) < 1:
        er_msg = "The parameter `pelt_models` seems to be set incorrectly, please check."
        if logger is not None:
            logger.error(er_msg)
        else:
            print(er_msg)
        return
    pen_range = kwargs.pop("penalty_range", PENEALTY)
    pen_num = kwargs.pop("penalty_num", 10)
    results_table = np.zeros((len(pelt_models), pen_num))
    pen_step = (pen_range[-1] - pen_range[0]) / pen_num
    pen = list(np.arange(pen_range[0], pen_range[-1], pen_step))
    for sample in data:
        logits, label = sample[0], sample[1]
        smoothed = np.convolve(logits, np.ones(3) / 3, mode='valid')
        for k_idx, kernel in enumerate(pelt_models):
            detector = rpt.Pelt(model=kernel).fit(logits.numpy())
            for p_idx, p_num in enumerate(pen):
                change_points = detector.predict(pen=p_num)
                loss = (label - change_points[0]) ** 2
                results_table[k_idx][p_idx] += loss
    model_id, pen_id = np.where(results_table == np.min(results_table))
    print(">> The best hyper-parameters is:")
    print(f"MODEL = {pelt_models[model_id[0]]}, PENALTY={pen[pen_id[0]]}")
