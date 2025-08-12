from typing import Optional, List
from copy import deepcopy
from logging import Logger

import numpy as np
from numba import jit, prange

from ..config.config import Config
from ..utils.utils_parser import BACKEND, pad_sequence_len


class MatcherBase(object):
    def __init__(self, config: Config, cxs_encoder: dict, vocab_range: dict, logger: Optional[Logger] = None):
        self.config = config
        self.logger = logger
        self.cxs_encoder = cxs_encoder
        self.vocab_range = vocab_range

    def set_encoder(self, cxs_encoder:dict, cxs_added_encoder: Optional[dict] = None):
        if cxs_added_encoder: new_encoder = deepcopy(cxs_encoder)
        else: new_encoder = {**deepcopy(cxs_encoder), ** deepcopy(cxs_added_encoder)}
        self.cxs_encoder = new_encoder

    def match(self, encoded: List, cxs_list: List, wwmask: Optional[List] = None, **kwargs):
        raise NotImplementedError


class SlowMatcher(MatcherBase):
    def match(self, encoded: List, cxs_list: List, wwmask: Optional[List] = None, **kwargs):
        # TODO (gzl): add wwmask case.
        res = []
        cxs_lps = []
        for cx in cxs_list:
            m = len(cx)
            lps = [0]*m
            self.compute_lps(cx, m, lps)
            cxs_lps.append(lps)
    
        for sent in encoded:
            sent_cx = []
            for cid, cx in enumerate(cxs_list):
                sent_res = self.kmp_search(sent, cx, cxs_lps[cid])
                for r in sent_res:
                    sent_cx.append((cid, r[0], r[1]))
            res.append(sent_cx)
        return res
    
    def compute_lps(self, pat, m, lps):
        len = 0
        lps[0] = 0
        i = 1

        while i < m:
            if pat[i] == pat[len]:
                len += 1
                lps[i] = len
                i += 1
            else:
                if len != 0:
                    len = lps[len-1]
                else:
                    lps[i] = 0
                    i += 1
    
    def kmp_search(self, txt, pat, lps):
        def get_type_id(tid):
            for idx, v in enumerate(self.vocab_range.values()):
                if tid in range(v[0], v[1]):
                    return idx
            
        m = len(pat)
        n = len(txt)
        matched_idx = []
        j = 0  # index for pat
        i = 0  # index for txt
        while(n-i) >= (m-j):
            
            if txt[i][get_type_id(pat[j])] == pat[j]:
                i += 1
                j += 1
    
            if j == m:
                matched_idx.append((i-j, i))
                j = lps[j-1]

            elif i <  n and pat[j] != txt[i][get_type_id(pat[j])]:
                if j != 0:
                    j = lps[j-1]
                else:
                    i += 1
        return matched_idx


class MPMatcher(MatcherBase):
    def match(self, encoded: List, cxs_list: List, wwmask: Optional[List] = None, **kwargs):
        # TODO (gzl): add wwmask case.
        pad_encoded_sentences = pad_sequence_len(encoded)
        pad_cxs_list = pad_sequence_len(cxs_list)
        
        @jit(nopython=True, parallel=True)
        def match_with_nb(sentences: np.ndarray, cxs_list: np.ndarray, vocab_range: np.ndarray, results: np.ndarray,
                          min_len: int):
            
            m = sentences.shape[1]
            n = cxs_list.shape[1]
            # Note: assume every sentence have 100 cxs at most.
            for s_id in prange(sentences.shape[0]):
                # print(f'Numba threads number: {numba.get_num_threads()}')
                cnt = 0
                for c_id in prange(cxs_list.shape[0]):
                    sent = sentences[s_id]
                    cx = cxs_list[c_id]
                    
                    match = False
                    end_idx = -1
                    cx_len = -1
                    for i in prange(m - min_len):
                        for j in range(n):
                            if i+j >= m:
                                break
                            if cx[j] == -1: 
                                match=True
                                end_idx = i+j-1
                                cx_len = j
                                break
                            if sent[i+j][0] == -1: 
                                break
                            
                            for idx, r in enumerate(vocab_range):
                                if cx[j] in range(r[0], r[1]):
                                    type_id = idx
                            
                            if sent[i+j][type_id] != cx[j]:
                                break
                        else:
                            end_idx = i+n-1
                            cx_len = n
                            match = True
                        if match:
                            results[s_id][cnt][0] = c_id
                            results[s_id][cnt][1] = end_idx-cx_len+1
                            results[s_id][cnt][2] = end_idx+1
                            cnt += 1
                            match = False
                        if cnt >= results.shape[1]:
                            break
                    if cnt >= results.shape[1]:
                        break
        vocab_range = np.array([list(v) for k, v in self.vocab_range.items()])
        results = np.zeros((pad_encoded_sentences.shape[0], self.config.parser.maximum_cxs_per_sentence, 3), dtype=int)-1
        match_with_nb(pad_encoded_sentences, pad_cxs_list, vocab_range, results, self.config.extractor.min_length) 
        
        out = []
        for result in results:
            r = []
            for c in result:
                if c[0] != -1:
                    r.append(tuple(c))
                else:
                    break
            out.append(r)
                    
        return out


class ACMatcher(MatcherBase):
    def __init__(self, config: Config, cxs_encoder: dict, vocab_range: dict, logger: Optional[Logger] = None):
        super(ACMatcher, self).__init__(config, cxs_encoder, vocab_range, logger)
        try:
            from ..tools.patternpiece.matcher import PatternPiece
        except Exception:
            try:
                # from patternpiece import PatternPiece
                pass
            except Exception:
                err_msg = "It looks like you haven't installed the patternpiece library yet. Please install it first " \
                          "using `pip install patternpiece`."
                if logger is not None:
                    logger.error(err_msg)
                raise ImportError(err_msg)
        # Initialize Matcher
        self.pp = PatternPiece(self.cxs_encoder)

    def match(self, encoded: List, cxs_list: List, wwmask: Optional[List] = None, **kwargs):
        return self.pp.match(encoded, wwmask)


class CUDAMatcher(MatcherBase):
    def match(self, encoded: List[tuple], cxs_list: List, **kwargs):
        # TODO (gzl): To implement CUDA backend
        pass


matcher_backend = {
    BACKEND.cpu : SlowMatcher,
    BACKEND.mp: MPMatcher,
    BACKEND.cuda: CUDAMatcher,
    BACKEND.ac: ACMatcher
}
