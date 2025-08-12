from cxglearner.utils.utils_log import init_logger
from cxglearner.config.config import Config
from cxglearner.encoder.encoder import Encoder
from cxglearner.encoder.dataset import Dataset
from cxglearner.utils.utils_config import DefaultConfigs


if __name__ == '__main__':
    config = Config(DefaultConfigs.eng)
    logger = init_logger(config)

    encoder = Encoder(config, logger)
    dataset = Dataset(config, logger, encoder)

    dataset.build_and_save()
