import os
import pickle
from typing import Dict, Union, Optional, Any, List, Tuple
from logging import Logger
from tqdm import tqdm
from functools import reduce
import traceback
from copy import deepcopy
from math import floor, ceil
import difflib

from ffrecord import FileReader, FileWriter
import numpy as np
import torch
from torch import nn
import cytoolz as cy
import networkx as nx

from .multi_processor import SpawnMultiProcessor, MultiProcessor, mp_allocate_data, mp_dynamic_device_data
from .file_loader import get_data_nums, convert_ffrecord, read_ffrecord_file, write_ffrecord_file, serialize
from .predefine import MP_LEARNER_UNPACK_FILE_NAME_TEMPLATE, MP_LEARNER_MDLGRAPH_FILE_NAME_TEMPLATE, MP_LEARNER_MDLGRAPH_STAT_FILE_NAME_TEMPLATE, MP_TEMPO_FILE_COMPUTE_SYNSSEMCL
from .predefine import PT_FILE_SUFFIX, MP_TEMPO_FILE_COMPUTE_DISTANCES_CAND, FFR_FILE_SUFFIX, MP_TEMPO_FILE_COMPUTE_DISTANCES, MP_TEMPO_FILE_COMPUTE_DISTANCES_LTOT, MP_TEMPO_FILE_COMPUTE_DISTANCES_GRAPH
from .utils_extractor import patch_batch_to_sentences, flatten_slots
from ..tools.mdlgraph import MDLGraph, MDLGraphProxy
from .utils_ds import PGraph


try:
    # Accelerate with CUDA
    import cuml
    import cupy as cp
    from cuml.metrics import pairwise_distances
    UMAP_HANDLER = cuml.UMAP
    from ..tools.hdbscan.hdbscan import OHDBSCAN
    HDBSCAN_HANDLER = OHDBSCAN
    CUML_ACCELERATOR = True
    PAIRWISE_DIST_HANDLER = pairwise_distances
except ImportError:
    # Compute with CPU
    import umap
    from ..tools.hdbscan.hdbscan import OHDBSCANCPU
    UMAP_HANDLER = umap.UMAP
    HDBSCAN_HANDLER = OHDBSCANCPU
    CUML_ACCELERATOR = False
    PAIRWISE_DIST_HANDLER = None

try:
    import msgpack
    MSGPACK_ON = True
except ImportError:
    MSGPACK_ON = False

MSGPACK_ON = False

FFRECORD_MAX_EVENT= 4096
DEFAULT_SYNSEM_CHUNK_SIZE = 4  # Need to be 2 for default


def initialize_state(state_num: int, method: str = "random", **kwargs) -> object:
    logger = kwargs.pop("logger", None)
    if method == 'random':
        init_state = np.random.randint(0, 2, state_num).astype(np.bool_).tolist()
    elif method == 'all-false':
        init_state = np.zeros(state_num).astype(np.bool_).tolist()
    elif method == 'all-true':
        init_state = np.ones(state_num).astype(np.bool_).tolist()
    else:
        warn_msg = f"There is no method `{method}` available here, so it will be replaced with the default `random` " \
                   f"method. You can also stop and perform a check if you prefer."
        if logger is not None: logger.warning(warn_msg)
        else: print(warn_msg)
        return initialize_state(state_num)
    return init_state


@SpawnMultiProcessor
def acquire_candidate_hidden(proc_id: int, worker_num: int, config, parser, **kwargs) -> torch.Tensor:
    from ..lm.association.association import Association
    # Parse params
    logger = kwargs.pop("logger", None)
    allow_cuda = kwargs.pop("allowCuda", False)
    gpu_indices = kwargs.pop("gpuIndices", [])
    batch_size = kwargs.pop("batchSize", 1)
    num_per_gpu, gpu_cpu_ratio = 1, 1
    # Data length
    data_num = len(parser)
    device = torch.device("cpu")
    if allow_cuda:
        start, end, device = mp_dynamic_device_data(data_num, proc_id, worker_num, gpu_indices,
                                                    num_per_gpu, gpu_cpu_ratio)
    else:
        start, end = mp_allocate_data(data_num, proc_id, worker_num)
    # Initialize association module
    asso_handler = Association(config, logger, device, parser.encoder)
    # Encode cxs
    hidden_states, batched = None, []
    for index in tqdm(range(start, end), desc="Processing with proc {}".format(proc_id), position=proc_id):
        cxs = parser.cxs_decoder[index] if index < len(parser.cxs_decoder) else parser.added_cxs_decoder[index]
        flattened = flatten_slots(cxs)
        batched.append(flattened)
        if len(batched) >= batch_size:
            hidden_state = asso_handler.encode_construction(batched)
            if hidden_states is None: hidden_states = hidden_state
            else: hidden_states = torch.cat((hidden_states, hidden_state))
            batched = []
    if batched:
        hidden_state = asso_handler.encode_construction(batched)
        if hidden_states is None: hidden_states = hidden_state
        else: hidden_states = torch.cat((hidden_states, hidden_state))
    return hidden_states


def generate_sem_clusters(cxs_embeddings: Optional[Union[np.ndarray, torch.Tensor]] = None,
                          umap_embeddings: Optional[Union[np.ndarray, tuple]] = None,
                          need_umap: Optional[bool] = False, n_neighbors: Optional[int] = 15,
                          n_components: Optional[int] = 5, min_cluster_size: Optional[int] = 5,
                          random_state: Optional[int] = None, n_jobs: Optional[int] = -1,
                          logger: Optional[Logger] = None) -> Any:
    # Dimensionality reduction
    if umap_embeddings is None:
        info_msg = "Dimensionality reduction of hidden states for constructions" + \
                   (" (Accelerated)" if CUML_ACCELERATOR else "")
        if logger is not None: logger.info(info_msg)
        else: print(info_msg)
        if CUML_ACCELERATOR:
            kwargs = {}
            cxs_embeddings = cxs_embeddings.cuda()
        else: kwargs = {"n_jobs": n_jobs}
        umap_embeddings = (UMAP_HANDLER(n_neighbors=n_neighbors,
                                        n_components=n_components,
                                        metric='cosine',
                                        random_state=random_state,
                                        **kwargs)
                           .fit_transform(cxs_embeddings))
        info_msg = "Initialize semantic clustering" + (" (Accelerated)" if CUML_ACCELERATOR else "")
        if logger is not None: logger.info(info_msg)
        else: print(info_msg)
    # Clustering
    clusters = HDBSCAN_HANDLER(min_cluster_size=min_cluster_size,
                               metric='euclidean',
                               cluster_selection_method='eom').fit(umap_embeddings)
    clusters.generate_prediction_data()
    if need_umap: return umap_embeddings, clusters
    else: return clusters


@MultiProcessor
def mp_naive_lexical_mapper(proc_id: int, worker_num: int, mp_path: Union[os.PathLike, str]) -> Dict:
    l_to_t, visited_slots = {}, []
    tempo_data = torch.load(mp_path)
    candidates, encoder = tempo_data["candidates"], tempo_data["encoder"]
    start, end = mp_allocate_data(len(candidates), proc_id, worker_num)
    for candidx in tqdm(range(start, end), desc="Building level mapper with proc {}".format(proc_id), position=proc_id):
        candidate = candidates[candidx]
        for slotidx in range(len(candidate)):
            slot = candidate[slotidx]
            if slot in visited_slots: continue
            if isinstance(slot, int) and encoder.is_lexical(slot):
                lexical_slot = encoder.decode_tokens_to_str(encoder.convert_ids_to_tokens(slot))
            elif isinstance(slot, tuple):
                lexical_token = encoder.convert_ids_to_tokens(slot)
                lexical_slot = encoder.decode_tokens_to_str(lexical_token)
            else: continue
            slot_group = encoder.encode(lexical_slot)
            if slot_group is None or len(slot_group) < 1: continue
            slot_group = list(slot_group[0])
            slot_group[0] = slot
            for slid in range(len(slot_group) - 1):
                sl = slot_group[slid]
                if sl in visited_slots: continue
                visited_slots.append(sl)
                others = slot_group[slid+1:]
                l_to_t[sl] = others
    return l_to_t


def compute_syntactic_dist(parser, cover_ratio: Optional[float] = 0.8, min_length: Optional[int] = 3,
                           half_weight: Optional[float] = 0.5, worker_num: Optional[int] = 1,
                           logger: Optional[Logger] = None, cache_dir: Optional[str] = './cache', **kwargs
                           ) -> Dict[int, Dict[int, float]]:
    fast_mode = kwargs.pop("fastSyn", True)
    all_candidates, encoder = {**parser.cxs_decoder, **parser.added_cxs_decoder}, parser.encoder
    encoder_dict = {**parser.cxs_encoder, **parser.added_cxs_encoder}
    tempo_remove_ls = []
    # Save tempo files
    if fast_mode:
        if hasattr(parser, "cxs_file_path") and parser.cxs_file_path is not None:
            # Original candidates (without flattening)
            ori_candidates = read_ffrecord_file(parser.cxs_file_path)
            proxy_candidates = {}
            for index in all_candidates:
                candidate = all_candidates[index]
                if isinstance(candidate, tuple) and len(candidate) == 2 and isinstance(candidate[-1], float):
                    candidate, score = candidate[0], candidate[1]
                else:
                    score = None
                flat_candidate = tuple(flatten_slots(candidate))
                if flat_candidate in parser.cxs_encoder:
                    candidate_result = candidate if score is None else (candidate, score)
                    proxy_candidates[parser.cxs_encoder[flat_candidate]] = candidate_result
            sorted_keys = list(proxy_candidates.keys())
            sorted_keys.sort()
            all_candidates = {key: proxy_candidates[key] for key in sorted_keys}
        write_ffrecord_file(os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES_CAND + FFR_FILE_SUFFIX),
                            all_candidates.values(), logger)
        tempo_remove_ls.append(os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES_CAND + FFR_FILE_SUFFIX))
    torch.save({
        "candidates": all_candidates, "encoder": encoder
    }, os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES + PT_FILE_SUFFIX))
    tempo_remove_ls.append(os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES + PT_FILE_SUFFIX))
    info_msg = "Preparing the level mapping dictionary"
    if logger is not None: logger.info(info_msg)
    else: print(info_msg)
    level_mapper = mp_naive_lexical_mapper(os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES + PT_FILE_SUFFIX),
                                           worker_num=worker_num)
    if worker_num > 1: ltot = reduce(lambda x, y: {**x, **y}, level_mapper)
    else: ltot = level_mapper
    torch.save({"ltot": ltot}, os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES_LTOT + PT_FILE_SUFFIX))
    tempo_remove_ls.append(os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES_LTOT + PT_FILE_SUFFIX))
    # Computing distances
    if not fast_mode:
        syn_dists = compute_dists(os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES + PT_FILE_SUFFIX),
                                  os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES_LTOT + PT_FILE_SUFFIX),
                                  cover_ratio, min_length, half_weight, logger, worker_num=worker_num)
    else:
        syn_dists, graph_tempo_path = compute_dists_fast(worker_num,
                                       os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES_CAND + FFR_FILE_SUFFIX),
                                       os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES_LTOT + PT_FILE_SUFFIX),
                                       encoder_dict, cover_ratio, min_length, half_weight, logger, cache_dir)
        tempo_remove_ls.append(graph_tempo_path)
    if worker_num > 1:
        info_msg = "Merging syntactic distances"
        if logger is not None: logger.info(info_msg)
        else: print(info_msg)
        syn_dists_return = syn_dists[0]
        for dic_id in tqdm(range(1, len(syn_dists)), desc="Merging"):
            dic = syn_dists[dic_id]
            for key in dic:
                if key not in syn_dists_return: syn_dists_return[key] = dic[key]
                else: syn_dists_return[key] = {**syn_dists_return[key], **dic[key]}
    else:
        syn_dists_return = syn_dists
    # Delete tempo files
    for tempo_path in tempo_remove_ls:
        try:
            os.remove(tempo_path)
        except Exception as e:
            err_info = f"Error occured when removing cache file {tempo_path}, detailed message:"
            err_info += e
            if logger is not None: logger.error(err_info)
            traceback.print_exc()
            raise Exception(e)
    return syn_dists_return


def get_common_length(list1: Union[list, tuple], list2: Union[list, tuple]) -> int:
    matcher = difflib.SequenceMatcher(None, list1, list2)
    match = matcher.find_longest_match(0, len(list1), 0, len(list2))
    length = match.size
    return length


@MultiProcessor
def compute_dists(proc_id: int, worker_num: int, mp_path: Union[str, os.PathLike], ltot_path: Union[str, os.PathLike],
                  cover_ratio: Optional[float] = 0.8, min_length: Optional[int] = 3,
                  half_weight: Optional[float] = 0.5, logger: Optional[Logger] = None) -> Dict[int, Dict[int, float]]:
    syn_dists, cxs_top_map = {}, {}
    tempo_data, ltot = torch.load(mp_path), torch.load(ltot_path)["ltot"]
    all_candidates, encoder = tempo_data["candidates"], tempo_data["encoder"]
    proc_candidates = dict([[_, all_candidates[_]] for _ in list(all_candidates)[proc_id::worker_num]])

    def top_cxs(cxs: tuple, index: int) -> tuple:
        if index not in cxs_top_map:
            proxy_cxs = []
            for slot in cxs:
                if slot in ltot:
                    proxy_cxs.append(ltot[slot][-1])
                else:
                    proxy_cxs.append(slot)
            cxs_top_map[index] = tuple(proxy_cxs)
        else:
            proxy_cxs = cxs_top_map[index]
        return proxy_cxs

    # Naive loop
    for i in tqdm(proc_candidates, desc="Processing syntactic distance with proc {}".format(proc_id), position=proc_id):
        cxs_1 = proc_candidates[i]
        proxy_cxs_1 = top_cxs(cxs_1, i)
        proxy_length_1 = len(proxy_cxs_1)
        for j in range(i + 1, len(all_candidates)):
            cxs_2 = all_candidates[j]
            proxy_cxs_2 = top_cxs(cxs_2, j)
            proxy_length_2 = len(proxy_cxs_2)
            # Rule 1 - If the length of a short candidate is cover_ratio times smaller than the length of a long
            # candidate, it should be ignored.
            min_proxy_length = min(proxy_length_1, proxy_length_2)
            if floor(max(proxy_length_1, proxy_length_2) * cover_ratio) > min_proxy_length: continue
            # Rule 2 - If the overlap between the types of two candidate slots is less than cover_ratio,
            # it should be ignored.
            min_threshold = max(min_length, ceil(min_proxy_length * cover_ratio))
            if len(set(proxy_cxs_1).intersection(proxy_cxs_2)) < min_threshold: continue
            # Rule 3 -  If the overlap between two candidate slots is less than cover_ratio, it should be ignored.
            common_length = get_common_length(proxy_cxs_1, proxy_cxs_2)
            if common_length < min_threshold: continue
            exact_match = get_common_length(cxs_1, cxs_2)
            half_match = common_length - exact_match
            scores = half_match * half_weight + exact_match
            if i not in syn_dists: syn_dists[i] = {j: scores / len(cxs_1)}
            else: syn_dists[i][j] = scores / len(cxs_1)
            if j not in syn_dists: syn_dists[j] = {i: scores / len(cxs_2)}
            else: syn_dists[j][i] = scores / len(cxs_2)
    return syn_dists


def compute_dists_fast(worker_num: int, candidate_path: Union[str, os.PathLike],
                       ltot_path: Union[str, os.PathLike], encoder_dict: Dict, cover_ratio: Optional[float] = 0.8,
                       min_length: Optional[int] = 3, half_weight: Optional[float] = 0.5,
                       logger: Optional[Logger] = None, cache_dir: Optional[str] = './cache'
                       ) -> Tuple[Any, str]:
    # MP Slot graph generation
    slots_graph = construct_high_slots_graph(candidate_path, encoder_dict, ltot_path, logger, worker_num=1)
    if not isinstance(slots_graph, PGraph): slots_graph = nx.compose_all(slots_graph)
    tempo_graph_path = os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_DISTANCES_GRAPH + PT_FILE_SUFFIX)
    torch.save({"graph": slots_graph}, tempo_graph_path)
    dist_dict = mp_graph_dist(candidate_path, tempo_graph_path, ltot_path, cover_ratio, min_length, half_weight,
                              logger, worker_num=worker_num)
    return dist_dict, tempo_graph_path


@MultiProcessor
def mp_graph_dist(proc_id: int, worker_num: int, candidate_path: Union[str, os.PathLike],
                  graph_path: Union[str, os.PathLike], ltot_path: Union[str, os.PathLike],
                  cover_ratio: Optional[float] = 0.8, min_length: Optional[int] = 3,
                  half_weight: Optional[float] = 0.5, logger: Optional[Logger] = None) -> Dict:
    syn_dists, cxs_top_map, loaded = {}, {}, {}
    graph = torch.load(graph_path)["graph"]
    ltot = torch.load(ltot_path)["ltot"]

    def top_cxs(cxs: tuple, index: int) -> tuple:
        if index not in cxs_top_map:
            proxy_cxs = []
            for slot in cxs:
                if slot in ltot:
                    proxy_cxs.append(ltot[slot][-1])
                else:
                    proxy_cxs.append(slot)
            cxs_top_map[index] = tuple(proxy_cxs)
        else:
            proxy_cxs = cxs_top_map[index]
        return proxy_cxs

    candidate_reader = FileReader(candidate_path, True)
    candidate_num = candidate_reader.n
    candidate_indices = list(range(candidate_num))
    proc_candidates = candidate_indices[proc_id::worker_num]
    for i in tqdm(proc_candidates, desc='Processing syntactic distance with proc {}'.format(
            proc_id), position=proc_id):
        try:
            if i in loaded: cxs_1 = loaded[i]
            else:
                cxs_1 = tuple(pickle.loads(candidate_reader.read_one(i)))
                loaded[i] = cxs_1
            proxy_cxs_1 = top_cxs(cxs_1, i)
            proxy_length_1 = len(proxy_cxs_1)
            related = graph.all_related_dists(cxs_1, i, ltot, min_length)
            for j in related:
                if j in loaded: cxs_2 = loaded[j]
                else:
                    cxs_2 = tuple(pickle.loads(candidate_reader.read_one(j)))
                    loaded[j] = cxs_2
                proxy_cxs_2 = top_cxs(cxs_2, j)
                proxy_length_2 = len(proxy_cxs_2)
                # Rule 1 - If the length of a short candidate is cover_ratio times smaller than the length of a long
                # candidate, it should be ignored.
                min_proxy_length = min(proxy_length_1, proxy_length_2)
                if floor(max(proxy_length_1, proxy_length_2) * cover_ratio) > min_proxy_length: continue
                # Rule 2 - If the overlap between the types of two candidate slots is less than cover_ratio,
                # it should be ignored.
                min_threshold = max(min_length, ceil(min_proxy_length * cover_ratio))
                if len(set(proxy_cxs_1).intersection(proxy_cxs_2)) < min_threshold: continue
                # Rule 3 -  If the overlap between two candidate slots is less than cover_ratio, it should be ignored.
                common_length = get_common_length(proxy_cxs_1, proxy_cxs_2)
                if common_length < min_threshold: continue
                exact_match = get_common_length(cxs_1, cxs_2)
                half_match = common_length - exact_match
                scores = half_match * half_weight + exact_match
                if i not in syn_dists: syn_dists[i] = {j: scores / len(cxs_1)}
                else: syn_dists[i][j] = scores / len(cxs_1)
                if j not in syn_dists: syn_dists[j] = {i: scores / len(cxs_2)}
                else: syn_dists[j][i] = scores / len(cxs_2)
        except Exception as e:
            if logger is not None: logger.error(e)
            traceback.print_exc()
            print(e)
            # raise Exception(e)
    candidate_reader.close()
    return syn_dists


def generate_soft_labels(distance_path: Union[os.PathLike, str], candidate_num: int) -> torch.Tensor:
    distance_reader = FileReader(distance_path, True)
    # Create dummy label mat
    labels = torch.ones((candidate_num, candidate_num))
    for row in tqdm(range(distance_reader.n), desc="Generating soft labels"):
        item = pickle.loads(distance_reader.read_one(row))
        if len(item) == 0: continue
        col, val = torch.tensor(list(item.keys())), torch.tensor(list(item.values()))
        labels[row][col] = val
    distance_reader.close()
    return labels


def calculate_chunk_indices(total_data_count, group_count):
    if group_count < 1:
        raise ValueError("Group count must be at least 1.")
    if total_data_count < group_count:
        raise ValueError("Group count is more than total data count.")
    base_size = total_data_count // group_count
    remainder = total_data_count % group_count
    indices = []
    current_index = 0
    for i in range(group_count):
        indices.append(current_index)
        current_index += base_size + (1 if i < remainder else 0)
    return indices


def compute_contrastive_loss(states: np.ndarray, hidden_states: Union[np.ndarray, torch.Tensor],
                             distance_info: Union[os.PathLike, str, torch.Tensor], similarity: np.array = None,
                             umap_states: np.ndarray = None, back_hmap_states: np.ndarray = None,
                             logger: Optional[Logger] = None, worker_num: Optional[int] = 1,
                             cache_dir: Optional[str] = './cache', **kwargs) -> float:
    tempo_files_path = os.path.join(cache_dir, MP_TEMPO_FILE_COMPUTE_SYNSSEMCL + PT_FILE_SUFFIX)
    seed = kwargs.pop("seed", 0)
    quiet = kwargs.pop("isQuiet", True)
    fast_mode = kwargs.pop("fastMode", False)
    batch_loss = kwargs.pop("batchLoss", False)
    need_cluster = kwargs.pop("needCluster", False)
    temperature = kwargs.pop("temperature", 0.01)
    if not need_cluster:
        if similarity is not None or isinstance(distance_info, torch.Tensor):
            with torch.no_grad():
                use_cuda = kwargs.pop("useCuda", True) if torch.cuda.is_available() else False
                chunk_size = kwargs.pop("chunkSize", DEFAULT_SYNSEM_CHUNK_SIZE)
                if chunk_size > 1 and use_cuda:
                    gathered_score = None
                    indices = calculate_chunk_indices(hidden_states.shape[0], chunk_size)
                    chunk_states = [torch.from_numpy(states[(states>=indices[cid]) & (states < indices[cid+1])] - indices[cid]).to('cuda:{}'.format(cid))
                              if cid < chunk_size - 1 else torch.from_numpy(states[states >= indices[cid]] - indices[cid]).to('cuda:{}'.format(cid))
                              for cid in range(chunk_size)]
                    chunk_states_offset = [0]
                    for i in range(1, len(chunk_states)): chunk_states_offset.append(chunk_states_offset[-1] + chunk_states[i-1].shape[0])
                    states = torch.from_numpy(states)
                    states = [states.to('cuda:{}'.format(cid)) for cid in range(chunk_size)]
                    for cid in range(chunk_size):
                        if chunk_states[cid].shape[0] < 1: continue
                        diag_offset = chunk_states_offset[cid]
                        scores = similarity[cid][chunk_states[cid]][:, states[cid]]
                        selected_dists = distance_info[cid][chunk_states[cid]][:, states[cid]]
                        scores[torch.arange(scores.shape[0]), torch.arange(scores.shape[0]) + diag_offset] = - float('inf')
                        scores = selected_dists * torch.softmax(scores / temperature, dim=1)
                        scores = - torch.log(torch.mean(scores * (selected_dists < 1).long(), dim=1))
                        scores[torch.isinf(scores)] = 0
                        gathered_score = torch.cat([gathered_score, scores.detach().cpu()]) if gathered_score is not None else scores.detach().cpu()
                    scores = gathered_score
                else:
                    scores = similarity[states][:, states]
                    selected_dists = distance_info[states][:, states]
                    scores.fill_diagonal_(float('-inf'))
                    scores = selected_dists * torch.softmax(scores / temperature, dim=1)
                    scores = - torch.log(torch.sum(scores * (selected_dists < 1).long(), dim=1))
                    scores[torch.isinf(scores)] = 0
                    scores = scores if not use_cuda else scores.detach().cpu()
            norm_loss = scores.mean() if batch_loss else scores.sum()
        else:
            err_msg = "If `need_cluster` is set to True, you should input `similarity` and `distance_info` first."
            if logger is not None: logger.error(err_msg)
            raise Exception(err_msg)
    else:
        if umap_states is None or back_hmap_states is None:
            err_msg = "If `needCluster` is set to True, `umap_states` and `back_hmap_states` cannot be None."
            if logger is not None:
                logger.error(err_msg)
            raise Exception(err_msg)
        # Clustering
        sem_umap_states = umap_states[states]
        clusters = generate_sem_clusters(umap_embeddings=sem_umap_states, need_umap=False, n_jobs=worker_num,
                                         random_state=seed, logger=logger)
        clusters.mirror_data = hidden_states[states]
        clusters.umap_states = back_hmap_states[states]
        predict_data = clusters.prediction_data_.exemplars
        cluster_hidden = torch.cat([torch.mean(tr, dim=0)[None] for tr in predict_data])
        candidate_label = np.array(clusters.labels_[states].tolist())
        state_index_map = map_state_to_idx(states)
        # Avoid open-mp error
        tempo_torch_thread_num = torch.get_num_threads()
        torch.set_num_threads(1)
        if fast_mode and CUML_ACCELERATOR:
            cluster_similarity = torch.from_numpy(PAIRWISE_DIST_HANDLER(cluster_hidden.numpy(), metric='cosine'))
            if batch_loss:
                torch.save(
                    {"states": states, "n_cluster": clusters.n_clusters_, "candidate_label": candidate_label,
                     "dist_path": distance_info, "state_map": state_index_map}, tempo_files_path)
                labels = mp_compute_cl_batch_label(tempo_files_path, logger, quiet,
                                                   **{**kwargs, **{"worker_num": worker_num}})
                torch.set_num_threads(tempo_torch_thread_num)
                if worker_num > 1: soft_labels = torch.cat(labels)
                else: soft_labels = labels
                scores = soft_labels * (1 - cluster_similarity - torch.eye(clusters.n_clusters_)) / temperature
                scores = - torch.log(torch.sum(torch.softmax(scores, dim=1) * (soft_labels < 1).long(), dim=1))
                # Avoid scores to be zero
                scores = torch.where(torch.isinf(scores), torch.zeros(scores.shape), scores)
                loss = torch.mean(scores)
            else:
                torch.save(
                    {"states": states,  "n_cluster": clusters.n_clusters_,
                     "cluster_similarity": cluster_similarity, "candidate_label": candidate_label, "dist_path": distance_info,
                     "state_map": state_index_map}, tempo_files_path)
                loss = mp_compute_cl_loss_fast(tempo_files_path, logger, quiet, **{**kwargs, **{"worker_num": worker_num}})
        else:
            if CUML_ACCELERATOR:
                allow_cuda = kwargs.pop("allowCuda", False)
                cluster_similarity = torch.from_numpy(PAIRWISE_DIST_HANDLER(
                    clusters.mirror_data.numpy(), cluster_hidden.numpy(), metric='cosine'))
                if allow_cuda: cluster_similarity = cluster_similarity.cuda()
                torch.save(
                    {"states": states, "n_cluster": clusters.n_clusters_, "candidate_label": candidate_label,
                     "dist_path": distance_info, "state_map": state_index_map}, tempo_files_path)
                labels = mp_compute_cl_batch_acel(tempo_files_path, logger, quiet,
                                                 **{**kwargs, **{"worker_num": worker_num}})
                torch.set_num_threads(tempo_torch_thread_num)
                if worker_num > 1: soft_labels = torch.cat(labels)
                else: soft_labels = labels
                if allow_cuda: soft_labels = soft_labels.cuda()
                scores = soft_labels * (1 - cluster_similarity) / temperature
                scores = - torch.log(torch.sum(torch.softmax(scores, dim=1) * (soft_labels < 1).long(), dim=1))
                # Avoid scores to be zero
                scores = torch.where(torch.isinf(scores), torch.zeros(
                    scores.shape, device="cuda" if allow_cuda else "cpu"), scores)
                loss = torch.mean(scores)
            else:
                torch.save(
                    {"states": states, "hidden": clusters.mirror_data, "n_cluster": clusters.n_clusters_,
                     "cluster_hidden": cluster_hidden, "candidate_label": candidate_label, "dist_path": distance_info,
                     "state_map": state_index_map}, tempo_files_path)
                loss = mp_compute_cl_loss(tempo_files_path, logger, quiet, **{**kwargs, **{"worker_num": worker_num}})
        torch.set_num_threads(tempo_torch_thread_num)
        if batch_loss: norm_loss = float(loss)
        else: norm_loss = np.mean(loss).tolist()
        # Clear tempo file
        os.remove(tempo_files_path)
    return norm_loss.item()


@MultiProcessor
def mp_compute_cl_batch_label(proc_id: int, worker_num: int, data_path: Union[os.PathLike, str],
                              logger: Optional[Logger] = None, quiet: Optional[bool] = True, **kwargs) -> torch.Tensor:
    # Process args and load data
    tempo_data = torch.load(data_path)
    states, n_cluster, dist_path, candidate_label, state_index_map = tempo_data["states"],  tempo_data["n_cluster"], \
        tempo_data["dist_path"], tempo_data["candidate_label"], tempo_data["state_map"]
    # Scaled
    set_states = set(states)
    distance_reader = FileReader(dist_path, True)
    # Determine data for different processors
    start, end = mp_allocate_data(n_cluster, proc_id, worker_num)
    # Create dummy label mat
    labels = torch.ones((end - start, n_cluster))
    # Cache
    cached_dict = {}

    def merge_dist_dict(a: dict, b: dict):
        for key in b:
            if key not in set_states: continue
            if key in a: a[key] = min((a[key], b[key]))
            else: a[key] = b[key]
        return a

    def fill_in_weights(c_index: int, pos_dict: dict) -> None:
        row = torch.full((len(pos_dict), ), c_index - start)
        col = torch.from_numpy(
            candidate_label[np.array(list(map(lambda x: state_index_map[x], pos_dict)), dtype=np.int32)]
        )
        val = torch.tensor(list(pos_dict.values()))
        labels.index_put_((row, col), val)

    def _compute_cl_labels(cluster_inds: int) -> None:
        ids_in_clusters = states[candidate_label == cluster_inds].tolist()
        if len(ids_in_clusters) < 1: return
        set_ids = set(ids_in_clusters)
        set_cached_ids = set(ids_in_clusters).intersection(cached_dict.keys())
        not_cached_ids = list(set_ids - set_cached_ids)
        if len(not_cached_ids) > FFRECORD_MAX_EVENT:
            cluster_data = []
            for i in range(0, len(not_cached_ids), FFRECORD_MAX_EVENT):
                cluster_data.extend(distance_reader.read(not_cached_ids[i:i+FFRECORD_MAX_EVENT]))
        else:
            cluster_data = distance_reader.read(ids_in_clusters)
        # deserialize data
        not_cache_clusters = [pickle.loads(b) for b in cluster_data]
        cached_dict.update(dict(zip(not_cached_ids, not_cache_clusters)))
        cached_clusters = [cached_dict[key] for key in set_cached_ids]
        clusters = cached_clusters + not_cache_clusters
        clusters[0] = cy.keyfilter(lambda x: x in set_states, clusters[0])
        clusters = reduce(merge_dist_dict, clusters)
        fill_in_weights(cluster_inds, clusters)

    # Start to process loss
    try:
        if quiet:
            for index in range(start, end): _compute_cl_labels(index)
        else:
            for index in tqdm(range(start, end), desc="Computing contrastive label with proc {}".format(proc_id),
                              position=proc_id): _compute_cl_labels(index)
    except Exception as e:
        traceback.print_exc()
        if logger is not None: logger.error(e)
        raise Exception(e)
    distance_reader.close()
    return labels


@MultiProcessor
def mp_compute_cl_batch_acel(proc_id: int, worker_num: int, data_path: Union[os.PathLike, str],
                            logger: Optional[Logger] = None, quiet: Optional[bool] = True, **kwargs) -> torch.Tensor:
    # Process args and load data
    tempo_data = torch.load(data_path)
    states, n_cluster, dist_path, candidate_label, state_index_map = tempo_data["states"], tempo_data["n_cluster"], \
        tempo_data["dist_path"], tempo_data["candidate_label"], tempo_data["state_map"]
    # Scaled
    set_states = set(states)
    distance_reader = FileReader(dist_path, True)
    # Determine data for different processors
    start, end = mp_allocate_data(len(states), proc_id, worker_num)
    # Create dummy label mat
    labels = torch.ones((end - start, n_cluster))

    def fill_in_weights(c_index: int, pos_dict: dict) -> None:
        row = torch.full((len(pos_dict), ), c_index - start)
        col = torch.tensor(list(pos_dict.keys()))
        val = torch.tensor(list(pos_dict.values()))
        labels.index_put_((row, col), val)

    def _compute_cl_labels(inds: int) -> None:
        cur_cxs_ids = states[inds]
        # Case: cxs is an outlier point, ignored.
        if candidate_label[inds] < 0: return
        clusters = pickle.loads(distance_reader.read_one(cur_cxs_ids))
        if len(clusters) < 1: return
        clusters = list(cy.keyfilter(lambda x: x in set_states, clusters).items())
        if len(clusters) < 1: return
        clusters = list(map(lambda x: [candidate_label[state_index_map[x[0]]], x[1]], clusters))
        clusters.sort(key=lambda x: x[-1], reverse=True)
        clusters = dict(clusters)
        if -1 in clusters: del clusters[-1]
        if len(clusters) < 1: return
        fill_in_weights(inds, clusters)

    # Start to process loss
    try:
        if quiet:
            for index in range(start, end):  _compute_cl_labels(index)
        else:
            for index in tqdm(range(start, end), desc="Computing contrastive label with proc {}".format(proc_id),
                              position=proc_id): _compute_cl_labels(index)
    except Exception as e:
        traceback.print_exc()
        if logger is not None: logger.error(e)
        raise Exception(e)
    distance_reader.close()
    return labels


@MultiProcessor
def mp_compute_cl_loss_fast(proc_id: int, worker_num: int, data_path: Union[os.PathLike, str],
                            logger: Optional[Logger] = None, quiet: Optional[bool] = True, **kwargs) -> List[float]:
    # Process args and load data
    if worker_num > 1: args = deepcopy(kwargs["kwds"])
    else: args = deepcopy(kwargs)
    temperature = args.pop("temperature", 0.01)
    tempo_data = torch.load(data_path)
    states, n_cluster, dist_path, cluster_similarity, candidate_label, state_index_map = \
        tempo_data["states"],  tempo_data["n_cluster"], tempo_data["dist_path"], \
            tempo_data["cluster_similarity"], tempo_data["candidate_label"], tempo_data["state_map"]
    # Scaled
    cluster_similarity_scale = (1 - cluster_similarity) / temperature
    set_states = set(states)
    total_cluster_set = set(list(range(n_cluster)))
    distance_reader = FileReader(dist_path, True)
    cl_loss = []
    # Determine data for different processors
    start, end = mp_allocate_data(n_cluster, proc_id, worker_num)

    def merge_dist_dict(a: dict, b: dict):
        for key in b:
            if key in a:
                a[key] = min((a[key], b[key]))
            else:
                a[key] = b[key]
        return a

    def convert_ids_to_clusters(pos_dict: dict) -> dict:
        pos_clusters = {}
        for pos in pos_dict:
            if pos not in set_states: continue
            cl = candidate_label[state_index_map[pos]]
            if cl in pos_clusters: pos_clusters[cl] = min(pos_clusters[cl], pos_dict[pos])
            else: pos_clusters[cl] = pos_dict[pos]
        return pos_clusters

    def _compute_cl(cluster_inds: int) -> None:
        ids_in_clusters = list(set(states[candidate_label == cluster_inds]))
        # Case: cxs is an outlier point, ignored.
        if len(ids_in_clusters) < 1: return
        if len(ids_in_clusters) > FFRECORD_MAX_EVENT:
            cluster_data = []
            for i in range(0, len(ids_in_clusters), FFRECORD_MAX_EVENT):
                cluster_data.extend(distance_reader.read(ids_in_clusters[i:i+FFRECORD_MAX_EVENT]))
        else:
            cluster_data = distance_reader.read(ids_in_clusters)
        # deserialize data
        positive_clusters = reduce(merge_dist_dict, [pickle.loads(b) for b in cluster_data])
        positive_clusters = convert_ids_to_clusters(positive_clusters)
        if cluster_inds in positive_clusters: del positive_clusters[cluster_inds]
        pos_key, pos_weight = positive_clusters.keys(), positive_clusters.values()
        positive_clusters = set(pos_key)
        negative_clusters = total_cluster_set - positive_clusters - {cluster_inds}
        if len(positive_clusters) < 1: return
        # Compute loss
        numerator = np.sum(np.exp(np.array(list(pos_weight)) * cluster_similarity_scale[cluster_inds, np.array(list(pos_key))]))
        denominator = np.sum(np.exp(cluster_similarity_scale[cluster_inds, np.array(list(negative_clusters))]))
        cll = - np.log(numerator / denominator).tolist()
        cl_loss.append(cll)

    # Start to process loss
    try:
        if quiet:
            for index in range(start, end):
                _compute_cl(index)
        else:
            for index in tqdm(range(start, end), desc="Computing contrastive loss with proc {}".format(proc_id),
                              position=proc_id):
                _compute_cl(index)
    except Exception as e:
        traceback.print_exc()
        if logger is not None: logger.error(e)
        raise Exception(e)
    distance_reader.close()
    return cl_loss


@SpawnMultiProcessor
def mp_compute_cl_loss(proc_id: int, worker_num: int, data_path: Union[os.PathLike, str],
                       logger: Optional[Logger] = None, quiet: Optional[bool] = True, **kwargs) -> List[float]:
    # Process args and load data
    if worker_num > 1: args = deepcopy(kwargs["kwds"])
    else: args = deepcopy(kwargs)
    temperature = args.pop("temperature", 0.1)
    allow_cuda = args.pop("allowCuda", False)
    gpu_indices = args.pop("gpuIndices", [])
    num_per_gpu = args.pop("numberPerGpu", 1)
    gpu_cpu_ratio = args.pop("gpuCpuRatio", 1)
    tempo_data = torch.load(data_path)
    candidates, states, hidden_states, n_cluster, dist_path, cluster_hidden, candidate_label, state_index_map = \
        tempo_data["candidates"], tempo_data["states"], tempo_data["hidden"], tempo_data["n_cluster"], \
        tempo_data["dist_path"], tempo_data["cluster_hidden"], tempo_data["candidate_label"], tempo_data["state_map"]
    total_cluster_set = set(list(range(n_cluster)))
    distance_reader = FileReader(dist_path, True)
    cl_loss = []
    # Determine data for different processors
    device = torch.device("cpu")
    if allow_cuda:
        start, end, device = mp_dynamic_device_data(len(states), proc_id, worker_num, gpu_indices,
                                                    num_per_gpu, gpu_cpu_ratio)
    else:
        start, end = mp_allocate_data(len(states), proc_id, worker_num)
    # Impl syn-sem loss module
    cl_handler = ContrastLoss(temperature, device).to(device)

    def _compute_cl(inds: int) -> None:
        cur_cxs_ids = states[inds]
        cur_label = candidate_label[inds].tolist()
        # Case: cxs is an outlier point, ignored.
        if cur_label < 0: return
        positive_cxs = pickle.loads(distance_reader.read_one(cur_cxs_ids))
        positive_cxs = [state_index_map[posidx] for posidx in positive_cxs if posidx in state_index_map]
        # Case: no similar point, ignored.
        if len(positive_cxs) < 1: return
        pos_label_set = set(candidate_label[np.array(positive_cxs)]) - {-1, cur_label}
        # Case: the similar cluster belongs to outlier.
        if len(pos_label_set) < 1: return
        # Hidden
        g_hidden = cluster_hidden[cur_label]
        g_pos_hidden = torch.cat([cluster_hidden[pos][None] for pos in pos_label_set])
        g_neg_hidden = torch.cat([cluster_hidden[pos][None] for pos in total_cluster_set - pos_label_set])
        cll = cl_handler(g_hidden, g_pos_hidden, g_neg_hidden).detach().cpu().numpy().tolist()
        cl_loss.append(cll)

    # Start to process loss
    try:
        if quiet:
            for index in range(start, end):
                _compute_cl(index)
        else:
            for index in tqdm(range(start, end), desc="Computing contrastive loss with proc {}".format(proc_id),
                              position=proc_id):
                _compute_cl(index)
    except Exception as e:
        traceback.print_exc()
        if logger is not None: logger.error(e)
        raise Exception(e)
    distance_reader.close()
    return cl_loss


def dict_dummy_writer(data_path: Union[os.PathLike, str], total_num: int, dict_data: Dict[int, Any]) -> None:
    writer = FileWriter(data_path, total_num)
    for index in range(total_num):
        if index in dict_data: element = dict_data[index]
        else: element = {}
        writer.write_one(serialize(element))
    writer.close()


def map_state_to_idx(states: np.ndarray) -> Dict:
    return dict(zip(states.tolist(), range(states.shape[0])))


class ContrastLoss(nn.Module):
    def __init__(self, temper: float, device: torch.device = torch.device("cpu")):
        super(ContrastLoss, self).__init__()
        self.temper = temper
        self.device = device
        self.cos = nn.CosineSimilarity(dim=-1)

    def forward(self, g: torch.Tensor, g_pos: torch.Tensor, g_neg:torch.Tensor, scaled: Optional[torch.Tensor] = None,
                ) -> torch.Tensor:
        with torch.no_grad():
            # Move tensor to device
            g = g.to(self.device)
            g_pos = g_pos.to(self.device)
            g_neg = g_neg.to(self.device)
            if scaled is not None: scaled = scaled.to(self.device)
            else: scaled = torch.ones(g_pos.shape[0], device=self.device)
            # Compute cl loss
            numerator = torch.sum(torch.exp(scaled * self.cos(g, g_pos) / self.temper))
            denominator = torch.sum(torch.exp(self.cos(g, g_neg) / self.temper))
            cl_loss = - torch.log(numerator / denominator)
        return cl_loss


def time_string(seconds):
    s = int(round(seconds))
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return '%4i:%02i:%02i' % (h, m, s)


# TODO: optimize the cost calculation
def compute_vocab_cost(vocab_range: dict) -> dict:
    r"""
    Args:
        vocab_range: dict, {vocab_type: (start_index, end_index)}
    Return:
        vocab_cost: dict, {(start_index, end_index): cost}
    """
    vocab_cost = {}
    vocab_size = vocab_range['lex'][1] - vocab_range['lex'][0]
    for v in vocab_range.values():
        vocab_cost[v] = vocab_size / (v[1] - v[0])
    return vocab_cost


def read_corpus_for_fsk(data_path) -> np.ndarray:
    corpus = []
    reader = FileReader(data_path, check_data=True)
    max_num = 10000
    def read_data(index_inner: int) -> Any:
        element = pickle.loads(reader.read_one(index_inner))
        corpus.append(element)
    
    if max_num > 0 and max_num < reader.n:
        for index in tqdm(range(max_num)): read_data(index)
    reader.close()

    raw_corpus = [sentence[0] for sentence in corpus]
    raw_corpus = [sentence for sentence in raw_corpus if len(sentence) == len(raw_corpus[0])]
    return np.array(raw_corpus)


@MultiProcessor
def construct_high_slots_graph(proc_id: int, worker_num, candidate_path: Union[str, os.PathLike], encoder_dict,
                               ltot_path: Union[str, os.PathLike], logger: Optional[Logger] = None) -> PGraph:
    ltot = torch.load(ltot_path)["ltot"]
    slots_graph = PGraph(logger=logger)
    candidate_reader = FileReader(candidate_path, True)
    candidate_num = candidate_reader.n
    index_set = set()
    start, end = mp_allocate_data(candidate_num, proc_id, worker_num)
    for index in tqdm(range(start, end), desc='Constructing slot graph with proc {}'.format(proc_id), position=proc_id):
        candidate = tuple(pickle.loads(candidate_reader.read_one(index)))
        if isinstance(candidate, tuple) and len(candidate) == 2 and (isinstance(candidate[-1], float) or isinstance(candidate[-1], int)):
            candidate = candidate[0]
        proxy_candidate = tuple(flatten_slots(candidate))
        proxy_index = encoder_dict[proxy_candidate]
        if proxy_index in index_set: continue
        index_set.add(proxy_index)
        slots_graph.add_candidates(candidate, proxy_index, **{"mapper": ltot})
    candidate_reader.close()
    return slots_graph


def init_mdlgraph(parser, num_sentences: int, pattern_length: np.array, init_states: List[bool]) -> MDLGraph:
    mdl_graph = MDLGraph(len(parser), num_sentences, pattern_length, np.array(init_states, dtype=np.int32))
    return mdl_graph


def merge_mdlgraph(mdl_graph: MDLGraph, sub_graph_path: str) -> None:
    sub_graph = torch.load(sub_graph_path)
    # Merge sentences
    for sentence in sub_graph.sentences:
        mdl_graph.merge_single_sentence(sentence.length, sentence.counter)
    # Merge patterns
    for index, pattern in enumerate(sub_graph.patterns):
        if len(pattern.linked) == 0: continue
        mdl_graph.merge_pattern(index, len(pattern.linked), np.array(pattern.linked, dtype=np.int32),
                                np.array(pattern.intervals, dtype=np.int32))


def build_mdlgraph(parser, sentence_path: List[str], init_states: np.array, batch_size: int,
                   worker_num: Optional[int] = 1, logger: Optional[Logger] = None, check_data: Optional[bool] = True,
                   cache_dir: Optional[str] = 'cache/') -> MDLGraph:

    data_nums = [0] + [get_data_nums(sentence_path[i], logger=logger) for i in range(len(sentence_path))][:-1]
    basements = np.cumsum(data_nums).tolist()
    mdl_graph_path = _build_mdlgraph(parser.init_kwargs, sentence_path, init_states, basements, batch_size, logger,
                                     check_data, cache_dir, worker_num=worker_num)
    if worker_num == 1:
        mdl_graph_path = [mdl_graph_path]
    stats = [torch.load(path[1]) for path in mdl_graph_path]
    num_sentences = sum([stats[i]["sentence"] for i in range(worker_num)])
    num_patterns = reduce(np.add, [stats[i]["pattern"] for i in range(worker_num)])
    num_patterns = num_patterns.astype(np.int32)

    mdl_graph = init_mdlgraph(parser, num_sentences, num_patterns, init_states=init_states)
    # Merge graph
    for i in tqdm(range(worker_num), desc="Merging"):
        merge_mdlgraph(mdl_graph, mdl_graph_path[i][0])
        os.remove(mdl_graph_path[i][0])
        os.remove(mdl_graph_path[i][1])
    # print(mdl_graph.avg_metrics)
    return mdl_graph


@MultiProcessor
def _build_mdlgraph(proc_id: int, worker_num, parser_args, sentence_path: List[str], init_states: np.array,
                    basements: List,  batch_size: int, logger: Optional[Logger] = None, check_data = True,
                    cahce_dir='cache/') -> Tuple:
    # Initialize Parser
    from ..parser.parser import Parser
    parser = Parser.from_pretrained(
        parser_args['name_or_path'], **{"logger": logger, "config": parser_args["config"]})
    mdl_graph_proxy = MDLGraphProxy(len(parser), init_states)
    # Args
    basement = basements[proc_id]
    sub_path = sentence_path[proc_id]
    out_path = os.path.join(cahce_dir, MP_LEARNER_MDLGRAPH_FILE_NAME_TEMPLATE.format(proc_id))
    out_stat_path = os.path.join(cahce_dir, MP_LEARNER_MDLGRAPH_STAT_FILE_NAME_TEMPLATE.format(proc_id))
    data_num = get_data_nums(sub_path, check_data=check_data, logger=logger)
    reader = FileReader(sub_path, check_data=check_data)
    for i in tqdm(range(data_num // batch_size + 1), desc="Building MDL subgraph with proc{}".format(proc_id),
                  position=proc_id):
        left, right = i * batch_size, (i + 1) * batch_size
        right = min(data_num, right)
        indices = list(range(left, right))
        data = reader.read(indices)
        batched_sentences = [pickle.loads(b) for b in data]
        parsed_results = parser.parse_only(batched_sentences)
        for index, matched in enumerate(parsed_results):
            mdl_graph_proxy.add_sentence(len(batched_sentences[index]), matched, basement)
    # Recorder
    num_sentences = len(mdl_graph_proxy.sentences)
    num_patterns = np.array([len(pat.intervals) for pat in mdl_graph_proxy.patterns])
    # I/O
    if MSGPACK_ON:
        with open(out_path, 'wb') as file_graph:
            file_graph.write(msgpack.packb(mdl_graph_proxy))

        with open(out_stat_path, 'wb') as file_stat:
            file_stat.write(msgpack.packb({"sentence": num_sentences, "pattern": num_patterns}))
    else:
        torch.save(mdl_graph_proxy, out_path)
        torch.save({"sentence": num_sentences, "pattern": num_patterns}, out_stat_path)
    os.remove(sub_path)
    return out_path, out_stat_path


def build_mdlgraph_hybrid(parser, sentence_path: str, init_states: np.ndarray, batch_size: int = 50, proc_id: int = -1, logger=None, check_data=True, cache_dir=None) -> MDLGraphProxy:
    basements = [0]
    mdl_graph_path = _build_mdlgraph_hybrid(proc_id,1,parser.init_kwargs, sentence_path, init_states, basements, batch_size, logger,
                                     check_data, cache_dir=cache_dir)
    mdl_graph_proxy = torch.load(mdl_graph_path[0])
    num_sentences = torch.load(mdl_graph_path[1])["sentence"]
    num_patterns = torch.load(mdl_graph_path[1])["pattern"].astype(np.int32)
    mdl_graph = init_mdlgraph(parser, num_sentences, num_patterns, init_states=init_states)
    merge_mdlgraph(mdl_graph, mdl_graph_path[0])
    os.remove(mdl_graph_path[0])
    os.remove(mdl_graph_path[1])
    return mdl_graph


def _build_mdlgraph_hybrid(proc_id: int, worker_num, parser_args, sentence_path: str, init_states: np.ndarray,
                    basements: List, batch_size: int, logger: Optional[Logger] = None, check_data = True,
                    cache_dir='cache/') -> Tuple:
    from ..parser.parser import Parser
    parser = Parser.from_pretrained(
        parser_args['name_or_path'], **{"logger": logger, "config": parser_args["config"]})
    mdl_graph_proxy = MDLGraphProxy(len(parser), init_states)
    # Args
    basement = basements[0]
    # sub_path = sentence_path[proc_id]
    out_path = os.path.join(cache_dir, MP_LEARNER_MDLGRAPH_FILE_NAME_TEMPLATE.format(proc_id))
    out_stat_path = os.path.join(cache_dir, MP_LEARNER_MDLGRAPH_STAT_FILE_NAME_TEMPLATE.format(proc_id))
    # data_num = get_data_nums(sub_path, check_data=check_data, logger=logger)
    readers = [FileReader(subpath) for subpath in sentence_path]
    # start, end = mp_allocate_data(sentences_num, proc_id, worker_num)
    sentences_num = readers[0].n
    start, end = 0, sentences_num
    
    for i in tqdm(range((end-start) // batch_size + 1), desc="Building MDL subgraph with proc{}".format(proc_id),
                  position=proc_id):
        left, right = start + i * batch_size, start + (i + 1) * batch_size
        right = min(sentences_num, right)
        indices = list(range(left, right))

        batched_sentences = readers[0].read(indices)
        batched_sentences = [pickle.loads(b) for b in batched_sentences]
        
        parsed_results = parser.parse_only(batched_sentences)

        for index, matched in enumerate(parsed_results):
            mdl_graph_proxy.add_sentence(len(batched_sentences[index]), matched, basement)
    # Recorder
    num_sentences = len(mdl_graph_proxy.sentences)
    num_patterns = np.array([len(pat.intervals) for pat in mdl_graph_proxy.patterns])
    # I/O
    if MSGPACK_ON:
        with open(out_path, 'wb') as file_graph:
            file_graph.write(msgpack.packb(mdl_graph_proxy))

        with open(out_stat_path, 'wb') as file_stat:
            file_stat.write(msgpack.packb({"sentence": num_sentences, "pattern": num_patterns}))
    else:
        torch.save(mdl_graph_proxy, out_path)
        torch.save({"sentence": num_sentences, "pattern": num_patterns}, out_stat_path)
    
    # for sub_path in sentence_path:
    #     os.remove(sub_path)
    return out_path, out_stat_path


def parallel_unpack_corpus(corpus_path: Union[str, os.PathLike], worker_num: Optional[int] = 1,
                           cache_dir: Optional[str] = 'cache/', logger: Optional[Logger] = None,
                           check_data: Optional[bool] = True) -> List:
    cache_path = _parallel_unpack_corpus(corpus_path, cache_dir, logger, check_data, worker_num=worker_num)
    return cache_path


@MultiProcessor
def _parallel_unpack_corpus(proc_id: int, worker_num, corpus_path: Union[str, os.PathLike],
                            out_path: Union[str, os.PathLike], logger: Optional[Logger] = None,
                            check_data = True) -> str:
    # for test
    # data_num = 1000
    data_num = get_data_nums(corpus_path, logger=logger)
    start, end = mp_allocate_data(data_num, proc_id, worker_num)
    reader = FileReader(corpus_path, check_data)
    if not os.path.exists(out_path):
        err_msg = "The `cache_dir` with `{}` is not exist, please check.".format(out_path)
        if logger is not None:
            logger.error(err_msg)
        raise IOError(err_msg)
    out_file_path = os.path.join(out_path, MP_LEARNER_UNPACK_FILE_NAME_TEMPLATE.format(proc_id))
    mp_data_num = 0

    def read_data(inner_index: int) -> Any:
        element = tuple(pickle.loads(reader.read_one(inner_index)))
        return element

    with open(out_file_path, "wb") as unpacked_writer:
        reserved_part = None
        if start > 0:
            prev_line = read_data(start - 1)
            prev_seq, prev_splitter, _ = prev_line
            if len(prev_splitter) > 0 and prev_splitter[-1] < len(prev_seq):
                reserved_part = [prev_seq[prev_splitter[-1]:], []]  # ww_mask is not needed at here
        for index in tqdm(range(start, end), desc="Unpacking corpus with proc{}".format(proc_id), position=proc_id):
            current_seq = read_data(index)
            unpack_sentences, reserved_part = patch_batch_to_sentences(current_seq, reserved_part)
            for instance in unpack_sentences:
                pickle.dump(instance[0], unpacked_writer)
                mp_data_num += 1

    out_file_path = convert_ffrecord(out_file_path, mp_data_num, logger, remove_old_file=True)
    return out_file_path


# when using cython object in multiprocessing, use spawn instead of fork
@SpawnMultiProcessor
def para_learn(proc_id: int, worker_num: int, 
                   shared_manage: dict, load_state: Optional[Union[str, os.PathLike]] = None,
                   serial_preprocess: Optional[List] = None, logger = None, config = None, cache_dir = None, 
                   parser_args = None, differ_init: Optional[bool] = False):
    # Initialize parser
        from . import misc
        from ..parser.parser import Parser
        from ..learner.metric import MetricManager, default_metrics
        from ..learner.heu_search import default_heu_search
        parser = Parser.from_pretrained(
                parser_args['name_or_path'], **{"logger": logger, "config": parser_args["config"]})
        # Determine random states
        if differ_init:
            proc_seed = config.experiment.seed + proc_id
        else:
            proc_seed = config.experiment.seed
        misc.set_seed(proc_seed)
        # Initialize states
        if load_state is None:
            initial_state = initialize_state(len(parser), "random", **{"logger": logger})
        else:
            initial_state = load_state
        
        metrics= []
        metric_names = config.learner.object
        # Connect shared metrics
        for metric_name in shared_manage:
            address, authkey = shared_manage[metric_name]
            MetricManager.register('metric')
            manager = MetricManager(address=address, authkey=authkey.encode('latin-1'))

            manager.connect()
            metric = manager.metric()
            metrics.append(metric)
            
        # Pre-process serial metrics
        for metric_name in serial_preprocess:
            metric = default_metrics[metric_name](config, cache_dir, **{"logger": logger, "parser": parser,
                                                            "preprocess": config.learner.do_preprocess, 
                                                            **config.learner.object[metric_name]})
            metric.preprocess(initial_state, proc_id, parser=parser)
            metrics.append(metric)
        
        heu_search = config.learner.heuristic_search
        proc_heu_search = default_heu_search[heu_search](config, metrics, logger, initial_state, cache_dir=cache_dir, hybrid=True, proc_id=proc_id)
        best_state, best_energy = proc_heu_search.start()
        print(f'Proc{proc_id} finished. Best energy: {best_energy}. Num of selected: {sum(best_state)}')
        return best_state, best_energy
