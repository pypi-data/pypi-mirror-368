import os
import multiprocessing
from typing import Optional, Union, List, Tuple
from logging import Logger

from ..config.config import Config
from ..utils import misc
from ..parser.parser import Parser
from ..utils.file_loader import create_cache_dir
from .metric import default_metrics, initialize_proxy_class, MetricManager, Metric_Proxy
from .heu_search import default_heu_search
from ..utils.utils_learner import initialize_state, para_learn


class Learner(object):
    def __init__(self, config: Config, parser: Optional[Parser] = None, logger: Optional[Logger] = None,
                 cache_dir: Optional[os.PathLike] = './cache'):
        """
        Initializes the Learner object.
        """
        self.config = config
        self.logger = logger
        self.cache_dir = create_cache_dir(cache_dir, config.experiment.name)
        self.init_method_name = config.learner.init_state_method
        self.heu_search = config.learner.heuristic_search
        # Initialize parser
        self.parser = self.initialize_parser(parser, config.learner.candidate_cxs_path)
        # Preprocess
        self.do_preprocess = config.learner.do_preprocess
        # Initialize metrics
        self.metrics = config.learner.object
        self.hybrid = config.learner.object['mdl']['hybrid']
        if not self.hybrid:
            self.check_and_initialize_metrics()
        # Initialize heuristic search
        self.check_and_impl_heu_search()

    def initialize_parser(self, parser, candidate_path: Union[str, os.PathLike]) -> Parser:
        """
        Initializes the parser for the Learner.
        """
        if parser is not None: return parser
        if candidate_path is None:
            err_msg = "The parameter `candidate_cxs_path` cannot be None, please check."
            if self.logger is not None: self.logger.error(err_msg)
            raise Exception(err_msg)
        parser = Parser.from_pretrained(candidate_path, **{"logger": self.logger, "config": self.config})
        return parser

    def check_and_initialize_metrics(self):
        """
        Checks and initializes the metrics for the learner.
        """
        if self.metrics is None:
            err_msg = "You cannot set the `object` as None. Please check."
            if self.logger is not None: self.logger.error(err_msg)
            raise Exception(err_msg)
        metrics = []
        for metric_name in self.metrics:
            if metric_name not in default_metrics:
                warn_msg = f"The `{metric_name}` seems not include in metric groups, ignored. You can use " \
                           f"`register_metrics` method to register the customized metrics."
                if self.logger is not None: self.logger.warning(warn_msg)
                else: print(warn_msg)
                continue
            else:
                metrics.append(default_metrics[metric_name](self.config, self.cache_dir,
                                                            **{"logger": self.logger, "parser": self.parser,
                                                               "preprocess": self.do_preprocess,
                                                               **self.metrics[metric_name]}))
        if len(self.metrics) < 1:
            err_msg = "At least one object (metric) needs to be set. Please check."
            if self.logger is not None: self.logger.error(err_msg)
            raise Exception(err_msg)
        self.metrics = metrics

    def check_and_impl_heu_search(self):
        """
        Checks and initializes the heuristic search method for the learner.
        """
        if self.heu_search is None:
            err_msg = "You cannot set the `heuristic_search` as None. Please check."
            if self.logger is not None: self.logger.error(err_msg)
            raise Exception(err_msg)
        if self.heu_search not in default_heu_search:
            err_msg = f"The `{self.heu_search}` seems not include in heuristic search groups. You can use " \
                       f"`register_heu_search` method to register the customized heuristic search method."
            if self.logger is not None: self.logger.error(err_msg)
            raise Exception(err_msg)
        self.heu_search = default_heu_search[self.heu_search]

    def learn(self, load_state: Optional[Union[str, os.PathLike]] = None):
        """
        Checks and initializes the heuristic search method for the learner.
        """
        num_workers = self.config.learner.object['mdl']['workerNum']
        serial_preprocess = ['mdl']
        if 'synsem' in self.config.learner.object:
            shared_metrics = ['synsem']
        if self.hybrid and num_workers > 1:
            # TODO: Check for serial_preprocess and shared_metrics
            # Stage I
            manage_info, manage_processes = self.shared_metrics(shared_metrics)
            initial_state = initialize_state(len(self.parser), self.init_method_name, **{"logger": self.logger})
            
            # preprocess
            metric = default_metrics['mdl'](self.config, self.cache_dir,
                                            **{"logger": self.logger, "parser": self.parser,
                                                "preprocess": self.do_preprocess,
                                                "hybrid": self.hybrid,
                                                **self.metrics['mdl']})
            metric.preprocess(initial_state)
            parser_kwargs = self.parser.init_kwargs
            para_learn(manage_info, initial_state, serial_preprocess, self.logger, self.config, self.cache_dir, parser_kwargs, False, worker_num=num_workers)

            # Post procedure
            for process in manage_processes:
                process.terminate()

        else:
            # Set seed
            misc.set_seed(self.config.experiment.seed)
            # Initialize heuristic search
            if load_state is None:
                initial_state = initialize_state(len(self.parser), self.init_method_name, **{"logger": self.logger})
            else:
                initial_state = load_state
            self.heu_search = self.heu_search(self.config, self.metrics, self.logger, initial_state=initial_state,
                                              cache_dir=self.cache_dir)
            # Preprocess
            for metric in self.metrics:
                metric.preprocess(initial_state)
            # Learning
            self.heu_search.start()

    def shared_metrics(self, shared_metrics: List) -> Tuple:
        import time
        # CUDA can only run in spawn mode.
        manage_info, manage_processes = {}, []
        multiprocessing.set_start_method('spawn', force=True)
        for metric_name in shared_metrics:
            met_cls = default_metrics[metric_name]
            global_m = multiprocessing.Manager() # use global manager to store shared variables
            return_dict = global_m.dict()
            args = (return_dict, metric_name, met_cls, self.config, self.cache_dir)
            kwargs = {"logger": self.logger, "preprocess": self.do_preprocess, **self.metrics[metric_name]}            
            manager_process = multiprocessing.Process(target=share_server_manager, args=args, kwargs=kwargs)
            manager_process.start()
            while(True):
                if return_dict.get(metric_name) is not None:
                    break
                time.sleep(10)
            manage_info[metric_name] = [return_dict[metric_name][0], return_dict[metric_name][1]]
            manage_processes.append(manager_process)
        return manage_info, manage_processes


def share_server_manager(*args, **kwargs):
    config = args[3]
    logger = kwargs['logger']
    parser = Parser.from_pretrained(config.learner.candidate_cxs_path, **{"logger": logger, "config": config})
    kwargs['parser'] = parser
    metric_instance = initialize_proxy_class(args[2], args[3:], kwargs)
    metric_instance.preprocess([])

    MetricManager.register('metric', callable = lambda: metric_instance, proxytype = Metric_Proxy)
    manager = MetricManager(address = ('localhost', 50000))
    args[0][args[1]] = [manager.address, manager._authkey.decode('latin-1')]

    manager.get_server().serve_forever()
