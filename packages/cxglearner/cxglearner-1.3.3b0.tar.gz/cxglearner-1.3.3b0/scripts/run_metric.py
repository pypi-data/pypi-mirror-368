from cxglearner.utils.utils_config import DefaultConfigs
from cxglearner.config.config import Config
from cxglearner.utils.utils_log import init_logger

from cxglearner.parser.parser import Parser
from cxglearner.learner.metric import MDL_Metric


if __name__ == '__main__':
    config = Config(DefaultConfigs.eng)
    logger = init_logger(config)

    parser = Parser(name_or_path="cache/", logger=logger, config=config)
    metric = MDL_Metric(config=config,
                        **{
                            "logger": logger,
                            "parser": parser,
                            "preprocess": config.learner.do_preprocess,
                            **config.learner.object['mdl']
                        })

    candidate_states = [True if i %
                        2 == 0 else False for i, _ in enumerate(parser.cxs_list)]

    metric.preprocess()

    res = metric.compute_metrics(candidate_states)
    print(res)
