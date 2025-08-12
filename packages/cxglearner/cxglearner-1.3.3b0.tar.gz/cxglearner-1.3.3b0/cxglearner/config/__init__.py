import os
from .config import Config, BaseConfig
from ..utils.utils_config import DefaultModelConfigs


class DefaultConfigs:
    eng: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/configs/eng/eng_config.json"))
    zho: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/configs/zho/zho_config.json"))


__all__ = ["BaseConfig", "Config", "DefaultConfigs", "DefaultModelConfigs"]
