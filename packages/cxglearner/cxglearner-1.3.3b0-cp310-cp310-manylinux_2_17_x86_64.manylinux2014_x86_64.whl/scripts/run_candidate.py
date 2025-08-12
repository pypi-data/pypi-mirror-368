from cxglearner.encoder.encoder import Encoder
from cxglearner.utils.utils_config import DefaultConfigs
from cxglearner.config.config import Config
from cxglearner.utils.utils_log import init_logger
from cxglearner.extractor.candidate import Candidate


if __name__ == '__main__':
    config = Config(DefaultConfigs.eng)
    logger = init_logger(config)

    encoder = Encoder(config, logger)
    cand_handler = Candidate(config, logger, encoder=encoder)

    cand_handler.build_and_save()
