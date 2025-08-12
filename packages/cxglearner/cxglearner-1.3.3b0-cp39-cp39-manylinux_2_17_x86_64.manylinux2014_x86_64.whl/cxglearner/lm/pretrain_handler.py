from logging import Logger
import math
import os

import torch
import torch.multiprocessing as mp
from torch.utils.data import DistributedSampler
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel
from ffrecord.torch import DataLoader

from ..utils.utils_log import init_logger
from ..utils.misc import set_seed, optimizer_to_cuda, allow_tf324torch
from ..utils.utils_lm import collators
from ..utils.file_loader import convert_dataset_suffix, determine_dataset_name
from ..utils.lm_components import str2optimizer, str2scheduler
from .model_factory import build_model, load_model
from .dataloader import dataloaders
from .trainer import trainers


try:
    import wandb
    from ..utils.utils_lm import register_wandb
    WANDB_ = True
except:
    WANDB_ = False


def debug_mode(config):
    set_seed(config.experiment.seed)
    model = build_model(config).cuda()
    train_set = dataloaders[config.lm.data_processor](config, config.lm.dataset_path)
    sampler = DistributedSampler(train_set, num_replicas=1, rank=0, shuffle=True)
    train_loader = DataLoader(train_set, batch_size=config.lm.batch_size, sampler=sampler, collate_fn=collators[config.lm.data_processor], prefetch_factor=None, pin_memory=True)
    for i, batch in enumerate(train_loader):
        batch_sub = [b.cuda(non_blocking=True).unsqueeze(0) if not isinstance(b, list) else [sb.cuda(non_blocking=True).unsqueeze(0) for sb in b] for b in batch]
        loss_mlm, correct_mlm, denominator = model(*batch_sub)
        loss_mlm.backward()
    print('Debug Done.')


def train_and_validate(config, encoder, logger: Logger = None) -> None:
    config.lm.tokenizer = encoder
    config.lm.logger = logger
    config.lm.vocab = encoder.vocab
    config.lm.vocab_size = len(encoder.vocab)
    config.lm.dataset_path = convert_dataset_suffix(determine_dataset_name(config, config.lm.dataset_path, logger), logger)
    if len(config.lm.gpu_ranks) <= 1: config.lm.dist_train = False
    else: config.lm.dist_train = True
    allow_tf324torch(config, logger)
    mp.spawn(worker, nprocs=len(config.lm.gpu_ranks), args=(config, ))
    # debug_mode(config)


def worker(local_rank, config):
    set_seed(config.experiment.seed)
    map_rank = config.lm.gpu_ranks[local_rank]
    torch.cuda.set_device(map_rank)
    torch.cuda.empty_cache()
    logger = init_logger(config)

    dist.init_process_group(backend=config.lm.backend,
                            init_method=config.lm.master_ip,
                            world_size=config.lm.world_size,
                            rank=local_rank)

    model, init_flag = build_and_load_model(config)
    train_set = dataloaders[config.lm.data_processor](config, config.lm.dataset_path)

    config.lm.total_steps = config.lm.epochs_num * math.ceil(len(train_set) / (config.lm.batch_size * config.lm.world_size))

    # Build optimizer.
    param_optimizer = list(model.named_parameters()) if init_flag else list(model[0].named_parameters())
    no_decay = ["bias", "gamma", "beta"]
    optimizer_grouped_parameters = [
        {"params": [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)], "weight_decay": 0.01},
        {"params": [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], "weight_decay": 0.0}
    ]

    if config.lm.optimizer in ["adamw"]:
        custom_optimizer = str2optimizer[config.lm.optimizer](optimizer_grouped_parameters, lr=config.lm.learning_rate, bias_correction=False)
    elif config.lm.optimizer in ["lamb"]:
        custom_optimizer = str2optimizer[config.lm.optimizer](optimizer_grouped_parameters, lr=config.lm.learning_rate, bias_correction=False)
    else:
        custom_optimizer = str2optimizer[config.lm.optimizer](optimizer_grouped_parameters, lr=config.lm.learning_rate, scale_parameter=False, relative_step=False)

    if config.lm.scheduler in ["constant"]:
        custom_scheduler = str2scheduler[config.lm.scheduler](custom_optimizer)
    elif config.lm.scheduler in ["constant_with_warmup"]:
        custom_scheduler = str2scheduler[config.lm.scheduler](custom_optimizer, config.lm.total_steps * config.lm.warmup)
    else:
        custom_scheduler = str2scheduler[config.lm.scheduler](custom_optimizer, config.lm.total_steps * config.lm.warmup, config.lm.total_steps)

    # Initialize hfai parameters
    if init_flag:
        # Build optimizer.
        start_step = 0
        start_epoch = 0
        global_step = 1
    else:
        model, optimizer_params, scheduler_params, start_step, start_epoch, global_step = model
        if logger is not None: logger.info('Restart from global_step = {}, start_epoch = {}, start_step = {}'.format(global_step, start_epoch, start_step)) if local_rank ==0 else None
        else: print('Restart from global_step = {}, start_epoch = {}, start_step = {}'.format(global_step, start_epoch, start_step)) if local_rank ==0 else None
        custom_optimizer.load_state_dict(optimizer_params)
        custom_scheduler.load_state_dict(scheduler_params)
        custom_optimizer = optimizer_to_cuda(custom_optimizer)
        if logger is not None:logger.info("Worker %d is loaded ... " % local_rank)
        else: print("Worker %d is loaded ... " % local_rank, flush=True)

    model = model.cuda()
    optimizer = custom_optimizer
    scheduler = custom_scheduler

    if config.lm.fp16:
        if not init_flag:
            # TODO: ADD support to amp for training (restore).
            if logger is not None: logger.warning('Restore training do not support amp, automatically set config.lm.fp16=False.')
            else: print('Restore training do not support amp, automatically set config.lm.fp16=False.')
            config.lm.fp16 = False
        else:
            try:
                from apex import amp
            except ImportError:
                if logger is not None: logger.error("Please install apex from https://www.github.com/nvidia/apex to use fp16 training.")
                raise ImportError("Please install apex from https://www.github.com/nvidia/apex to use fp16 training.")
            model, optimizer = amp.initialize(model, optimizer, opt_level=config.lm.fp16_opt_level)
            config.lm.amp = amp

    model = DistributedDataParallel(model, device_ids=[map_rank])
    if WANDB_ and local_rank == 0:
        config.lm.wandb_activate = register_wandb(config, logger)
        if config.lm.wandb_activate: wandb.watch(model)

    sampler = DistributedSampler(train_set, num_replicas=config.lm.world_size, rank=local_rank, shuffle=True)
    train_loader = DataLoader(train_set, batch_size=config.lm.batch_size, sampler=sampler, collate_fn=collators[config.lm.data_processor], num_workers=config.lm.loader_num, pin_memory=config.lm.pin_memory)

    if logger is not None: logger.info("Worker %d is training ... " % map_rank)
    else: print("Worker %d is training ... " % map_rank, flush=True)
    trainer = trainers[config.lm.data_processor](config, logger, start_step, start_epoch, global_step)
    trainer.train(config, train_loader, model, optimizer, scheduler, sampler)

    if WANDB_ and local_rank == 0: wandb.finish()
    if local_rank == 0:
        if logger is not None: logger.info("Language model training completed.")
        else: print("Language model training completed.")


def build_and_load_model(config):
    # Build model.
    model = build_model(config)

    # Load or initialize parameters.
    if config.lm.output_path is not None and os.path.exists(config.lm.output_path):
        # Initialize with pretrained model.
        model = load_model(model, config.lm.output_path)
        print('Continue training, loading model ...', flush=True)
        init_flag = False
    else:
        # Initialize with normal distribution.
        if config.lm.deep_init:
            scaled_factor = 1 / math.sqrt(2.0 * config.lm.layers_num)
            for n, p in list(model.named_parameters()):
                if "gamma" not in n and "beta" not in n:
                    if "linear_2.weight" in n or "final_linear.weight" in n:
                        p.data.normal_(0, 0.02 * scaled_factor)
                    elif "linear_2.bias" in n or "final_linear.bias" in n:
                        p.data.zero_()
                    else:
                        p.data.normal_(0, 0.02)
        else:
            for n, p in list(model.named_parameters()):
                if "gamma" not in n and "beta" not in n:
                    p.data.normal_(0, 0.02)
        init_flag = True

    return model, init_flag
