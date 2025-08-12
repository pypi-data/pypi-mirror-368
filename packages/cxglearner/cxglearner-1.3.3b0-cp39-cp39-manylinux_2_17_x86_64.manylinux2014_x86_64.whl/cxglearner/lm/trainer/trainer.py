import time
from ..model_factory import save_model
import torch.distributed as dist
import torch


class BaseTrainer(object):
    def __init__(self, config, logger, start_step, start_epoch, global_step):
        self.wandb = False
        if hasattr(config.lm, 'wandb_activate') and config.lm.wandb_activate: self.wandb = True
        self.current_step = global_step
        self.total_steps = config.lm.total_steps
        self.epochs = config.lm.epochs_num
        self.logger = logger
        self.clip = config.lm.clip_gradient

        self.accumulation_steps = config.lm.accumulation_steps
        self.report_steps = config.lm.report_steps
        self.save_checkpoint_steps = config.lm.save_checkpoint_steps

        self.output_model_path = config.lm.output_path

        self.start_time = time.time()
        self.total_loss = 0.0

        self.dist_train = config.lm.dist_train
        self.batch_size = config.lm.batch_size
        self.world_size = config.lm.world_size

        self.rank = dist.get_rank()
        self.gpus = dist.get_world_size()

        self.start_step = start_step
        self.start_epoch = start_epoch

    def forward_propagation(self, batch, model):

        raise NotImplementedError

    def report_and_reset_stats(self):

        raise NotImplementedError

    def train(self, config, loader, model, optimizer, scheduler, sampler):
        model.train()
        for epoch in range(self.start_epoch, self.epochs):
            sampler.set_epoch(epoch)
            loader.set_step(self.start_step)

            for step, batch in enumerate(loader):
                step += self.start_step
                self.seq_length = batch[0].size(1)
                batch = [
                    b.cuda(non_blocking=True) if not isinstance(b, list) else [sb.cuda(non_blocking=True) for sb in b]
                    for b in batch]

                loss = self.forward_propagation(batch, model)

                if config.lm.fp16:
                    with config.lm.amp.scale_loss(loss, optimizer) as scaled_loss:
                        scaled_loss.backward()
                else:
                    loss.backward()

                if self.current_step % self.accumulation_steps == 0:
                    optimizer.step()
                    scheduler.step()
                    model.zero_grad()

                if self.rank % torch.cuda.device_count() == 0 and self.current_step % self.report_steps == 0:
                    self.report_and_reset_stats()
                    self.start_time = time.time()

                if self.rank == 0 and self.current_step % self.save_checkpoint_steps == 0:
                    save_model(model, step, epoch, self.current_step, optimizer, scheduler,
                                      self.output_model_path)
                    if self.logger is not None: self.logger.info('|    Reach checkpoint recorder, saving model ...')
                    else: print('|    Reach checkpoint recorder, saving model ...', flush=True)

                self.current_step += 1

            self.start_step = 0