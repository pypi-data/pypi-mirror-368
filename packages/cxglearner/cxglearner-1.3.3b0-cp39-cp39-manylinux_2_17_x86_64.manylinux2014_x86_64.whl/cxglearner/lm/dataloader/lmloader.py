import random
from .pretrain_loader import PretrainLoader
from typing import Tuple
from ...utils.utils_lm import create_learner_index


def level_selection(src: list, token_index: list, level_probs: list):
    resrc, retoken_index, attr_src = [], [], []
    re_pos = 0
    level_mapping, level_probs = level_probs

    def _get_loc(prob: float) -> int:
        for index, value in enumerate(level_probs):
            if value > prob: return index
        return len(level_probs) - 1

    for index_set in token_index:
        level_prob = random.random()
        level = _get_loc(level_prob)
        if level == level_mapping['lexical']:  # lexical
            retidx = []
            for pos in index_set:
                resrc.append(src[pos][level])
                retidx.append(re_pos)
                re_pos += 1
            retoken_index.append(retidx)
        else:  # other levels
            resrc.append(src[index_set[0]][level])
            retoken_index.append([re_pos])
            re_pos += 1
        attr_src.append(level)
    retoken_index = list(zip(retoken_index, attr_src))
    return resrc, retoken_index


def mask_sequence(src, tokenizer, vocab, mask_index, special_index, glossary_index, whole_word_masking):
    token_index, _ = create_learner_index(src, tokenizer, special_index)
    src, token_index = level_selection(src, token_index)
    random.shuffle(token_index)
    num_to_predict = max(1, int(round(len(src) * 0.15)))
    tgt_mlm = []

    for index_set in token_index:
        if len(tgt_mlm) >= num_to_predict:
            break

        prob = random.random()
        if prob < 0.8: MODE = 'MASK'
        elif prob < 0.9: MODE = 'SUBS'
        else: MODE = 'RES'

        attribute = index_set[1]
        for i in index_set[0]:
            token = src[i]
            tgt_mlm.append((i, token))
            if MODE == 'MASK':
                src[i] = mask_index
            elif MODE == 'SUBS':
                while True:
                    if attribute == 0: rdi = random.randint(1, len(vocab) - 1)
                    else: rdi = random.choice(glossary_index[attribute])
                    if rdi not in special_index:
                        break
                src[i] = rdi
        tgt_mlm = sorted(tgt_mlm, key=lambda x: x[0])
    return src, tgt_mlm


def produce_gpt_sequence(src: list, special_ids: list, pad_ids: int, seq_length: int, level_probs: list) -> Tuple[list, list]:
    src_single, _, wwmask = src
    token_index, _ = create_learner_index(src_single, special_ids, wwmask)
    src_single, _ = level_selection(src_single, token_index, level_probs)
    src_single = src_single + [pad_ids] * (seq_length - len(src_single))
    src = src_single[:-1]
    tgt_mlm = src_single[1:]
    return src, tgt_mlm


class LearnerLMLoader(PretrainLoader):
    def _processor(self, instances):
        batch_data = []
        for instance in instances:
            src, tgt_mlm_seq = mask_sequence(instance, self.tokenizer, self.tokenizer.decoder.keys(), self.mask_ids, self.special_tokenids, self.glossary_ids, self.whole_word_masking)
            src = [self.bos_ids] + src + [self.eos_ids]
            src = src + [self.pad_ids] * (self.seq_length - len(src))
            tgt_mlm = [0] * self.seq_length
            for tgt in tgt_mlm_seq: tgt_mlm[tgt[0]] = tgt[1]
            batch_data.append([src, tgt_mlm])
        return batch_data


class LearnerGPTLoader(PretrainLoader):
    def _processor(self, instances):
        batch_data = []
        for instance in instances:
            src, tgt_lm_seq = produce_gpt_sequence(instance, self.special_tokenids, self.eos_ids if self.pad_ids is None else self.pad_ids, self.seq_length, self.level_probs)
            batch_data.append([src, tgt_lm_seq])
        return batch_data
