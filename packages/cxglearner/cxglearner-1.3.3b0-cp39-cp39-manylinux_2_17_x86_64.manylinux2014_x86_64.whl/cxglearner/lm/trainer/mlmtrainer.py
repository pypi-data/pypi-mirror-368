from .trainer import BaseTrainer
import time


try:
    import wandb
    WANDB_ = True
except:
    WANDB_ = False


class MLMTrainer(BaseTrainer):
    def __init__(self, config, start_step, start_epoch, global_step):
        super(MLMTrainer, self).__init__(config, start_step, start_epoch, global_step)
        self.total_instances = 0.0
        self.total_loss_mlm = 0.0
        self.total_correct_mlm = 0.0
        self.total_denominator = 0.0

    def forward_propagation(self, batch, model):
        loss_info = model(*batch)
        # loss_mlm, correct_mlm, denominator
        loss_mlm, correct_mlm, denominator = loss_info
        loss = loss_mlm
        self.total_loss += loss.item()
        self.total_loss_mlm += loss_mlm.item()
        self.total_correct_mlm += correct_mlm.item()
        self.total_denominator += denominator.item()
        self.total_instances += batch[0].size(0)
        loss = loss / self.accumulation_steps

        return loss

    def report_and_reset_stats(self):
        done_tokens = self.batch_size * self.seq_length * self.report_steps
        if self.dist_train:
            done_tokens *= self.world_size

        token_per_secs = done_tokens / (time.time() - self.start_time)
        loss_mlm = self.total_loss_mlm / self.report_steps
        acc_mlm = self.total_correct_mlm / self.total_denominator

        print("| {:8d}/{:8d} steps"
              "| {:8.2f} tokens/s"
              "| loss {:7.2f}"
              "| loss_mlm: {:3.3f}"
              "| acc_mlm: {:3.3f}".format(
            self.current_step,
            self.total_steps,
            token_per_secs,
            self.total_loss / self.report_steps,
            loss_mlm,
            acc_mlm), flush=True)

        if WANDB_ and self.wandb: wandb.log({'token/s': token_per_secs, 'loss': loss_mlm, 'mlm_acc': acc_mlm}, step=self.current_step)

        self.total_loss, self.total_loss_mlm = 0.0, 0.0
        self.total_correct_mlm, self.total_denominator = 0.0, 0.0
        self.total_instances = 0.0