from typing import Optional
from decimal import Decimal
from logging import Logger
from collections import defaultdict
from copy import deepcopy

from ..config.config import Config
from ..utils.utils_extractor import compose_slots, LRUCache, flatten_slots, compute_murmurhash, forbid_detector
from ..lm.association.association import Association
from .pruner import CandidatePruner


class BaseBeamSearch(object):
    def __init__(self, config: Config, association_cache: LRUCache, asso_handler: Association, forbid_ls: list,
                 length_range: list, ava_levels: dict, seed: Optional[int] = 0, logger: Optional[Logger] = None):
        self.candidates = defaultdict(list)
        self.association_cache = association_cache
        self.asso_handler = asso_handler
        self.candidate_length = length_range
        self.ava_levels = ava_levels
        self.forbidden = forbid_ls
        self.seed = seed
        self.logger = logger
        self.accum_op = config.extractor.score_accum
        self.refer_num = config.extractor.ref_num
        self.beam_size = config.extractor.beam_size
        self.candidate_mode = config.extractor.candidate_mode
        self.candidate_kwargs = {
            "neucleus_p": getattr(config.extractor, "neucleus_p", None),
            "neucleus_k": getattr(config.extractor, "neucleus_k", None)
        }
        self.unique_ids = []
        self.init_score = Decimal(1.0)
        self.set_accumlate_operator()

    def recursive_search(self, slots: list, depth: int, sentence: list, ww_masks: list, index: int, length: int,
                         score: Optional[Decimal] = Decimal(1.0), beam_size: Optional[int] = 1) -> None:
        raise NotImplementedError

    def append_candidate(self, slots: list, depth: int, score: Decimal) -> None:
        hash_slots = compute_murmurhash(slots)
        if hash_slots not in self.unique_ids:
            self.candidates[depth].append([slots, score])
            self.unique_ids.append(hash_slots)

    def set_accumlate_operator(self):
        if self.accum_op not in ["add", "multiply"]:
            err_msg = f"The value of `scoreAccum` / `score_accum` cannot be set to `{self.accum_op}`, please check."
            if self.logger is not None:
                self.logger.error(err_msg)
            raise Exception(err_msg)
        if self.accum_op == "add":
            self.init_score = Decimal(0.0)


class HighRecallSearch(BaseBeamSearch):

    def recursive_search(self, slots: list, depth: int, sentence: list, ww_masks: list, index: int, length: int,
                         score: Optional[Decimal] = Decimal(1.0), beam_size: Optional[int] = 1) -> None:
        if depth >= self.candidate_length[-1]:
            self.append_candidate(slots, depth, score)
            return
        index += 1
        if index >= length:
            if depth >= self.candidate_length[0]:
                self.append_candidate(slots, depth, score)
            return
        for level in self.ava_levels:
            nslot = compose_slots(
                sentence, ww_masks[index], self.ava_levels, level)
            deter_slot = nslot[0]
            if deter_slot in self.forbidden:
                if depth >= self.candidate_length[0]:
                    self.append_candidate(slots, depth, score)
                return
            if depth < self.candidate_length[0] - 1:
                score = score * \
                    Decimal(self.asso_handler.compute_association(
                        slots, deter_slot))
                self.recursive_search(slots + nslot if len(nslot) < 2 else slots + [
                                      tuple(nslot)], depth + 1, sentence, ww_masks, index, length, score)
            else:
                cur_slots = flatten_slots(slots)
                hash_seq = compute_murmurhash(cur_slots, self.seed)
                seq_candidates = self.association_cache.get(hash_seq)
                if seq_candidates is None:
                    seq_candidates = self.asso_handler.compute_candidate(cur_slots, self.candidate_mode, self.refer_num,
                                                                         self.beam_size, **self.candidate_kwargs)[0]
                    self.association_cache.set(hash_seq, seq_candidates)
                if deter_slot in seq_candidates.keys():
                    self.recursive_search(slots + nslot if len(nslot) < 2 else slots + [tuple(
                        nslot)], depth + 1, sentence, ww_masks, index, length, score * Decimal(seq_candidates[deter_slot]))
                else:
                    if depth >= self.candidate_length[0]:
                        self.append_candidate(slots, depth, score)


class HighPrecisionSearch(BaseBeamSearch):
    def __init__(self, config: Config, association_cache: LRUCache, asso_handler: Association, forbid_ls: list,
                 length_range: list, ava_levels: dict, seed: Optional[int] = 0):
        super().__init__(config, association_cache, asso_handler,
                         forbid_ls, length_range, ava_levels, seed)
        self.level_prune = CandidatePruner.prune_level_precision

    def recursive_search(self, slots: list, depth: int, sentence: list, ww_masks: list, index: int, length: int,
                         score: Optional[Decimal] = Decimal(1.0), beam_size: Optional[int] = 1) -> None:
        if depth >= self.candidate_length[-1]:
            return
        index += 1
        if index >= length:
            return
        batch_data = []
        for lid, level in enumerate(self.ava_levels):
            nslot = compose_slots(
                sentence, ww_masks[index], self.ava_levels, level)
            deter_slot = nslot[0]
            if lid == 0 and forbid_detector(sentence, ww_masks[index], self.ava_levels, self.forbidden):
                break
            if depth < 1:
                batch_data.append(
                    [nslot if len(nslot) < 2 else [tuple(nslot)], score])
                continue
            if depth < self.candidate_length[0] - 1:
                tempo_slots = [flatten_slots(slot[0]) for slot in slots]
                associate_strength = self.asso_handler.compute_association(
                    tempo_slots, deter_slot)
                if isinstance(associate_strength, float):
                    associate_strength = [associate_strength]
                for i, x in enumerate(slots):
                    batch_data.append([x[0] + nslot if len(nslot) < 2 else x[0] + [tuple(nslot)],
                                       x[1] * Decimal(associate_strength[i]) if self.init_score == "multiply" else
                                       x[1] + Decimal(associate_strength[i])])
                continue
            batch_data.extend(self.compute_strength(slots, deter_slot, nslot))
        if not batch_data:
            return
        if depth < self.candidate_length[0] - 1:
            self.recursive_search(batch_data, depth + 1, sentence,
                                  ww_masks, index, length, score, beam_size=beam_size)
        else:
            pruned_candidates = CandidatePruner.prune(
                batch_data, prune_num=beam_size)
            if not self.level_prune(batch_data, self.ava_levels, depth + 1, self.candidate_length[0]):
                for sl in pruned_candidates:
                    self.append_candidate(sl[0], depth + 1, sl[1])
            self.recursive_search(pruned_candidates, depth + 1, sentence,
                                  ww_masks, index, length, score, beam_size=beam_size)

    def compute_strength(self, slots: list, deter_slot: int, nslot: list) -> list:
        slots = deepcopy(slots)
        need_compute, map_index, need_hash_seq, remove_ids = [], [], [], []
        for i, x in enumerate(slots):
            cur_slot = flatten_slots(x[0])
            hash_seq = compute_murmurhash(cur_slot, self.seed)
            seq_candidates = self.association_cache.get(hash_seq)
            if seq_candidates is None:
                need_compute.append(cur_slot)
                map_index.append(i)
                need_hash_seq.append(hash_seq)
            else:
                if deter_slot in seq_candidates.keys():
                    slots[i][1] = Decimal(seq_candidates[deter_slot]) * x[1] if self.accum_op == "multiply" else \
                        Decimal(seq_candidates[deter_slot]) + x[1]
                    slots[i][0] += nslot if len(nslot) < 2 else tuple(nslot)
                else:
                    slots[i][1] = Decimal(-1.0)
                    remove_ids.append(i)
        if need_compute:
            seq_candidates = self.asso_handler.compute_candidate(need_compute, self.candidate_mode, self.refer_num,
                                                                 self.beam_size, **self.candidate_kwargs)
            for idx, candidate in enumerate(seq_candidates):
                self.association_cache.set(need_hash_seq[idx], candidate)
                if deter_slot in candidate.keys():
                    slots[map_index[idx]][1] = slots[map_index[idx]][1] * Decimal(candidate[deter_slot]) \
                        if self.accum_op == "multiply" else slots[map_index[idx]][1] + Decimal(candidate[deter_slot])
                    slots[map_index[idx]
                          ][0] += nslot if len(nslot) < 2 else tuple(nslot)
                else:
                    slots[map_index[idx]][1] = Decimal(-1.0)
                    remove_ids.append(map_index[idx])
        remove_ids.sort(reverse=True)
        for rid in remove_ids:
            del slots[rid]
        return slots


class TradeOffSearch(HighPrecisionSearch):
    def __init__(self, config: Config, association_cache: LRUCache, asso_handler: Association, forbid_ls: list,
                 length_range: list, ava_levels: dict, seed: Optional[int] = 0):
        super().__init__(config, association_cache, asso_handler,
                         forbid_ls, length_range, ava_levels, seed)
        self.level_prune = CandidatePruner.prune_level_tradeoff
