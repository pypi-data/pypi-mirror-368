from cxglearner.utils.utils_config import DefaultConfigs
from cxglearner.config.config import Config
from cxglearner.utils.utils_log import init_logger
from cxglearner.encoder.encoder import Encoder
from cxglearner.extractor.candidate import Candidate


if __name__ == '__main__':
    config = Config(DefaultConfigs.eng)
    logger = init_logger(config)

    encoder = Encoder(config, logger)
    cand_handler = Candidate(config, logger, encoder=encoder)
    
    cand_handler.rpt_debug(dataset_path="cache/eng_learner_enron/gpt-enron-split-candidate.pt", model_path="checkpoints/gpt-2-base-enron/pytorch_model.bin", seed=42)
