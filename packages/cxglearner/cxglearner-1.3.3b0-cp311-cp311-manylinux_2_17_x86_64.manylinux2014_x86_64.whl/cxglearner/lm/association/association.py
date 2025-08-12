import os
from logging import Logger
from typing import Union, Optional, List, Tuple
import traceback

import torch
import numpy as np

from ...config.config import Config
from ...encoder.encoder import Encoder
from ...encoder.tokenizer.tokenizer import Tokenizer
from .lm_model import LMHead
from ...utils.predefine import DEFAULT_ASSOCIA_SIZE
from ...utils.utils_lm import change_point_estimate, nucleus_estimate, estimate_dominate_slots, pack_and_pad_sequence


class Association(object):
    def __init__(self, config: Config, logger: Optional[Logger] = None,
                 device: Union[str, torch.device, int, None] = None, encoder: Optional[Encoder] = None,
                 model_path: Optional[Union[str, os.PathLike]] = None):
        """
        This class represents an association mechanism to compute associations between sequences and candidates using a language model.
        """
        self.config = config
        self.logger = logger
        if encoder is None:
            self.check_components()
        else:
            self.set_encoder(encoder)
        self.lm_head = LMHead(config, logger)
        if model_path is None:
            self.lm_head.from_pretrained(config.lm.output_path)
        else:
            self.lm_head.from_pretrained(model_path)
        self.lm_head.eval()
        if device is not None:
            self.set_device(device)
        else:
            self.device = torch.device('cpu')

    def set_device(self, device: Union[str, torch.device, int]) -> None:
        """
        Sets the computation device.
        """
        try:
            if isinstance(device, str):
                device = torch.device(device)
            elif isinstance(device, int) and torch.cuda.is_available() and device < torch.cuda.device_count():
                # device = torch.device("cuda:{}".format(device))
                device = torch.device("cuda")
            elif not isinstance(device, torch.device):
                raise Exception("The `device` should be `torch.device`, "
                                "`cuda_device_id` or `str`.")
        except:
            if self.logger is not None:
                self.logger.error(traceback.print_exc())
            else:
                print(traceback.print_exc())
            device = torch.device("cpu")
        self.device = device
        self.lm_head.to(self.device)

    def check_components(self):
        """
        Checks the necessary components in the config.
        """
        if "vocab_size" not in self.config.lm.__dict__:
            if self.logger is not None:
                self.logger.error("The `vocab_size` should be in config file, you "
                                  "can use `set_vocab_size` first.")
            raise Exception(
                "The `vocab_size` should be in config file, you can use `set_vocab_size` first.")
        if "tokenizer" not in self.config.lm.__dict__:
            if self.logger is not None:
                self.logger.error("The `tokenizer` should be in config file, you "
                                  "can use `set_tokenizer` first.")
            raise Exception(
                "The `tokenizer` should be in config file, you can use `set_tokenizer` first.")

    @staticmethod
    def set_vocab_size(config: Config, vocab_or_size: Union[dict, Encoder, int]) -> Config:
        """
        Sets the vocabulary size in the configuration.
        """
        if isinstance(vocab_or_size, int):
            config.lm.vocab_size = vocab_or_size
        elif isinstance(vocab_or_size, dict):
            config.lm.vocab_size = len(vocab_or_size)
        elif isinstance(vocab_or_size, Encoder):
            config.lm.vocab_size = len(vocab_or_size.vocab)
        else:
            raise Exception(
                "The `vocab_or_size` can only be `Encoder`, `dict` or `int`.")
        return config

    @staticmethod
    def set_tokenizer(config: Config, tokenizer: Union[Tokenizer]) -> Config:
        """
        Sets the tokenizer in the configuration.
        """
        config.lm.tokenizer = tokenizer
        return config

    def set_encoder(self, encoder: Encoder) -> None:
        """
        Sets the encoder in the configuration and updates related attributes.
        """
        self.config.lm.tokenizer = encoder
        self.config.lm.vocab = encoder.vocab
        self.config.lm.vocab_size = len(encoder.vocab)

    def compute_association(self, sequence: Union[torch.Tensor, list, np.array],
                            candidates: Optional[Union[None, int,
                                                       list, np.array, torch.Tensor]] = None,
                            associa_size: int = DEFAULT_ASSOCIA_SIZE, padding_size: Optional[int] = None,
                            padding_val: int = 0) -> Union[float, list, np.array]:
        """
        Computes the association scores between a given sequence and candidate sequences.
        """
        sequence, no_pad_len = self._pack_and_pad_sequence(
            sequence, padding_size, padding_val)
        n_samples = sequence.shape[0]
        with torch.no_grad():
            lm_hidden = self.lm_head(sequence)
            if no_pad_len is not None:
                lm_hidden = torch.cat([lm_hidden[i, x, :].unsqueeze(
                    0) for i, x in enumerate(no_pad_len)], dim=0)
            else:
                lm_hidden = lm_hidden[:, -1, :]
            lm_hidden_logits = torch.nn.functional.softmax(lm_hidden, dim=1)
        if isinstance(candidates, list) and len(candidates) < 1:
            candidates = None
        if isinstance(candidates, np.ndarray):
            candidates = torch.from_numpy(candidates)
        if candidates is None:
            # Return Candidates according to associa_size
            logits, indexes = lm_hidden_logits.topk(associa_size, 1)
            results = [list(zip(indexes[i].detach().cpu().numpy().tolist(), logits[i].detach().cpu().numpy().tolist()))
                       for i in range(n_samples)]
            if len(results) == 1:
                results = results[0]
            return results
        elif isinstance(candidates, int) or \
                (isinstance(candidates, list) and len(candidates) == 1 and isinstance(candidates[0], int)) \
                or (isinstance(candidates, torch.Tensor) and len(candidates.shape) == 1 and candidates.shape[0] == 1):
            if isinstance(candidates, list):
                candidates = candidates[0]
            results = lm_hidden_logits[:, candidates].detach(
            ).cpu().numpy().tolist()
            if len(results) == 1:
                results = results[0]
            return results
        elif isinstance(candidates, list) or isinstance(candidates, torch.Tensor):
            candidate_length = len(candidates) if isinstance(
                candidates, list) else candidates.shape[0]
            if n_samples != 1 and n_samples != candidate_length:
                if self.logger is not None:
                    self.logger.error("The length of parameter `candidates` should "
                                      "be either 1 or the same as the number of `sequence`. "
                                      "Please check.")
                raise Exception("The length of parameter `candidates` should be either 1 or the same as the "
                                "number of `sequence`. Please check.")
            else:
                if n_samples == 1:
                    results = np.array([lm_hidden_logits[:, idx].detach().cpu().numpy()
                                        for idx in candidates])
                else:
                    results = [lm_hidden_logits[i, idx].detach().cpu().numpy()
                               for i, idx in enumerate(candidates)]
                return results
        else:
            if self.logger is not None:
                self.logger.error("The `candidates` can only be `None`, "
                                  "`torch.Tensor`, `np.array`, `int`, or `list`.")
            raise Exception(
                "The `candidates` can only be `None`, `torch.Tensor`, `np.array`, `int`, or `list`.")

    def compute_candidate(self, sequence: Union[torch.Tensor, list, np.array], mode: Optional[str] = 'dynamic',
                          refer_num: Optional[int] = 50, beam_size: Optional[int] = 20,
                          padding_size: Optional[int] = None, padding_val: Optional[int] = 0, **kwargs
                          ) -> Union[List[dict], Tuple]:
        """
        Computes candidate tokens for a given sequence.
        """
        rpt_debug = kwargs.pop("rpt_debug", False)
        sequence, no_pad_len = self._pack_and_pad_sequence(
            sequence, padding_size, padding_val)
        with torch.no_grad():
            lm_hidden = self.lm_head(sequence)
            if no_pad_len is not None:
                lm_hidden = torch.cat([lm_hidden[i, x, :].unsqueeze(
                    0) for i, x in enumerate(no_pad_len)], dim=0)
            else:
                lm_hidden = lm_hidden[:, -1, :]
            lm_hidden_logits = torch.nn.functional.softmax(lm_hidden, dim=1)
        logits, indexes = lm_hidden_logits.topk(refer_num, 1)
        logits, indexes = logits.detach().cpu(), indexes.detach().cpu()
        if rpt_debug:
            return logits, indexes
        if mode == 'dynamic':
            change_point = [min(change_point_estimate(logits[idx], **kwargs), beam_size)
                            for idx in range(logits.shape[0])]
        elif mode == 'static':
            # TODO: implement the static mode.
            change_point = [0]
        elif mode == 'nucleus':
            if "neucleus_p" in kwargs and "neucleus_k" in kwargs and kwargs["neucleus_p"] and kwargs["neucleus_k"]:
                change_point = [min(nucleus_estimate(logits[idx], **kwargs), beam_size)
                                for idx in range(logits.shape[0])]
            else:
                if self.logger is not None:
                    self.logger.error(
                        "The `neucleus_p` and `neucleus_k` seems to be set incorrectly, it can not be None.")
                raise Exception(
                    "The `neucleus_p` and `neucleus_k` seems to be set incorrectly, it can not be None.")
        else:
            if self.logger is not None:
                self.logger.error(
                    "The `mode` seems to be set incorrectly, it can only be [`dynamic`, `static`].")
            raise Exception(
                "The `mode` seems to be set incorrectly, it can only be [`dynamic`, `static`].")
        logits, indexes = logits.numpy().tolist(), indexes.numpy().tolist()
        candidates = [{indexes[i][index]: logits[i][index]
                       for index in range(cp)} for i, cp in enumerate(change_point)]
        return candidates

    def compute_dominate_slots(self, sequence: Union[torch.Tensor, list, np.array], mode: Optional[str] = 'dynamic',
                               refer_num: Optional[int] = 50, beam_size: Optional[int] = 20,
                               padding_size: Optional[int] = None, padding_val: Optional[int] = 0, **kwargs
                               ) -> List[List[int]]:
        """
        Computes the dominate slots for a given sequence.
        """
        # Check params
        dominate_slots = []
        if mode not in ['dynamic', 'static', 'nucleus']:
            if self.logger is not None:
                self.logger.error(
                    "The `mode` seems to be set incorrectly, it can only be [`dynamic`, `static`, `nucleus`].")
            raise Exception(
                "The `mode` seems to be set incorrectly, it can only be [`dynamic`, `static`, `nucleus`].")
        scaled = kwargs.pop("scaled", True)
        dominate_thresh = kwargs.pop("threshold", 0.8)
        sequence, no_pad_len = self._pack_and_pad_sequence(
            sequence, padding_size, padding_val)
        with torch.no_grad():
            lm_hidden = self.lm_head(sequence)
            lm_hidden_logits = torch.nn.functional.softmax(lm_hidden, dim=2)
        logits, indexes = lm_hidden_logits.topk(refer_num, 2)
        logits, indexes = logits.detach().cpu(), indexes.detach().cpu()
        for batch_id in range(logits.shape[0]):
            instance_logits, instance_indexes = logits[batch_id], indexes[batch_id]
            if no_pad_len is not None:
                pad_len = no_pad_len[batch_id] + 1
            else:
                pad_len = instance_logits.shape[0]
            if mode == 'dynamic':
                change_point = [min(change_point_estimate(instance_logits[idx], **kwargs), beam_size)
                                for idx in range(pad_len)]
            else:  # static mode
                # TODO: implement the static mode.
                change_point = [0]
            # Find dominate
            dominates = estimate_dominate_slots(instance_logits, instance_indexes, change_point, scaled,
                                                dominate_thresh, self.logger)
            dominate_slots.append(dominates)
        return dominate_slots

    def _pack_and_pad_sequence(self, sequence: Union[torch.Tensor, list, np.array], padding_size: Optional[int] = None,
                               padding_val: Optional[int] = 0) -> Tuple[torch.Tensor, Union[List[int], None]]:
        no_pad_len = None
        if isinstance(sequence, list):
            assert len(
                sequence) > 0, "The length of sequence should be more than `0`."
            if isinstance(sequence[0], list):
                no_pad_len = [len(seq) - 1 for seq in sequence]
                padding_size = max(no_pad_len) + 1
            else:
                padding_size = len(sequence)
        sequence = pack_and_pad_sequence(
            sequence, padding_size, padding_val, self.logger).to(self.device)
        if len(sequence.shape) == 1:
            sequence = sequence.unsqueeze(0)
        return sequence, no_pad_len

    def encode_construction(self, cxs: Union[torch.Tensor, list, np.array], padding_size: Optional[int] = None,
                            padding_val: Optional[int] = 0, **kwargs) -> torch.Tensor:
        """
        Encode the input sequence by transforming it and extracting certain hidden states from a language model.
        """
        sequence, no_pad_len = self._pack_and_pad_sequence(
            cxs, padding_size, padding_val)
        return_tensor = None
        with torch.no_grad():
            lm_hidden = self.lm_head(sequence, only_hidden=True)
            for batch_id in range(lm_hidden.shape[0]):
                instance_logits = lm_hidden[batch_id][None]
                if no_pad_len is not None:
                    pad_len = no_pad_len[batch_id]
                else:
                    pad_len = instance_logits.shape[1] - 1
                if return_tensor is None:
                    return_tensor = instance_logits[:, pad_len]
                else:
                    return_tensor = torch.cat(
                        (return_tensor, instance_logits[:, pad_len]))
        return return_tensor.detach().cpu()
