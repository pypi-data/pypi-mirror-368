from typing import Tuple
import torch.nn.functional as F
from packaging import version
from logging import Logger
import traceback
import torch
import math
from typing import Tuple, Optional, List, Union

import cytoolz as cy
from scipy.stats import ks_2samp
import numpy as np

try:
    import ruptures as rpt
    RUPTURES_FLAG = True
except: RUPTURES_FLAG = False

try:
    import wandb
    WANDB_FLAG = True
except: WANDB_FLAG = False

WANDB_LM_CONFIG_LIST = ['dataset_path', 'learning_rate', 'epochs_num', 'batch_size', 'max_seq_length', 'world_size',
                        'tf32', 'torch_compile']

WANDB_LEARNER_CONFIG_LIST = ['heuristic_search', 'init_state_method']

WANDB_CONFIG_LIST = {
    'lm': WANDB_LM_CONFIG_LIST,
    'learner': WANDB_LEARNER_CONFIG_LIST
}


@torch.jit.script
def gelu(x):
    return x * 0.5 * (1.0 + torch.erf(x / math.sqrt(2.0)))


@torch.jit.script
def gelu_fast(x):
    return 0.5 * x * (1.0 + torch.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * torch.pow(x, 3.0))))


def relu(x):
    return F.relu(x)


def linear(x):
    return x


def _silu_python(x):
    """
    See Gaussian Error Linear Units (Hendrycks et al., https://arxiv.org/abs/1606.08415) where the SiLU (Sigmoid Linear
    Unit) was originally introduced and coined, and see Sigmoid-Weighted Linear Units for Neural Network Function
    Approximation in Reinforcement Learning (Elfwing et al., https://arxiv.org/abs/1702.03118) and Swish: a Self-Gated
    Activation Function (Ramachandran et al., https://arxiv.org/abs/1710.05941v1) where the SiLU was experimented with
    later.
    """
    return x * torch.sigmoid(x)


if version.parse(torch.__version__) < version.parse("1.7"):
    silu = _silu_python
else:
    silu = F.silu


def register_wandb(config, logger: Logger = None, module: str = 'lm'):
    wandb_name = config.__dict__[module].wandb_name
    if wandb_name is None or wandb_name == "":
        if logger is not None:
            logger.warning('Current experiment will not be recorded in wandb, config.wandb_name = None.')
        else:
            print('Current experiment will not be recorded in wandb, config.wandb_name = None.')
        return False
    wandb.init(
        project=wandb_name,
        config=filter_params(config, module)
    )
    return True


def filter_params(config, module: str = 'lm'):
    args = {}
    args_dict = config.__dict__
    for co in WANDB_CONFIG_LIST[module]:
        if co not in args_dict :continue
        args[co] = config.__dict__[co]
    return args


def par_wwindex_seq(index_seq: list, threshold: int) -> Tuple[list, list]:
    sel_seq, par_idx = [], 0
    for idx, seq in enumerate(index_seq):
        if seq[-1] < threshold:
            sel_seq.append(seq)
            par_idx += 1
        elif seq[0] >= threshold:
            break
        else:
            par_former = [seq[0], threshold-1]
            if par_former[0] != par_former[1]:
                sel_seq.append([seq[0], threshold-1])
            index_seq[idx][0] = threshold
            if index_seq[idx][0] == index_seq[idx][1]:
                par_idx += 1
    rest_seq = [[seq[0] - threshold, seq[1] - threshold]
                for seq in index_seq[par_idx:]]
    return sel_seq, rest_seq


def collate_fn_gpt(batch):
    src = [item[0] for item in batch]
    tgt_mlm = [item[1] for item in batch]
    return [
        torch.LongTensor(src),
        torch.LongTensor(tgt_mlm),
    ]


activate_fns = {"gelu": gelu, "gelu_fast": gelu_fast, "relu": relu, "silu": silu, "linear": linear}
collators = {'base': collate_fn_gpt, 'gpt': collate_fn_gpt}


def rescale_level_probs(probs: dict, logger: Logger = None, eps: float = 1e-8) -> dict:
    """
    Automatic Adjust probs for different levels in LM loader.
    """
    prob_counter = 0.
    for p in probs: prob_counter += probs[p]
    if abs(prob_counter - 1.) <= eps: return probs
    if abs(prob_counter - 0.) <= eps:
        if logger is not None: logger.error("The set probabilities for the levels cannot all be zero. Please check.")
        else: print("The set probabilities for the levels cannot all be zero. Please check.")
        raise Exception("The set probabilities for the levels cannot all be zero. Please check.")
    scale_factor = 1 / prob_counter
    for p in probs: probs[p] = probs[p] * scale_factor
    logger.warning("The level probability has been adaptively modified, resulting in: {}".format(probs))
    return probs


def create_learner_index(src: list, special_index: list, wwmask: list) -> Tuple[list, list]:
    tokens_index, whole_word, i = [], {}, 0
    for mask in wwmask: whole_word[mask[0]] = [_ for _ in range(mask[0], mask[1] + 1)]
    while i < len(src):
        if src[i] in special_index:
            i += 1
            continue
        flag = i in whole_word
        if flag:
            tokens_index.append(whole_word[i])
            i += len(whole_word[i])
        else:
            tokens_index.append([i])
            i += 1
    return tokens_index, src


def pack_sequence(sequence: Union[torch.Tensor, list, np.array], logger: Optional[Logger] = None) -> torch.Tensor:
    if isinstance(sequence, list):
        sequence = torch.from_numpy(np.array(sequence)).to(torch.int64)
    elif isinstance(sequence, np.ndarray):
        sequence = torch.from_numpy(sequence).to(torch.int64)
    elif not isinstance(sequence, torch.Tensor):
        if logger is not None: logger.error(
            "The `sequence` can only be `torch.Tensor`, `np.array` or `list`.")
        raise Exception("The `sequence` can only be `torch.Tensor`, `np.array` or `list`.")
    return sequence


def pack_and_pad_sequence(sequence: Union[torch.Tensor, list, np.array], padding_size: int, padding_val: int = 0,
                          logger: Optional[Logger] = None) -> torch.Tensor:
    def _padding(inputs: list, padding_size: int, pad_val: int = 0) -> np.ndarray:
        doc = np.array([
            np.pad(x[0:padding_size], (0, padding_size - len(x[0:padding_size])),
                   'constant', constant_values=pad_val)
            for x in inputs
        ]).astype('int64')
        return doc

    if isinstance(sequence, list):
        if not isinstance(sequence[0], int): sequence = _padding(sequence, padding_size, padding_val)
    sequence = pack_sequence(sequence, logger)
    return sequence


def nucleus_estimate(logits: torch.Tensor, neucleus_k: int, neucleus_p: float) -> int:
    neucleus = logits[:neucleus_k]
    neucleus /= neucleus.sum(dim=-1, keepdim=True)
    accum_probs = 0.0
    for ind in range(neucleus_k):
        accum_probs += neucleus[ind]
        if accum_probs >= neucleus_p:
            return ind
    return neucleus_k - 1


def change_point_estimate(logits: torch.Tensor, estimate_method: Optional[str] = 'rpt', kernel: Optional[str] = 'rbf',
                          penalty: Optional[float] = 3, logger: Optional[Logger] = None) -> int:
    if estimate_method not in ['rpt', 'ks']:
        if logger is not None:
            logger.error("The `estimate_method` seems to be set incorrectly, it can only be [`rpt`, `ks`].")
        raise Exception("The `estimate_method` seems to be set incorrectly, it can only be [`rpt`, `ks`].")

    # KS estimate
    def find_ks_point(data: list):
        n = len(data)
        max_d = -1
        turning_point = None
        for i in range(2, n - 1):
            x = data[:i]
            y = data[i:]
            d, _ = ks_2samp(x, y)
            if d > max_d:
                max_d = d
                turning_point = i
        return turning_point

    if estimate_method == 'rpt':
        if not RUPTURES_FLAG:
            if logger is not None:
                logger.error("It looks like you haven't installed the ruptures library yet. Please install it first \
                using `pip install ruptures`.")
            raise Exception("It looks like you haven't installed the ruptures library yet. Please install it first "
                            "using `pip install ruptures`.")
        try:
            detector = rpt.Pelt(model=kernel).fit(logits.numpy())
            change_points = detector.predict(pen=penalty)
            if len(change_points) > 0: change_point = change_points[0]
            else: change_point = -1
        except Exception as e:
            if logger is not None: logger.error(e)
            traceback.print_exc()
            raise Exception(e)
    elif estimate_method == 'ks':
        change_point = find_ks_point(logits.numpy().tolist())
        if change_point is None: change_point = -1
    else: change_point = -1
    return change_point


def estimate_dominate_slots(logits: torch.Tensor, indexes: torch.Tensor, change_points: List[int], scaled: bool = True,
                            dominate_thresh: float = 0.8, logger: Optional[Logger] = None, eps: float = 1e-8
                            ) -> List:
    dominates = []
    for slot_index in range(len(change_points)):
        try:
            logit, index = logits[slot_index][:change_points[slot_index]], \
                indexes[slot_index][:change_points[slot_index]]
            if scaled: logit = logit / (logit.sum() + eps)
            paired = dict(zip(index.numpy().tolist(), logit.numpy().tolist()))
            dominate = list(cy.valfilter(lambda x: x >= dominate_thresh, paired).keys())
        except Exception as e:
            if logger is not None: logger.error(e)
            else: print(e)
            dominate = []
        dominates.append(dominate)
    return dominates


def softmax_one(x: torch.Tensor, dim=None):
    # Orig Impl in https://github.com/kyegomez/AttentionIsOFFByOne
    # But we can concat a zero instead
    x = x - x.max(dim=dim, keepdim=True).values
    # compute exponentials
    exp_x = torch.exp(x)
    # compute softmax values and add on in the denominator
    return exp_x / (1 + exp_x.sum(dim=dim, keepdim=True))
