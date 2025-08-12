import os
from typing import Any, Optional
from argparse import Namespace

from .config_experiment import experiment_opts
from .config_encoder import encoder_opts
from .config_lm import lm_opts
from .config_extractor import extractor_opts
from .config_learner import learner_opts
from .config_parser import parser_opts
from ..utils.utils_config import load_hyperparam, load_customparams, argument_check_and_merge, DefaultModelConfigs


class BaseConfig(object):
    """
    This is the template configuration class to store the configuration for each submodule in CxGLearner.
    """
    def __init__(self, parser: Any, desc: str):
        args = parser().parse_args()
        self.load_arguments(args)
        self.desc = desc

    def load_arguments(self, args: Namespace) -> None:
        """
        Load arguments from Namespace.
        """
        for key in args.__dict__:
            self.__dict__[key] = args.__dict__[key]

    def output_help(self) -> None:
        """
        Output the helper message via bash.
        """
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "{}.py".format(self.desc)))
        command = "python {} -h".format(abs_path)
        os.system(command)


class Config(object):
    """
    This is the configuration class to store the configuration of CxGLearner. It is used to
    instantiate the pipeline according to the specified arguments. Instantiating a
    configuration with the defaults will yield the basic procedure that can be used in English.

    Configuration objects for customization can be utilized to override corresponding arguments.
    """
    def __init__(self, override_config_path: Optional[str] = None):
        self.experiment = BaseConfig(experiment_opts, 'config_experiment')
        self.encoder = BaseConfig(encoder_opts, 'config_encoder')
        self.lm = BaseConfig(lm_opts, 'config_lm')
        self.extractor = BaseConfig(extractor_opts, 'config_extractor')
        self.learner = BaseConfig(learner_opts, 'config_learner')
        self.parser = BaseConfig(parser_opts, 'config_parser')
        # Merge parameters
        if override_config_path: self.merge_params(override_config_path)
        # Load LM hyperparameters
        self.load_lmparams()

    def load_lmparams(self) -> None:
        """
        Load hyperparameters from config file for language models.
        """
        if hasattr(self.lm, "model_name") and self.lm.model_name is not None and hasattr(DefaultModelConfigs, self.lm.model_name):
            self.lm.config_path = DefaultModelConfigs.__dict__[self.lm.model_name]
        load_hyperparam(self.lm)

    def merge_params(self, config_path: str) -> None:
        """
        Merge parameters from external config file.
        :param config_path: The path of custom config file.
        """
        custom_args = load_customparams(config_path)
        argument_check_and_merge(custom_args, self)
