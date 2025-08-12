from typing import Union, List, Tuple, Any
from copy import deepcopy
import os

from .base_encoder import BaseEncoder
from .cleaner import Cleaner
from ..utils.utils_encoder import flatten_results, encode_lexical_stoken


class Encoder(BaseEncoder):
    """
    Encoder of the CxGLearner, which is used to tokenize and convert texts into labels of various abstract levels in
    different languages.
    """
    def encode(self, sentence: str, raw: bool = False, need_ids: bool = True, need_mask: bool = False) -> \
            Union[Tuple[Union[dict, list], Union[list, None]], list, dict, None]:
        """
        Converts a single sentence into its various abstraction levels based on the set configuration.
        """
        if not self.is_available(): return None
        # Clean Text
        sentence = Cleaner.clean(sentence, **self.config.encoder.clean_args)
        encoded_levels = dict()
        # Lexical
        tokens = self.tokenize(sentence)
        encoded_levels['lexical'] = encode_lexical_stoken(tokens, self.tokenizer)
        # Other levels
        ww_mask = None
        for pkey in self.parser_mapper:
            encode_kwargs = deepcopy(self.parser_mapper[pkey][0])
            if pkey == self.config.encoder.whole_word_flag: encode_kwargs.update({'need_mask': need_mask})
            res = self.parsers[pkey][1](self.parsers[pkey][0], sentence, tokens, self.lang, **encode_kwargs)
            if res is None: return None
            if pkey == self.config.encoder.whole_word_flag and need_mask: res, ww_mask = res
            if isinstance(sentence, str) and isinstance(res, list):
                res = res[0]
            for rkey in res:
                if rkey in encoded_levels: encoded_levels[rkey][pkey] = res[rkey]
                else: encoded_levels[rkey] = {pkey: res[rkey]}
        if raw:
            if need_mask: return encoded_levels, ww_mask
            else: return encoded_levels
        else:
            # Squeeze
            for pkey in encoded_levels:
                if pkey in ['lexical'] or isinstance(encoded_levels[pkey], list):
                    if need_ids: encoded_levels[pkey] = self.convert_tokens_to_ids(encoded_levels[pkey])
                else:
                    flattend = flatten_results(encoded_levels[pkey], self.parser_mapper, pkey)
                    encoded_levels[pkey] = self.convert_tokens_to_ids(flattend) if need_ids else flattend
            # Re-organize
            results = list(zip(*[encoded_levels[level] for level in self.ava_levels]))
            if need_mask: return results, ww_mask
            else: return results
        
    def encode_batch(self, sentences: list[str], raw: bool = False, need_ids: bool = True, need_mask: bool = False
                     ) -> Any:
        """
        Converts a batch of sentences into their respective abstraction levels.
        """
        if not self.is_available(): return None
        batch_size = len(sentences)
        
        # Clean Text
        sentences = [Cleaner.clean(sentence, **self.config.encoder.clean_args) for sentence in sentences]
        
        # Lexical
        batch_tokens = [self.tokenize(sentence) for sentence in sentences]
        
        # encoded_levels['lexical'] = tokens
        batch_results = dict()
        for pkey in self.parser_mapper:
            encode_kwargs = deepcopy(self.parser_mapper[pkey][0])
            if pkey == self.config.encoder.whole_word_flag: encode_kwargs.update({'need_mask': need_mask})
            batch_results[pkey] = self.parsers[pkey][2](self.parsers[pkey][0], sentences, batch_tokens,
                                                        self.lang, **encode_kwargs)
        
        # format
        raw_results, wwmasks = [], [] if need_mask else None
        for i in range(batch_size):
            encoded_levels = dict()
            encoded_levels['lexical'] = encode_lexical_stoken(batch_tokens[i], self.tokenizer)
            for pkey in self.parser_mapper:
                if isinstance(batch_results[pkey], tuple):
                    batch_res = batch_results[pkey][0][i]
                    mask = batch_results[pkey][1][i]
                    wwmasks.append(mask)
                else:
                    batch_res = batch_results[pkey][i]
                for rkey in batch_res:
                    if rkey in encoded_levels: encoded_levels[rkey][pkey] = batch_res[rkey]
                    else: encoded_levels[rkey] = {pkey: batch_res[rkey]}
            raw_results.append(encoded_levels)
        if raw:
            if need_mask:
                return raw_results, wwmasks
            else:
                return raw_results
        else:
            format_results = []
            for i in range(batch_size):
                encoded_levels = raw_results[i]
                # Squeeze
                for pkey in encoded_levels:
                    if pkey in ['lexical'] or isinstance(encoded_levels[pkey], list):
                        if need_ids: encoded_levels[pkey] = self.convert_tokens_to_ids(encoded_levels[pkey])
                    else:
                        flattend = flatten_results(encoded_levels[pkey], self.parser_mapper, pkey)
                        encoded_levels[pkey] = self.convert_tokens_to_ids(flattend) if need_ids else flattend
                # Re-organize
                results = list(zip(*[encoded_levels[level] for level in self.ava_levels]))
                format_results.append(results)
            if need_mask:
                return format_results, wwmasks
            else:
                return format_results
        
    def encode_files(self, batch_or_path: Union[os.PathLike, list, List[os.PathLike]]) -> list:
        """
        Encodes sentences from a given file or batch of files. Method implementation needs to be provided.
        """
        raise NotImplementedError
