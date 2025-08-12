from typing import Dict, Union, List, Tuple, Any, Optional
from copy import deepcopy

import numpy as np

from ..utils.utils_parser import BACKEND, PARSER_BACKEND_MODE, LIST_FILE_NAMES, PRETRAINED_LIST_FILES_MAP, CYTHON_MATCHERS
from .parser_base import PreTrainedParserBase
from ..utils.utils_cxs import convert_slots_to_str
from ..utils.utils_parser import load_cxs_list
from .matcher import matcher_backend
from ..downloader import Downloader


class ParsedCxs(object):
    def __init__(self, cxs: List[str], starts: List[str], ends: List[str]):
        self.cxs = cxs
        self.starts = starts
        self.ends = ends

    def __len__(self):
        return len(self.cxs)


class PreTrainedParser(PreTrainedParserBase):
    """
    Base class for all parsers.
    """
    def __init__(self, **kwargs):
        super(PreTrainedParser, self).__init__(**kwargs)

        self.added_cxs_encoder: Dict[str, int] = {}
        self.added_cxs_decoder: Dict[int, str] = {}
        self.cxs_encoder: Dict[str, int] = {}
        self.cxs_decoder: Dict[int, str] = {}

        logger = kwargs.pop("logger", None)
        config = kwargs.pop("config", None)
        self.config = config
        self.logger = logger
        if config is None:
            err_msg = "Cannot find the configuration file required by the parser, please check."
            if logger is not None: logger.error(err_msg)
            raise Exception(err_msg)
        mode = config.parser.backend
        self.backend_mode = getattr(BACKEND, mode)
        self.check_backend_mode(mode)

        self.matcher = None

        if self._encoder_class is None:
            self._set_encoder_class(config, logger)
        self.vocab_range = self._encoder_class.vocab_range

    @property
    def need_cuda(self) -> bool:
        """
        Indicates whether CUDA is needed.
        """
        return False

    @property
    def encoder(self):
        """
        Property to get the encoder class.
        """
        return self._encoder_class

    @property
    def cxs_size(self) -> int:
        """
        `int`: Size of the base construction list.
        """
        raise NotImplementedError

    def __len__(self):
        """
        Size of the full vocabulary with the added tokens.
        """
        return self.cxs_size + len(self.added_cxs_encoder)

    def get_added_cxs(self) -> Dict[str, int]:
        """
        Returns the added cxs in the list to index.
        """
        return self.added_cxs_encoder

    def convert_cxs_representation(self, cxs: Union[str]):
        """
        Converts construction representation.
        """
        return cxs

    def check_backend_mode(self, backend: str) -> None:
        """
        Checks if the backend mode is supported.
        """
        if not backend in PARSER_BACKEND_MODE:
            error_msg = "Can't set the backend to `{}`, you can only choose from [{}].".format(
                backend, ', '.join(PARSER_BACKEND_MODE))
            if self.logger is not None: self.logger.error(error_msg)
            raise Exception(error_msg)

    def is_contain(self, cxs: Union[str]):
        """
        Checks if the given construction is contained in the parser's vocabulary.
        """
        return cxs in self.cxs_encoder.keys()

    def add_cxs(self, new_cxs: List[str]) -> int:
        """
        Adds new constructions to the parser's vocabulary.
        """
        new_cxs = [str(cx) for cx in new_cxs]
        cxs_to_add = []

        for cx in new_cxs:
            if not isinstance(cx, str):
                err_msg = "Cx `{}` is not a string but a `{}`.".format(cx, type(cx))
                if self.logger is not None: self.logger.error(err_msg)
                raise TypeError(err_msg)
            if not self.is_contain(cx):
                cxs_to_add.append(self.convert_cxs_representation(cx))

        added_cxs_encoder = {tok: len(self) + i for i, tok in enumerate(cxs_to_add)}
        added_cxs_decoder = {v: k for k, v in added_cxs_encoder.items()}
        self.added_cxs_encoder.update(added_cxs_encoder)
        self.added_cxs_decoder.update(added_cxs_decoder)
        if self.matcher is not None: self.matcher.set_encoder(self.cxs_encoder, self.added_cxs_encoder)
        return len(cxs_to_add)

    def print_constructions(self) -> None:
        """
        Prints all constructions in the parser's vocabulary.
        """
        for cxs in {**self.cxs_encoder, **self.added_cxs_encoder}:
            print(convert_slots_to_str(cxs, encoder=self.encoder, logger=self.logger))

    def output_constructions(self, out_path: str) -> None:
        import pandas as pd
        construction_ls = []
        for cxs in {**self.cxs_encoder, **self.added_cxs_encoder}:
            try:
                construction_ls.append([self.cxs_encoder[cxs],
                    convert_slots_to_str(cxs, encoder=self.encoder, logger=self.logger).replace("Ġ", "")])
            except:
                continue
        df = pd.DataFrame(construction_ls, columns=["ID", "Construction"])
        df.to_csv(out_path, index=False)

    def parse(self, text: Union[str, List[str]], **kwargs) -> Union[ParsedCxs, List[ParsedCxs]]:
        """
        Parses text to extract constructions.
        """
        if isinstance(text, str): text = [text]
        encoded, masks = self._encoder_class.encode_batch(text, raw=False, need_ids=True, need_mask=True)
        parsed = self._parse(encoded, masks, **kwargs)
        return parsed

    def parse_only(self, encoded: Union[List[tuple]], wwmasks: Optional[List] = None, **kwargs) -> Union[ParsedCxs, List[ParsedCxs]]:
        parsed = self._parse(encoded, wwmasks, **kwargs)
        return parsed

    def _parse(self, encoded: List[tuple], wwmasks: Optional[List] = None, **kwargs):
        raise NotImplementedError

    def parse_with_specified_cxs(self, encoded: List[Any], cxs_idx: Optional[np.ndarray] = None, **kwargs):
        """
        Parses text with specified constructions.
        """
        # if isinstance(text, str): text = [text]
        # self.encoded = self._encoder_class.encode_batch(text, raw = False, need_ids=True)
        parsed = self._parse_with_specified_cxs(encoded, cxs_idx, **kwargs)
        return parsed
    
    def _parse_with_specified_cxs(self, encoded: List[tuple], cxs_idx: np.ndarray, **kwargs):
        raise NotImplementedError


class Parser(PreTrainedParser):
    """
    A specialized parser that extends PreTrainedParser for handling unidirectional parsing tasks.
    """
    list_files_names = LIST_FILE_NAMES
    pretrained_list_files_map = PRETRAINED_LIST_FILES_MAP
    cython_matcher = CYTHON_MATCHERS

    def __init__(self, **kwargs):
        """
        Initialize a new instance of the Parser.
        """
        super().__init__(**kwargs)
        self.cxs_file_path = None
        self.need_score = kwargs.pop("need_score", False)
        self.version = kwargs.pop("version", None)
        if self.config.parser.specified_cxs:
            self.cxs_list = kwargs.pop("specifed_cxs", None)
        else:
            # Load construction list.
            cache_dir = kwargs.get("cache_dir", None)
            if not self.name_or_path:
                downloader = Downloader(verbose=True, cache_dir=cache_dir)
                if not self.version:
                    self.name_or_path = downloader.get_cache_data(self.config.experiment.lang)
                else:
                    self.name_or_path = downloader.get_cache_version(self.config.experiment.lang, self.version)
                    
            self.cxs_list, self.cxs_file_path = load_cxs_list(self.name_or_path, self.list_files_names["cxs_file"],
                                                              self._encoder_class, self.logger,
                                                              need_score=self.need_score)
        if self.need_score and isinstance(self.cxs_list, dict):
            # Process New Format with scores (Frequency)
            self.cxs_scores = deepcopy(self.cxs_list)
            self.cxs_list = list(self.cxs_list.keys())
        self.cxs_encoder = {cx: i for i, cx in enumerate(self.cxs_list)}
        self.cxs_decoder = {i: cx for i, cx in enumerate(self.cxs_list)}
        self.matcher = matcher_backend[self.backend_mode](self.config, self.cxs_encoder, self.vocab_range, self.logger)

    @property
    def cxs_size(self) -> int:
        """
        `int`: Size of the base construction list.
        """
        return len(self.cxs_encoder)
            
    def _parse(self, encoded: List[List[Tuple]], wwmasks: Optional[List] = None, **kwargs
               ) -> Union[ParsedCxs, List[ParsedCxs]]:
        res = self.matcher.match(encoded, self.cxs_list, wwmasks)
        return res

    def matcher_clear(self):
        if self.backend_mode in self.cython_matcher:
            self.matcher = None

    def matcher_recover(self):
        if self.backend_mode in self.cython_matcher:
            self.matcher = matcher_backend[self.backend_mode](self.config, self.cxs_encoder,
                                                              self.vocab_range, self.logger)
    
    def _parse_with_specified_cxs(self, encoded: List[tuple], cxs_idx: Optional[np.ndarray] = None, **kwargs):
        if cxs_idx is None: cxs = self.cxs_list
        else: cxs = [self.cxs_list[cid] for cid in cxs_idx]
        res = self.matcher.match(encoded, cxs)
        return res
