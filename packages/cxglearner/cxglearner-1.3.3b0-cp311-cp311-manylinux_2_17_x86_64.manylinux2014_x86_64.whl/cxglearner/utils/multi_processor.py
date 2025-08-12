from multiprocessing import cpu_count, synchronize
from copy import deepcopy
from typing import Callable, Optional, Union, Tuple, Any
from pathos.multiprocessing import ProcessingPool as Pool
import multiprocess.context as ctx

import torch


NOT_COPY = (synchronize.RLock, synchronize.Barrier, synchronize.Lock)


def custom_deepcopy(obj, _memo=None):
    if _memo is None:
        _memo = {}

    obj_id = id(obj)
    if obj_id in _memo:
        return _memo[obj_id]

    if isinstance(obj, NOT_COPY):
        _memo[obj_id] = obj
        return obj

    if isinstance(obj, tuple):
        copied_obj = tuple(custom_deepcopy(item, _memo) for item in obj)
    elif isinstance(obj, list):
        copied_obj = [custom_deepcopy(item, _memo) for item in obj]
    elif isinstance(obj, dict):
        copied_obj = {custom_deepcopy(key, _memo): custom_deepcopy(value, _memo) for key, value in obj.items()}
    else:
        copied_obj = deepcopy(obj, _memo)

    _memo[obj_id] = copied_obj
    return copied_obj


class MultiProcessor(object):
    """
    A decorator class that is used to flexibly implement multiprocessing handling.
    """
    def __init__(self, func: Callable):
        assert callable(func), "The `func` need to be callable, please check."
        self._func = func
        self.cuda = False

    def __call__(self, *args, **kwargs) -> Optional[Union[None, list]]:
        # Check var name
        self._check_varname(self)
        # Check and parse
        worker_num, args, kwargs = self._check_and_get_worker_num(self, *args, **kwargs)
        # Auto for worker_num
        worker_num = self._is_worker_available(*args, worker_num=worker_num)
        # Start
        if self._func.__code__.co_varnames[0] in ['self', 'cls']: proc_index = 1
        else: proc_index = 0
        args = list(args)
        if worker_num == 0:
            args.insert(proc_index, 0)
            args.insert(proc_index + 1, 1)
            return self._func(*args, **kwargs)
        else:
            pool_list, results = [], []
            if not self.cuda:
                ctx._force_start_method("fork")
            else:
                ctx._force_start_method("spawn")
            pool = Pool(worker_num)
            # Need to restart the Pool. Reference -> https://github.com/uqfoundation/pathos/issues/111
            pool.restart()
            # Allocate data
            for i in range(worker_num):
                arg_thread = custom_deepcopy(args)
                arg_thread.insert(proc_index, i)
                arg_thread.insert(proc_index + 1, worker_num)
                if len(kwargs) > 0:
                    result = pool.apipe(self._func, *arg_thread, kwds=kwargs)
                else:
                    result = pool.apipe(self._func, *arg_thread)
                pool_list.append(result)
            pool.close()
            pool.join()
            # Collect Data
            for res in pool_list:
                result_list = res.get()
                if result_list is not None:
                    if isinstance(result_list, list): results.extend(result_list)
                    else: results.append(result_list)
            if not results: return
            else: return results

    @staticmethod
    def _check_varname(cls) -> None:
        var_names = cls._func.__code__.co_varnames
        flag = True
        if var_names[0] == "proc_id" and var_names[1] == "worker_num" and var_names[0] not in ['self', 'cls']: flag = False
        elif var_names[0] in ['self', 'cls'] and var_names[1] == "proc_id" and var_names[2] == "worker_num": flag = False
        if flag: raise Exception("The proc_id and worker_num need to appear in args for `{}`".format(cls._func))

    @staticmethod
    def _check_and_get_worker_num(cls, *args, **kwargs) -> Tuple[int, tuple, dict]:
        """
        Get worker_num in func and check the args.
        :return: Number of workers.
        """
        arg_num, kwarg_num = len(args), len(kwargs)
        func_arg_num = cls._func.__code__.co_argcount
        func_arg_name = cls._func.__code__.co_varnames
        worker_num = 0
        if 'worker_num' in kwargs:
            if 'kwargs' not in func_arg_name and func_arg_num != arg_num + kwarg_num + 1:
                raise Exception('There exists some incorrct args in `{}`, please check.'.format(cls._func))
            worker_num = kwargs['worker_num']
            del kwargs['worker_num']
        else:
            if func_arg_num != arg_num + kwarg_num + 2:
                if func_arg_num == arg_num + kwarg_num and (args[-1] is None or isinstance(args[-1], int)):
                    worker_num = 0 if args[-1] is None else args[-1]
                    args = args[:-1]
                else:
                    raise Exception('There exists some incorrct args in `{}`, please check.'.format(cls._func))
        if worker_num <= 1: worker_num = 0
        return worker_num, args, kwargs

    @staticmethod
    def _is_worker_available(*args, worker_num: int) -> int:
        """
        Check the physical resources and adjust worker_num.
        """
        cpu_num = cpu_count()
        if worker_num > cpu_num:
            if hasattr(args[0], "logger"):
                args[0].logger.warning('The physical machine has only `{}` logical core, but you set worker_num to `{}`. We force the worker_num to be `{}`'.format(cpu_num, worker_num, cpu_num))
            else:
                print('The physical machine has only `{}` logical core, but you set worker_num to `{}`. We force the worker_num to be `{}`'.format(cpu_num, worker_num, cpu_num))
            return cpu_num
        return worker_num


class SpawnMultiProcessor(MultiProcessor):
    """
    A decorator class that is used to flexibly implement multiprocessing handling.
    Note: This module is for Pytorch-CUDA with the context of spawn
    https://github.com/uqfoundation/pathos/issues/250
    """
    def __init__(self, func: Callable):
        super(SpawnMultiProcessor, self).__init__(func)
        assert callable(func), "The `func` need to be callable, please check."
        self._func = func
        self.cuda = True


def mp_allocate_data(data: Any, proc_id: int, worker_num: int) -> Any:
    """
    Par data into sub-parts to be sent for different workers.
    :param data: The data to be segmented.
    :param proc_id: Current worker index
    :param worker_num: The number of workers
    """
    if isinstance(data, int):
        start = proc_id * data // (worker_num)
        end = (proc_id + 1) * data // (worker_num)
        return start, end
    else:
        start = proc_id * len(data) // (worker_num)
        end = (proc_id + 1) * len(data) // (worker_num)
        data = data[start: end]
    return data


def mp_dynamic_device_data(data: Any, proc_id: int, worker_num: int, gpu_ranks: list, numpgpus: int,
                           ratio: Optional[int] = 1.) -> Any:
    """
    Par data into sub-parts to be sent for different workers with multiple devices.
    """
    cuda_devices = len(gpu_ranks) * numpgpus
    # Determine device
    if proc_id >= cuda_devices: device = 'cpu'
    else: device = 'cuda:{}'.format(gpu_ranks[proc_id % len(gpu_ranks)])
    # Determine data
    cuda_workers = min(cuda_devices, worker_num)
    cpu_workers = worker_num - cuda_workers
    scaled_cuda_workers = ratio * cuda_workers
    total_workers = int(scaled_cuda_workers + max(0, worker_num - cuda_workers))
    if isinstance(data, int): data_allocate_num = data
    else: data_allocate_num = len(data)
    cuda_data_allocate_num = int(scaled_cuda_workers * data_allocate_num // (total_workers))
    cpu_data_allocate_num = data_allocate_num - cuda_data_allocate_num
    if device == 'cpu': # CPU
        if cuda_workers <= 0: raise Exception("Multi_processor has an invalid param for `worker_num`.")
        start = (proc_id - cuda_workers) * cpu_data_allocate_num // (cpu_workers) + cuda_data_allocate_num
        end = (proc_id - cuda_workers + 1) * cpu_data_allocate_num // (cpu_workers) + cuda_data_allocate_num
    else: # CUDA
        start = proc_id * cuda_data_allocate_num // (cuda_workers)
        end = (proc_id + 1) * cuda_data_allocate_num // (cuda_workers)
    if isinstance(data, int):
        return start, end, torch.device(device)
    else:
        data = data[start: end]
        return data, torch.device(device)
