from typing import Union, List
from transformers import AddedToken


class Tokenizer(object):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.vocab = None
        self.sp_model = None
        self.SPECIAL_TOKENS_ATTRIBUTES = []

    def tokenize(self, text: str):
        raise NotImplementedError

    def convert_tokens_to_ids(self, tokens: Union[str, List[str]]) -> Union[int, List[int]]:
        raise NotImplementedError

    def convert_ids_to_tokens(self, ids: Union[int, List[int]], skip_special_tokens: bool = False) -> Union[str, List[str]]:
        raise NotImplementedError

    def add_tokens( self, new_tokens: Union[str, AddedToken, List[Union[str, AddedToken]]], special_tokens: bool = False) -> int:
        raise NotImplementedError

    def is_lexical(self, ids: int) -> bool:
        raise NotImplementedError
