import os
from logging import Logger
from typing import List, Union, Tuple
from copy import deepcopy

from ..utils.utils_encoder import default_parsers, is_parser_legal, convert_tokens_to_str
from ..config.config import Config
from .tokenizer.hf_tokenizer import DefaultTokenizer, HFTokenizer

class BaseEncoder(object):
    def __init__(self, config: Config, logger: Logger, need_register: bool = False):
        """
        This class serves as a base class for different encoding strategies, providing a
        structured way to convert text data into a format that is suitable for models.
        """
        self.config = config
        self.logger = logger
        self.parsers = deepcopy(default_parsers)
        self.lang = config.experiment.lang
        self.parser_mapper = {}
        self.ava_levels = ['lexical']
        self.initialized = False
        self.tokenizer = None
        self.vocab = None
        if not need_register: self._level_check()

    def encode(self, sentence: str, raw: bool = False, need_ids: bool = True, need_mask: bool = False) -> \
            Union[Tuple[Union[dict, list], Union[list, None]], list, dict, None]:
        """
        Abstract method to encode a sentence into a format suitable for models.
        """
        raise NotImplementedError

    def encode_files(self, batch_or_path: Union[os.PathLike, list, List[os.PathLike]]) -> list:
        """
        Abstract method to encode content from files.
        """
        raise NotImplementedError

    def tokenize(self, text: str, **kwargs) -> List[str]:
        """
        Tokenize a given text.
        """
        if self.tokenizer is not None: return self.tokenizer.tokenize(text, **kwargs)

    def convert_tokens_to_ids(self, tokens: Union[str, List[str]]) -> Union[int, List[int]]:
        """
        Convert tokens to their corresponding IDs.
        """
        if self.tokenizer is not None: return self.tokenizer.convert_tokens_to_ids(tokens)

    def convert_ids_to_tokens(self, ids: Union[int, List[int]], skip_special_tokens: bool = False) -> Union[str, List[str]]:
        """
        Convert token IDs back to tokens.
        """
        if self.tokenizer is not None: return self.tokenizer.convert_ids_to_tokens(ids, skip_special_tokens)

    def decode_tokens_to_str(self, tokens: Union[str, List[str]]) -> str:
        """
        Convert a list of tokens or a single token to a string.
        """
        return convert_tokens_to_str(tokens)

    def is_lexical(self, ids: int) -> bool:
        """
        Check if a token ID corresponds to a lexical token.
        """
        if self.tokenizer is not None: return self.tokenizer.is_lexical(ids)

    def get_vocab(self):
        """
        Retrieve the vocabulary.
        """
        if self.tokenizer is not None: return self.tokenizer.vocab

    def register_parser(self, **kwargs) -> None:
        """
        Register a parser. This is a placeholder method to be implemented in child classes.
        """
        pass

    def initialize_parser(self) -> None:
        """
        Initialize required parser for encoding after the check is complete.
        """
        
        add_tokens = []
        for p in self.parser_mapper:
            self.vocab_range = {}
            vocab_size = len(self.tokenizer.vocab)
            self.lex_size = vocab_size
            self.vocab_range['lex'] = (0, vocab_size)
            self.parsers[p][0] = self.parsers[p][0](self.config.experiment.lang, self.logger)
            parse_levels = list(self.parser_mapper[p][-1].keys())
            vocab_dict = self.parsers[p][-1]
            for lev in parse_levels:
                if lev in vocab_dict: 
                    self.vocab_range[lev] = (vocab_size, vocab_size+len(vocab_dict[lev]))
                    vocab_size += len(vocab_dict[lev])
                    add_tokens.extend(["<{}>".format(ele) for ele in list(vocab_dict[lev].keys() if isinstance(vocab_dict[lev], list) else vocab_dict[lev])])
                else:
                    self.logger.error("Failed to find the vocabulary for `{}` level that corresponds to the `{}` parser, please check.".format(lev, p))
                    raise Exception("Failed to find the vocabulary for `{}` level that corresponds to the `{}` parser, please check.".format(lev, p))
        self.token_size = vocab_size # the number of all tokens
        # Add vocab to tokenizer
        self.tokenizer.add_tokens(add_tokens, special_tokens=True)
        self.vocab = self.tokenizer.vocab
        # Set flag
        self.initialized = True

    def is_available(self) -> bool:
        """
        Check if the encoder is ready for use.
        """
        if not self.initialized:
            self.logger.error("The encoder module has not been initialized properly, please check.")
        return self.initialized

    def _level_check(self) -> None:
        """
        Check the parsers for all levels
        """
        self.parser_mapper = {}
        # Check lexical
        if 'lexical' not in self.config.encoder.levels:
            self.logger.error("The level of `lexical` should be contained in config file, please check the document.")
            raise Exception("The level of `lexical` should be contained in config file, please check the document.")
        # Check parsers
        levels = self.config.encoder.levels
        for p in levels:
            if p in ['lexical']: continue
            for pkey in levels[p]:
                if pkey == 'default' and 'default_{}'.format(p) in self.parsers:
                    if not is_parser_legal(self.parsers['default_{}'.format(p)]):
                        del self.parsers['default_{}'.format(p)]
                        self.logger.warning("There is no parser named `{}` for `{}` level, ignored. Please ensure it has been registered.".format(pkey, p))
                        continue
                    if 'default_{}'.format(p) not in self.parser_mapper:
                        self.parser_mapper['default_{}'.format(p)] = [{p: True}, {p: levels[p][pkey]}]
                    else:
                        self.parser_mapper[pkey][0].update({p: True})
                        self.parser_mapper['default_{}'.format(p)][1].update({p: levels[p][pkey]})
                else:
                    if pkey not in self.parsers:
                        self.logger.warning("There is no parser named `{}` for `{}` level, ignored. Please ensure it has been registered.".format(pkey, p))
                        continue
                        # raise Exception("There is no parser named `{}` for `{}` level, ignored. Please ensure it has been registered.".format(pkey))
                    if pkey not in self.parser_mapper:
                        self.parser_mapper[pkey] = [{p: True}, {p: levels[p][pkey]}]
                    else:
                        self.parser_mapper[pkey][0].update({p: True})
                        self.parser_mapper[pkey][1].update({p: levels[p][pkey]})
        # Check Lexical
        if hasattr(DefaultTokenizer, levels['lexical']):
            settings = DefaultTokenizer.__dict__[levels['lexical']]
            if len(settings) > 1: self.config.lm.tokenizer = settings[-1]
            self.tokenizer = settings[0](self.config, self.logger)
        else:
            self.tokenizer = HFTokenizer(self.config, self.logger)
        # Check levels
        plevels = set()
        for pkey in self.parser_mapper:
            for plkey in self.parser_mapper[pkey]: plevels.update(plkey)
        plevels = list(plevels)
        for p in levels:
            if p in ['lexical']: continue
            elif p in plevels: self.ava_levels.append(p)
        if len(self.ava_levels) < len(levels):
            self.logger.warning("Some levels may not be resolved due to the lack of parsers, the current levels are: {}".format(self.ava_levels))
        # Initialize Parser
        self.initialize_parser()
