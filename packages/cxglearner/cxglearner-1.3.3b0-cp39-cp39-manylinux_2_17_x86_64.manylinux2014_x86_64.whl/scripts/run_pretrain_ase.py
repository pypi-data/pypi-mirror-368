from cxglearner.utils.utils_log import init_logger
from cxglearner.config.config import Config
from cxglearner.encoder.encoder import Encoder
from cxglearner.utils.utils_config import DefaultConfigs
from cxglearner.lm.pretrain_handler import train_and_validate


if __name__ == '__main__':
    config = Config(DefaultConfigs.eng)
    logger = init_logger(config)

    encoder = Encoder(config, logger)
    
    train_and_validate(config, encoder, logger)
