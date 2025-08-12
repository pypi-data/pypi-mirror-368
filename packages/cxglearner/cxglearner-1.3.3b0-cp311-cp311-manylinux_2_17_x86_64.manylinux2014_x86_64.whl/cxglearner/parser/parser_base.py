import os
from copy import deepcopy
from typing import Dict, Union, Optional
from logging import Logger

from ..config.config import Config
from ..encoder.encoder import Encoder
from ..utils.utils_parser import VERY_LARGE_INTEGER, BACKEND


class PreTrainedParserBase(object):
    """
    Base class for CxGParsers that Analyze the constructions in the given sentence.
    """
    # Inspired by tokenization procedure in hf/transformers.

    list_files_names: Dict[str, str] = {}  # Required components for the parser
    # Download files from remote spaces
    pretrained_list_files_map: Dict[str, Dict[str, str]] = {}
    backend_mode: str = BACKEND.mp

    def __init__(self, **kwargs):
        """
        Initialize a new instance of the PreTrainedParserBase.
        """
        # inputs and kwargs for saving and re-loading (see ``from_pretrained`` and ``save_pretrained``)
        self.init_inputs = ()
        self.init_kwargs = deepcopy(kwargs)
        self.name_or_path = kwargs.pop("name_or_path", "")
        self.logger = kwargs.pop("logger", None)
        self._encoder_class = kwargs.pop("endoder_class", None)
        model_max_length = kwargs.pop(
            "model_max_length", kwargs.pop("max_len", None))
        self.model_max_length = model_max_length if model_max_length is not None else VERY_LARGE_INTEGER

    def _set_encoder_class(self, config: Config, logger: Optional[Logger] = None):
        """Sets processor class as an attribute."""
        self._encoder_class = Encoder(config, logger)

    def __len__(self) -> int:
        raise NotImplementedError()

    @classmethod
    def from_pretrained(
            cls,
            pretrained_model_name_or_path: Union[str, os.PathLike],
            *init_inputs,
            config: Optional[Config] = None,
            cache_dir: Optional[Union[str, os.PathLike]] = None,
            **kwargs):
        """
        Instantiate the parser from a pretrained model or local directory.
        """
        logger = kwargs.pop("logger", None)
        kwargs["logger"] = logger
        list_files = {**cls.list_files_names}

        resolved_list_files = {}
        unresolved_files = []

        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        is_local = os.path.isdir(pretrained_model_name_or_path)
        if not is_local and not os.path.exists(pretrained_model_name_or_path):
            if logger is not None:
                logger.error(
                    "The current version does not support remote retrieval of parsers.")
            raise Exception(
                "The current version does not support remote retrieval of parsers.")
        else:
            for file_id, file_name in list_files.items():
                if isinstance(file_name, str):
                    file_name = [file_name]
                for sub_file_name in file_name:
                    if os.path.exists(os.path.join(pretrained_model_name_or_path, sub_file_name)):
                        resolved_list_files[file_id] = sub_file_name
                        break
                else:
                    unresolved_files.append(file_id)
                    err_msg = "Can't load parsers from local directory `{}`, due to lack of `{}` file.".format(
                        pretrained_model_name_or_path, file_name)
                    if logger is not None:
                        logger.error(err_msg)
                    raise Exception(err_msg)
        return cls._from_pretrained(
            pretrained_model_name_or_path,
            resolved_list_files,
            *init_inputs,
            cache_dir=cache_dir,
            config=config,
            is_local=is_local,
            **kwargs,
        )

    @classmethod
    def _from_pretrained(
            cls,
            pretrained_model_name_or_path,
            resolved_list_files,
            *init_inputs,
            cache_dir=None,
            config: Config = None,
            is_local=False,
            **kwargs,
    ):
        parser_config_file = resolved_list_files.pop("config_file", None)
        logger = kwargs.pop("logger", None)
        kwargs["logger"] = logger

        if parser_config_file is not None:
            init_config = Config(os.path.join(
                pretrained_model_name_or_path, parser_config_file))
            kwargs["config"] = init_config
        else:
            if config is not None:
                kwargs["config"] = config
            else:
                err_msg = "Cannot find the configuration file required by the parser, please check."
                if logger is not None:
                    logger.error(err_msg)
                raise Exception(err_msg)
        kwargs["name_or_path"] = pretrained_model_name_or_path

        # Instantiate tokenizer.
        try:
            tokenizer = cls(*init_inputs, **kwargs)
        except OSError:
            err_msg = "Unable to load vocabulary from file. " \
                "Please check that the provided vocabulary is accessible and not corrupted."
            if logger is not None:
                logger.error(err_msg)
            raise err_msg

        return tokenizer
