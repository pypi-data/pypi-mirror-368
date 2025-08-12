import os
import numpy as np
import pickle
from typing import List, Union, Optional, Dict
from logging import Logger
import traceback

from .predefine import CXS_LINK_SYMBOL


VERY_LARGE_INTEGER = int(1e30)


class BACKEND:
    cpu: str = "cpu-normal"
    mp: str = "cpu-mp"
    cuda: str = "cuda"
    ac: str = "cpu-mpac"

PARSER_BACKEND_MODE = [mode for mode in BACKEND.__dict__]


LIST_FILE_NAMES = {"cxs_file": ["constructions.txt", "constructions.pt", "constructions.ffr"]}
CYTHON_MATCHERS = [BACKEND.ac]
PRETRAINED_LIST_FILES_MAP = {}  # For remoting resources


def load_cxs_list(path: Union[str, os.PathLike], file_list: List[str], encoder: Optional = None, # type: ignore
                  logger: Optional[Logger] = None, link_sym: str = CXS_LINK_SYMBOL, return_path: Optional[bool] = True,
                  need_score: bool = False) -> List:
    # Get path of cxs list
    for cxs_file_name in file_list:
        if os.path.exists(os.path.join(path, cxs_file_name)):
            cxs_file_path = os.path.join(path, cxs_file_name)
            break
    else:
        err_msg = f"Can't find a cxs list file at path '{path}'. To load the cxs list from a pretrained" \
                    " model use `parser = SlowParser.from_pretrained(PRETRAINED_MODEL_NAME_OR_PATH)`"
        if logger is not None: logger.error(err_msg)
        traceback.print_exc()
        raise ValueError(err_msg)
    # Load data
    suffix = cxs_file_path.split('.')[-1]
    try:
        if suffix in ['txt']:
            ret = encode_str_to_cxs(cxs_file_path, encoder, link_sym)
        elif suffix in ["pt"]:
            ret = encode_pt_to_cxs(cxs_file_path)
        elif suffix in ["ffr"]:
            ret = encode_ffr_to_cxs(cxs_file_path)
        else:
            err_msg = f"The list file type cannot be parsed. Please check."
            if logger is not None: logger.error(err_msg)
            raise Exception(err_msg)
        # Resolve conflicts
        ret_set = list(set(ret))
        if need_score:
            score_ret = {cxs: ret[cxs] for cxs in ret_set}
            ret = score_ret
        else:
            ret = ret_set
        if return_path:
            ret = (ret, cxs_file_path)
        return ret
    except Exception as e:
        if logger is not None: logger.error(e)
        traceback.print_exc()
        raise Exception(e)


def encode_str_to_cxs(cxs_list_path: Union[str, os.PathLike], encoder, link_sym: str) -> List:
    encoded_cxs = []
    with open(cxs_list_path, "r") as f:
        cxs_list = f.read().splitlines()
    for cx in cxs_list:
        slots = cx.split(link_sym)
        encoded_repr = [encoder.convert_tokens_to_ids(slot) for slot in slots]
        encoded_cxs.append(encoded_repr)
    return encoded_cxs


def encode_pt_to_cxs(cxs_list_path: Union[str, os.PathLike]) -> Dict:
    from .utils_extractor import flatten_slots
    encoded_cxs = []
    scores = []
    idx = 0
    dataset_reader = open(cxs_list_path, "rb")
    try:
        while True:
            cxs = pickle.load(dataset_reader)
            if isinstance(cxs, tuple) and len(cxs) == 2 and isinstance(cxs[-1], float):
                # New version
                enc_info = tuple(flatten_slots(cxs[0]))
                score = cxs[1]
            else:
                # Old version
                enc_info = tuple(flatten_slots(cxs))
                score = idx
            encoded_cxs.append(enc_info)
            scores.append(score)
            idx += 1
    except EOFError:
        pass
    dataset_reader.close()
    return dict(zip(encoded_cxs, scores))


def encode_ffr_to_cxs(cxs_list_path: Union[str, os.PathLike]) -> Dict:
    from .file_loader import read_ffrecord_file
    from .utils_cxs import flatten_slots
    encoded_cxs, scores = [], []
    idx = 0
    cxs_list = read_ffrecord_file(cxs_list_path)
    for cxs in cxs_list:
        if isinstance(cxs, tuple) and len(cxs) == 2 and (isinstance(cxs[-1], float) or isinstance(cxs[-1], int)):
            # New version
            enc_info = tuple(flatten_slots(cxs[0]))
            score = cxs[1]
        else:
            # Old version
            enc_info = tuple(flatten_slots(cxs))
            score = idx
        encoded_cxs.append(enc_info)
        scores.append(score)
        idx += 1
    return dict(zip(encoded_cxs, scores))

def pad_sequence_len(input: List) -> np.ndarray:
    """
    Pad every sentence in the input to the max length of sentences in the list. 
    """
    input = [np.array(line) for line in input]
    lens = np.array([len(s) for s in input])
    mask = lens[:, None] > np.arange(lens.max())
    
    out_shape = mask.shape + (input[0].shape[1], ) if len(input[0].shape) > 1 else mask.shape
    out = np.zeros(out_shape, dtype = int) - 1
    out[mask] = np.concatenate(input)
    return out
