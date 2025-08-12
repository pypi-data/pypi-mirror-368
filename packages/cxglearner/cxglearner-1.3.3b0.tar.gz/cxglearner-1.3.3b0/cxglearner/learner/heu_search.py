import os
import abc
import pickle
import copy
import math
import random
import time
import sys
from typing import Optional, List, Union
from logging import Logger
import datetime

from ffrecord import FileWriter
import numpy as np

from ..config.config import Config
from ..utils.file_loader import create_cache_dir
from ..utils.utils_learner import time_string, serialize
from .metric import BaseMetric


try:
    import wandb
    from ..utils.utils_lm import register_wandb
    WANDB_ = True
except:
    WANDB_ = False


class BaseHeuSearch(object):

    __metaclass__ = abc.ABCMeta
    copy_strategy = 'deepcopy'
    user_exit = False
    save_state_on_exit = True

    def __init__(self, config: Config, metrics: List[BaseMetric], logger: Optional[Logger] = None,
                 initial_state: Optional[List] = None, load_state: Optional[Union[str, os.PathLike]] = None,
                 cache_dir: Optional[os.PathLike] = './cache',hybrid=False, proc_id: Optional[int] = -1):
        self.config = config
        self.metrics = metrics
        self.logger = logger
        self.hybrid = hybrid
        if self.hybrid:
            self.proc_id = proc_id
        self.cache_dir = create_cache_dir(cache_dir, config.experiment.name)
        self.weights = config.learner.metric_weight
        self.recorder = config.learner.recorder_path
        if initial_state is not None:
            self.state = self.copy_state(initial_state)
        elif load_state:
            self.load_state(load_state)
        else:
            err_msg = "No valid values supplied for neither initial_state nor load_state"
            if logger is not None: logger.error(err_msg)
            raise ValueError(err_msg)

        if WANDB_: self.wandb_activate = register_wandb(config, logger, module='learner')
        else: self.wandb_activate = False

        # signal.signal(signal.SIGINT, self.set_user_exit)

    def save_state(self, fname=None):
        if not fname:
            date = datetime.datetime.now().strftime("%Y-%m-%dT%Hh%Mm%Ss")
            fname = date + "_score_" + str(self.compute_score()) + ".state"
            fname = os.path.join(self.cache_dir, fname)
        with open(fname, "wb") as fh:
            pickle.dump(self.state, fh)

    def load_state(self, fname=None):
        with open(fname, 'rb') as fh:
            self.state = pickle.load(fh)

    @abc.abstractmethod
    def step(self, T: float) -> float:
        pass

    @abc.abstractmethod
    def compute_score(self) -> float:
        pass

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def default_update(self, step, T, E, acceptance, improvement):
        pass

    def update(self, *args, **kwargs):
        self.default_update(*args, **kwargs)

    def set_user_exit(self, signum, frame):
        self.user_exit = True

    def copy_state(self, state):
        if self.copy_strategy == 'deepcopy':
            return copy.deepcopy(state)
        elif self.copy_strategy == 'slice':
            return state[:]
        elif self.copy_strategy == 'method':
            return state.copy()
        else:
            err_msg = f"No implementation found for the self.copy_strategy `{self.copy_strategy}`"
            if self.logger is not None: self.logger.error(err_msg)
            raise RuntimeError(err_msg)


class SimAnnual(BaseHeuSearch):

    # defaults
    Tmax = 2000.0
    Tmin = 2.5
    steps = 40000
    updates = 2000

    Tfac_High = 0.25
    Tfac_Low = 0.15

    cur_step = 0

    # placeholders
    best_state = None
    best_energy = None
    start_time = None

    def step(self, T: float) -> float:
        initial_energy = self.compute_score()
        tfac_record = len(self.state) * (T - self.Tmin) / (self.Tmax - self.Tmin)
        trans_num_high = math.ceil(tfac_record* self.Tfac_High)
        trans_num_low = math.ceil(tfac_record * self.Tfac_Low)
        # TODO (gzl): use hyperparameters or choose more suitable functions, and apply truncation methods.
        if T < 20:
            trans_num = 1
        else:
            trans_num = random.randint(trans_num_low, trans_num_high + 1)
        trans_states = random.sample(range(len(self.state)), trans_num)
        for state in trans_states: self.state[state] = not self.state[state]
        return self.compute_score() - initial_energy

    def compute_score(self) -> float:
        if self.weights is None: weights = {}
        else: weights = self.weights
        scores, combined_score = {}, 0.0
        for metric in self.metrics:
            scores = {**scores, **metric.compute_metrics(self.state)}
        log_info = {}

        # Compute MDL score
        coverage = scores['coverage']*weights['coverage']
        overlap = scores['overlap']*weights['overlap']
        cost = scores['cost']*weights['cost']
        num_selected_candidates = sum(self.state)
        mdl_score = coverage / overlap + num_selected_candidates * cost
        # Compute SynSem score
        cont_score = scores['cont']*weights['cont']
        
        combined_score = mdl_score + cont_score

        for sco in scores:
            log_info[sco] = scores[sco]
        log_info['num_selected_candidates'] = num_selected_candidates
        log_info['total'] = combined_score
        if self.wandb_activate and WANDB_: wandb.log(log_info, step=self.cur_step)
        return combined_score

    def default_update(self, step, T, E, acceptance, improvement, **kwargs):
        elapsed = time.time() - self.start_time
        if step == 0:
            if not self.hybrid:
                print('\n Temperature        Energy    Accept   Improve     Elapsed   Remaining',
                    file=sys.stderr)
                print('\r{Temp:12.5f}  {Energy:12.2f}                      {Elapsed:s}            '
                    .format(Temp=T,
                            Energy=E,
                            Elapsed=time_string(elapsed)),
                    file=sys.stderr, end="")
                sys.stderr.flush()
            else:
                print('\n Temperature        Energy    Accept   Improve     Elapsed   Remaining   Proc',
                    file=sys.stderr)
                print('\r{Temp:12.5f}  {Energy:12.2f}                      {Elapsed:s}            {Proc:4d}'
                    .format(Temp=T,
                            Energy=E,
                            Elapsed=time_string(elapsed),
                            Proc=self.proc_id),
                    file=sys.stderr, end="")
                sys.stderr.flush()
        else:
            remain = (self.steps - step) * (elapsed / step)
            if not self.hybrid:
                print('\r{Temp:12.5f}  {Energy:12.2f}   {Accept:7.2%}   {Improve:7.2%}  {Elapsed:s}  {Remaining:s}'
                    .format(Temp=T,
                            Energy=E,
                            Accept=acceptance,
                            Improve=improvement,
                            Elapsed=time_string(elapsed),
                            Remaining=time_string(remain)),
                    file=sys.stderr, end="")
                sys.stderr.flush()
            else:
                print('\r{Temp:12.5f}  {Energy:12.2f}   {Accept:7.2%}   {Improve:7.2%}  {Elapsed:s}  {Remaining:s}  {Proc:4d}'
                    .format(Temp=T,
                            Energy=E,
                            Accept=acceptance,
                            Improve=improvement,
                            Elapsed=time_string(elapsed),
                            Remaining=time_string(remain),
                            Proc=self.proc_id),
                    file=sys.stderr, end="")
                sys.stderr.flush()

    def start(self):
        if self.hybrid and self.proc_id == 0:
            wandb_config = self.config.learner.metric_weight
            wandb_config['steps'] = self.steps
            wandb.init(
                project=self.config.learner.wandb_name, 
                config=wandb_config
            )
            self.wandb_activate = True
        self.cur_step = 0
        self.start_time = time.time()
        if self.recorder is not None and self.recorder != "":
            self.recorder = FileWriter(self.recorder, n=self.steps)
        else: self.recorder = None

        # Precompute factor for exponential cooling from Tmax to Tmin
        if self.Tmin <= 0.0:
            err_msg = "Exponential cooling requires a minimum temperature greater than zero."
            if self.logger is not None: self.logger.error(err_msg)
            raise Exception(err_msg)
        t_factor = - math.log(self.Tmax / self.Tmin)

        # Note initial state
        T = self.Tmax
        E = self.compute_score()
        prev_state = self.copy_state(self.state)
        prev_energy = E
        self.best_state = self.copy_state(self.state)
        self.best_energy = E
        trials = accepts = improves = 0
        if self.updates > 0:
            # Initialize updateWavelength
            update_wave_length = self.steps / self.updates
            self.update(self.cur_step, T, E, None, None)
        else:
            err_msg = "Updates requires a minimum num greater than zero."
            if self.logger is not None: self.logger.error(err_msg)
            raise Exception(err_msg)

        # Attempt moves to new states
        while self.cur_step < self.steps and not self.user_exit:
            self.cur_step += 1
            is_best = False
            T = self.Tmax * math.exp(t_factor * self.cur_step / self.steps)
            dE = self.step(T)
            record_state = self.copy_state(self.state)
            if self.wandb_activate and WANDB_: wandb.log({"T": T, "num_states": np.sum(np.array(self.state))}, step=self.cur_step)
            if dE is None:
                E = self.compute_score()
                dE = E - prev_energy
            else:
                E += dE
            trials += 1
            # TODO (gzl): Originally it was T, changed to T/2 but without necessary evidence,
            #  further investigation is needed.
            if dE > 0.0 and math.exp(-dE / (T/2)) < random.random():
                # Restore previous state
                self.state = self.copy_state(prev_state)
                E = prev_energy
            else:
                # Accept new state and compare to best state
                accepts += 1
                if dE < 0.0:
                    improves += 1
                prev_state = self.copy_state(self.state)
                prev_energy = E
                if E < self.best_energy:
                    self.best_state = self.copy_state(self.state)
                    self.best_energy = E
                    is_best = True
            if self.updates > 1:
                if (self.cur_step // update_wave_length) > ((self.cur_step - 1) // update_wave_length):
                    self.update(
                        self.cur_step, T, self.best_energy, accepts / trials, improves / trials)
                    trials = accepts = improves = 0
            # Record
            if not self.hybrid:
                record_info = {"state": record_state, "dE": dE, "E": E, "T": T, "best": is_best}
            else:
                record_info = {"state": record_state, "dE": dE, "E": E, "T": T, "best": is_best, "proc_id": self.proc_id}
            if self.recorder is not None:
                self.recorder.write_one(serialize(record_info))
        self.state = self.copy_state(self.best_state)
        if self.recorder is not None:
            self.recorder.close()
        if self.save_state_on_exit:
            fname = f'final_state_{self.proc_id}.state'
            fname = os.path.join(self.cache_dir, fname)
            self.save_state(fname)

        # Return best state and energy
        return self.best_state, self.best_energy


default_heu_search = {
    "simu_annual": SimAnnual
}


def register_heu_search(logger: Optional[Logger] = None, **search_group):
    for search_name, search_method in search_group.items():
        if search_name in default_heu_search:
            warn_msg = f"The name of the heuristic search to be registered, `{search_name}`, conflicts with a " \
                       f"built-in method and will be ignored."
            if logger is not None: logger.warning(warn_msg)
            else: print(warn_msg)
            continue
        if not isinstance(search_method, BaseHeuSearch):
            warn_msg = f"The desired registration method `{search_name}` does not seem to inherit from the abstract " \
                       f"base class `BaseHeuSearch` and will be ignored. Please check the documentation."
            if logger is not None: logger.warning(warn_msg)
            else: print(warn_msg)
            continue
        default_heu_search[search_name] = search_method
