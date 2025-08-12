from typing import Optional
from .config.config import Config
from .utils.utils_log import init_logger
from .utils.utils_control import create_save_dir
from .encoder.encoder import Encoder


class Controller(object):
    """
    The core process controller of A will learn the structure in various stages according to the steps, and possess the
    ability to store and resume the process.
    """

    def __init__(self, override_config_path: Optional[str] = None):
        self.config = Config(override_config_path)
        self.logger = init_logger(self.config)
        # Encoder
        self.logger.info('Initializing encoder module ...')
        self.encoder = Encoder(self.config, self.logger)
        # Prepare work space
        self.workspace = create_save_dir(self.config)

    def run(self):
        pass
