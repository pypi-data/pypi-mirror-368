import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

from cxglearner.utils.utils_config import DefaultConfigs
from cxglearner.utils.utils_log import init_logger
from cxglearner.config.config import Config
from cxglearner.learner.learner import Learner


if __name__ == '__main__':
    config = Config(DefaultConfigs.eng)
    logger = init_logger(config)

    learner = Learner(config, logger=logger)
    
    learner.learn()
