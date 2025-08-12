from typing import Union, List
from logging import Logger
from copy import deepcopy
import os

from transformers import AutoTokenizer, AddedToken
from .tokenizer import Tokenizer

class HFTokenizer(Tokenizer):
    def __init__(self, config, logger: Logger):
        super(HFTokenizer, self).__init__(config, logger)
        try:
            self.hf_tokenizer = AutoTokenizer.from_pretrained(config.lm.tokenizer, use_fast=False)
            self.vocab = self.hf_tokenizer.encoder
            self.SPECIAL_TOKENS_ATTRIBUTES = self.hf_tokenizer.SPECIAL_TOKENS_ATTRIBUTES
            self.update_special_token()
            #self.pad_token_id = self.hf_tokenizer.pad_token_id
        except:
            import traceback
            self.logger.error(traceback.print_exc())
            raise Exception(traceback.print_exc())

    def tokenize(self, text: str):
        return self.hf_tokenizer.tokenize(text)

    def convert_tokens_to_ids(self, tokens: Union[str, List[str]]) -> Union[int, List[int]]:
        return self.hf_tokenizer.convert_tokens_to_ids(tokens)

    def convert_ids_to_tokens(self, ids: Union[int, List[int]], skip_special_tokens: bool = False) -> Union[str, List[str]]:
        return self.hf_tokenizer.convert_ids_to_tokens(ids, skip_special_tokens)

    def update_special_token(self) -> None:
        for key in self.SPECIAL_TOKENS_ATTRIBUTES:
            if '_' + key not in self.hf_tokenizer.__dict__: continue
            if not self.hf_tokenizer.__dict__['_' + key]: continue
            ckey = self.hf_tokenizer.__dict__['_' + key].content
            self.__dict__[key + '_id'] = self.hf_tokenizer.encoder[ckey] if ckey in self.hf_tokenizer.encoder else None

    def add_tokens( self, new_tokens: Union[str, AddedToken, List[Union[str, AddedToken]]], special_tokens: bool = False) -> int:
        result = self.hf_tokenizer.add_tokens(new_tokens, special_tokens)
        self.vocab = deepcopy(self.hf_tokenizer.encoder)
        self.vocab.update(self.hf_tokenizer.added_tokens_encoder)
        return result

    def is_lexical(self, ids: int) -> bool:
        return ids not in self.hf_tokenizer.added_tokens_decoder


class DefaultTokenizer:
    gpt: str = [HFTokenizer, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/models/GPT_Base/"))]
