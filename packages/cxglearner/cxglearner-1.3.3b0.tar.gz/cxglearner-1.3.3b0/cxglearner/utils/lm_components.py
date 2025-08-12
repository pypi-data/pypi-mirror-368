import math
from typing import Callable, Iterable, Tuple

import torch
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LambdaLR


def get_constant_schedule(optimizer: Optimizer, last_epoch: int = -1):
    """
    Create a schedule with a constant learning rate, using the learning rate set in optimizer.
    Args:
        optimizer (:class:`~torch.optim.Optimizer`):
            The optimizer for which to schedule the learning rate.
        last_epoch (:obj:`int`, `optional`, defaults to -1):
            The index of the last epoch when resuming training.
    Return:
        :obj:`torch.optim.lr_scheduler.LambdaLR` with the appropriate schedule.
    """
    return LambdaLR(optimizer, lambda _: 1, last_epoch=last_epoch)


def get_constant_schedule_with_warmup(optimizer: Optimizer, num_warmup_steps: int, last_epoch: int = -1):
    """
    Create a schedule with a constant learning rate preceded by a warmup period during which the learning rate
    increases linearly between 0 and the initial lr set in the optimizer.
    Args:
        optimizer (:class:`~torch.optim.Optimizer`):
            The optimizer for which to schedule the learning rate.
        num_warmup_steps (:obj:`int`):
            The number of steps for the warmup phase.
        last_epoch (:obj:`int`, `optional`, defaults to -1):
            The index of the last epoch when resuming training.
    Return:
        :obj:`torch.optim.lr_scheduler.LambdaLR` with the appropriate schedule.
    """

    def lr_lambda(current_step: int):
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1.0, num_warmup_steps))
        return 1.0

    return LambdaLR(optimizer, lr_lambda, last_epoch=last_epoch)


def get_linear_schedule_with_warmup(optimizer, num_warmup_steps, num_training_steps, last_epoch=-1):
    """
    Create a schedule with a learning rate that decreases linearly from the initial lr set in the optimizer to 0, after
    a warmup period during which it increases linearly from 0 to the initial lr set in the optimizer.
    Args:
        optimizer (:class:`~torch.optim.Optimizer`):
            The optimizer for which to schedule the learning rate.
        num_warmup_steps (:obj:`int`):
            The number of steps for the warmup phase.
        num_training_steps (:obj:`int`):
            The total number of training steps.
        last_epoch (:obj:`int`, `optional`, defaults to -1):
            The index of the last epoch when resuming training.
    Return:
        :obj:`torch.optim.lr_scheduler.LambdaLR` with the appropriate schedule.
    """

    def lr_lambda(current_step: int):
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        return max(
            0.0, float(num_training_steps - current_step) / float(max(1, num_training_steps - num_warmup_steps))
        )

    return LambdaLR(optimizer, lr_lambda, last_epoch)


def get_cosine_schedule_with_warmup(
    optimizer: Optimizer, num_warmup_steps: int, num_training_steps: int, num_cycles: float = 0.5, last_epoch: int = -1
):
    """
    Create a schedule with a learning rate that decreases following the values of the cosine function between the
    initial lr set in the optimizer to 0, after a warmup period during which it increases linearly between 0 and the
    initial lr set in the optimizer.
    Args:
        optimizer (:class:`~torch.optim.Optimizer`):
            The optimizer for which to schedule the learning rate.
        num_warmup_steps (:obj:`int`):
            The number of steps for the warmup phase.
        num_training_steps (:obj:`int`):
            The total number of training steps.
        num_cycles (:obj:`float`, `optional`, defaults to 0.5):
            The number of waves in the cosine schedule (the defaults is to just decrease from the max value to 0
            following a half-cosine).
        last_epoch (:obj:`int`, `optional`, defaults to -1):
            The index of the last epoch when resuming training.
    Return:
        :obj:`torch.optim.lr_scheduler.LambdaLR` with the appropriate schedule.
    """

    def lr_lambda(current_step):
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        progress = float(current_step - num_warmup_steps) / float(max(1, num_training_steps - num_warmup_steps))
        return max(0.0, 0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * progress)))

    return LambdaLR(optimizer, lr_lambda, last_epoch)


def get_cosine_with_hard_restarts_schedule_with_warmup(
    optimizer: Optimizer, num_warmup_steps: int, num_training_steps: int, num_cycles: int = 1, last_epoch: int = -1
):
    """
    Create a schedule with a learning rate that decreases following the values of the cosine function between the
    initial lr set in the optimizer to 0, with several hard restarts, after a warmup period during which it increases
    linearly between 0 and the initial lr set in the optimizer.
    Args:
        optimizer (:class:`~torch.optim.Optimizer`):
            The optimizer for which to schedule the learning rate.
        num_warmup_steps (:obj:`int`):
            The number of steps for the warmup phase.
        num_training_steps (:obj:`int`):
            The total number of training steps.
        num_cycles (:obj:`int`, `optional`, defaults to 1):
            The number of hard restarts to use.
        last_epoch (:obj:`int`, `optional`, defaults to -1):
            The index of the last epoch when resuming training.
    Return:
        :obj:`torch.optim.lr_scheduler.LambdaLR` with the appropriate schedule.
    """

    def lr_lambda(current_step):
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        progress = float(current_step - num_warmup_steps) / float(max(1, num_training_steps - num_warmup_steps))
        if progress >= 1.0:
            return 0.0
        return max(0.0, 0.5 * (1.0 + math.cos(math.pi * ((float(num_cycles) * progress) % 1.0))))

    return LambdaLR(optimizer, lr_lambda, last_epoch)


def get_polynomial_decay_schedule_with_warmup(
    optimizer, num_warmup_steps, num_training_steps, lr_end=1e-7, power=1.0, last_epoch=-1
):
    """
    Create a schedule with a learning rate that decreases as a polynomial decay from the initial lr set in the
    optimizer to end lr defined by `lr_end`, after a warmup period during which it increases linearly from 0 to the
    initial lr set in the optimizer.
    Args:
        optimizer (:class:`~torch.optim.Optimizer`):
            The optimizer for which to schedule the learning rate.
        num_warmup_steps (:obj:`int`):
            The number of steps for the warmup phase.
        num_training_steps (:obj:`int`):
            The total number of training steps.
        lr_end (:obj:`float`, `optional`, defaults to 1e-7):
            The end LR.
        power (:obj:`float`, `optional`, defaults to 1.0):
            Power factor.
        last_epoch (:obj:`int`, `optional`, defaults to -1):
            The index of the last epoch when resuming training.
    Note: `power` defaults to 1.0 as in the fairseq implementation, which in turn is based on the original BERT
    implementation at
    https://github.com/google-research/bert/blob/f39e881b169b9d53bea03d2d341b31707a6c052b/optimization.py#L37
    Return:
        :obj:`torch.optim.lr_scheduler.LambdaLR` with the appropriate schedule.
    """

    lr_init = optimizer.defaults["lr"]
    assert lr_init > lr_end, f"lr_end ({lr_end}) must be be smaller than initial lr ({lr_init})"

    def lr_lambda(current_step: int):
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        elif current_step > num_training_steps:
            return lr_end / lr_init  # as LambdaLR multiplies by lr_init
        else:
            lr_range = lr_init - lr_end
            decay_steps = num_training_steps - num_warmup_steps
            pct_remaining = 1 - (current_step - num_warmup_steps) / decay_steps
            decay = lr_range * pct_remaining ** power + lr_end
            return decay / lr_init  # as LambdaLR multiplies by lr_init

    return LambdaLR(optimizer, lr_lambda, last_epoch)


class AdamW(Optimizer):
    """
    Implements Adam algorithm with weight decay fix as introduced in `Decoupled Weight Decay Regularization
    <https://arxiv.org/abs/1711.05101>`__.
    Parameters:
        params (:obj:`Iterable[torch.nn.parameter.Parameter]`):
            Iterable of parameters to optimize or dictionaries defining parameter groups.
        lr (:obj:`float`, `optional`, defaults to 1e-3):
            The learning rate to use.
        betas (:obj:`Tuple[float,float]`, `optional`, defaults to (0.9, 0.999)):
            Adam's betas parameters (b1, b2).
        eps (:obj:`float`, `optional`, defaults to 1e-6):
            Adam's epsilon for numerical stability.
        weight_decay (:obj:`float`, `optional`, defaults to 0):
            Decoupled weight decay to apply.
        bias_correction (:obj:`bool`, `optional`, defaults to `True`):
            Whether ot not to correct bias in Adam (for instance, in Bert TF repository they use :obj:`False`).
    """

    def __init__(
        self,
        params: Iterable[torch.nn.parameter.Parameter],
        lr: float = 1e-3,
        betas: Tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-6,
        weight_decay: float = 0.0,
        bias_correction: bool = True,
    ):
        if lr < 0.0:
            raise ValueError("Invalid learning rate: {} - should be >= 0.0".format(lr))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0[".format(betas[0]))
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0[".format(betas[1]))
        if not 0.0 <= eps:
            raise ValueError("Invalid epsilon value: {} - should be >= 0.0".format(eps))
        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay, correct_bias=bias_correction)
        super().__init__(params, defaults)

    def step(self, closure: Callable = None):
        """
        Performs a single optimization step.
        Arguments:
            closure (:obj:`Callable`, `optional`): A closure that reevaluates the model and returns the loss.
        """
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    raise RuntimeError("Adam does not support sparse gradients, please consider SparseAdam instead")

                state = self.state[p]

                # State initialization
                if len(state) == 0:
                    state["step"] = 0
                    # Exponential moving average of gradient values
                    state["exp_avg"] = torch.zeros_like(p.data)
                    # Exponential moving average of squared gradient values
                    state["exp_avg_sq"] = torch.zeros_like(p.data)

                exp_avg, exp_avg_sq = state["exp_avg"], state["exp_avg_sq"]
                beta1, beta2 = group["betas"]

                state["step"] += 1

                # Decay the first and second moment running average coefficient
                # In-place operations to update the averages at the same time
                exp_avg.mul_(beta1).add_(grad, alpha=1.0 - beta1)
                exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1.0 - beta2)
                denom = exp_avg_sq.sqrt().add_(group["eps"])

                step_size = group["lr"]
                if group["correct_bias"]:  # No bias correction for Bert
                    bias_correction1 = 1.0 - beta1 ** state["step"]
                    bias_correction2 = 1.0 - beta2 ** state["step"]
                    step_size = step_size * math.sqrt(bias_correction2) / bias_correction1

                p.data.addcdiv_(exp_avg, denom, value=-step_size)

                # Just adding the square of the weights to the loss function is *not*
                # the correct way of using L2 regularization/weight decay with Adam,
                # since that will interact with the m and v parameters in strange ways.
                #
                # Instead we want to decay the weights in a manner that doesn't interact
                # with the m/v parameters. This is equivalent to adding the square
                # of the weights to the loss with plain (non-momentum) SGD.
                # Add weight decay at the end (fixed version)
                if group["weight_decay"] > 0.0:
                    p.data.add_(p.data, alpha=-group["lr"] * group["weight_decay"])

        return loss


class Adafactor(Optimizer):
    """
    AdaFactor pytorch implementation can be used as a drop in replacement for Adam original fairseq code:
    https://github.com/pytorch/fairseq/blob/master/fairseq/optim/adafactor.py
    Paper: `Adafactor: Adaptive Learning Rates with Sublinear Memory Cost` https://arxiv.org/abs/1804.04235 Note that
    this optimizer internally adjusts the learning rate depending on the *scale_parameter*, *relative_step* and
    *warmup_init* options. To use a manual (external) learning rate schedule you should set `scale_parameter=False` and
    `relative_step=False`.
    Arguments:
        params (:obj:`Iterable[torch.nn.parameter.Parameter]`):
            Iterable of parameters to optimize or dictionaries defining parameter groups.
        lr (:obj:`float`, `optional`):
            The external learning rate.
        eps (:obj:`Tuple[float, float]`, `optional`, defaults to (1e-30, 1e-3)):
            Regularization constants for square gradient and parameter scale respectively
        clip_threshold (:obj:`float`, `optional`, defaults 1.0):
            Threshold of root mean square of final gradient update
        decay_rate (:obj:`float`, `optional`, defaults to -0.8):
            Coefficient used to compute running averages of square
        beta1 (:obj:`float`, `optional`):
            Coefficient used for computing running averages of gradient
        weight_decay (:obj:`float`, `optional`, defaults to 0):
            Weight decay (L2 penalty)
        scale_parameter (:obj:`bool`, `optional`, defaults to :obj:`True`):
            If True, learning rate is scaled by root mean square
        relative_step (:obj:`bool`, `optional`, defaults to :obj:`True`):
            If True, time-dependent learning rate is computed instead of external learning rate
        warmup_init (:obj:`bool`, `optional`, defaults to :obj:`False`):
            Time-dependent learning rate computation depends on whether warm-up initialization is being used
    This implementation handles low-precision (FP16, bfloat) values, but we have not thoroughly tested.
    Recommended T5 finetuning settings:
        - Scheduled LR warm-up to fixed LR
        - disable relative updates
        - use clip threshold: https://arxiv.org/abs/2004.14546
        Example::
            Adafactor(model.parameters(), lr=1e-3, relative_step=False, warmup_init=True)
        - Alternatively, relative_step with warmup_init can be used.
        - Training without LR warmup or clip threshold is not recommended. Additional optimizer operations like
          gradient clipping should not be used alongside Adafactor.
    Usage::
        # replace AdamW with Adafactor
        optimizer = Adafactor(
            model.parameters(),
            lr=1e-3,
            eps=(1e-30, 1e-3),
            clip_threshold=1.0,
            decay_rate=-0.8,
            beta1=None,
            weight_decay=0.0,
            relative_step=False,
            scale_parameter=False,
            warmup_init=False
        )
    """

    def __init__(
        self,
        params,
        lr=None,
        eps=(1e-30, 1e-3),
        clip_threshold=1.0,
        decay_rate=-0.8,
        beta1=None,
        weight_decay=0.0,
        scale_parameter=True,
        relative_step=True,
        warmup_init=False,
    ):
        if lr is not None and relative_step:
            raise ValueError("Cannot combine manual lr and relative_step options")
        if warmup_init and not relative_step:
            raise ValueError("warmup_init requires relative_step=True")

        defaults = dict(
            lr=lr,
            eps=eps,
            clip_threshold=clip_threshold,
            decay_rate=decay_rate,
            beta1=beta1,
            weight_decay=weight_decay,
            scale_parameter=scale_parameter,
            relative_step=relative_step,
            warmup_init=warmup_init,
        )
        super().__init__(params, defaults)

    @staticmethod
    def _get_lr(param_group, param_state):
        rel_step_sz = param_group["lr"]
        if param_group["relative_step"]:
            min_step = 1e-6 * param_state["step"] if param_group["warmup_init"] else 1e-2
            rel_step_sz = min(min_step, 1.0 / math.sqrt(param_state["step"]))
        param_scale = 1.0
        if param_group["scale_parameter"]:
            param_scale = max(param_group["eps"][1], param_state["RMS"])
        return param_scale * rel_step_sz

    @staticmethod
    def _get_options(param_group, param_shape):
        factored = len(param_shape) >= 2
        use_first_moment = param_group["beta1"] is not None
        return factored, use_first_moment

    @staticmethod
    def _rms(tensor):
        return tensor.norm(2) / (tensor.numel() ** 0.5)

    @staticmethod
    def _approx_sq_grad(exp_avg_sq_row, exp_avg_sq_col):
        r_factor = (exp_avg_sq_row / exp_avg_sq_row.mean(dim=-1, keepdim=True)).rsqrt_()
        c_factor = exp_avg_sq_col.rsqrt()
        return torch.mm(r_factor.unsqueeze(-1), c_factor.unsqueeze(0))

    def step(self, closure=None):
        """
        Performs a single optimization step
        Arguments:
            closure (callable, optional): A closure that reevaluates the model
                and returns the loss.
        """
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.dtype in {torch.float16, torch.bfloat16}:
                    grad = grad.float()
                if grad.is_sparse:
                    raise RuntimeError("Adafactor does not support sparse gradients.")

                state = self.state[p]
                grad_shape = grad.shape

                factored, use_first_moment = self._get_options(group, grad_shape)
                # State Initialization
                if len(state) == 0:
                    state["step"] = 0

                    if use_first_moment:
                        # Exponential moving average of gradient values
                        state["exp_avg"] = torch.zeros_like(grad)
                    if factored:
                        state["exp_avg_sq_row"] = torch.zeros(grad_shape[:-1]).to(grad)
                        state["exp_avg_sq_col"] = torch.zeros(grad_shape[:-2] + grad_shape[-1:]).to(grad)
                    else:
                        state["exp_avg_sq"] = torch.zeros_like(grad)

                    state["RMS"] = 0
                else:
                    if use_first_moment:
                        state["exp_avg"] = state["exp_avg"].to(grad)
                    if factored:
                        state["exp_avg_sq_row"] = state["exp_avg_sq_row"].to(grad)
                        state["exp_avg_sq_col"] = state["exp_avg_sq_col"].to(grad)
                    else:
                        state["exp_avg_sq"] = state["exp_avg_sq"].to(grad)

                p_data_fp32 = p.data
                if p.data.dtype in {torch.float16, torch.bfloat16}:
                    p_data_fp32 = p_data_fp32.float()

                state["step"] += 1
                state["RMS"] = self._rms(p_data_fp32)
                group["lr"] = self._get_lr(group, state)

                beta2t = 1.0 - math.pow(state["step"], group["decay_rate"])
                update = (grad ** 2) + group["eps"][0]
                if factored:
                    exp_avg_sq_row = state["exp_avg_sq_row"]
                    exp_avg_sq_col = state["exp_avg_sq_col"]

                    exp_avg_sq_row.mul_(beta2t).add_(1.0 - beta2t, update.mean(dim=-1))
                    exp_avg_sq_col.mul_(beta2t).add_(1.0 - beta2t, update.mean(dim=-2))

                    # Approximation of exponential moving average of square of gradient
                    update = self._approx_sq_grad(exp_avg_sq_row, exp_avg_sq_col)
                    update.mul_(grad)
                else:
                    exp_avg_sq = state["exp_avg_sq"]

                    exp_avg_sq.mul_(beta2t).add_(1.0 - beta2t, update)
                    update = exp_avg_sq.rsqrt().mul_(grad)

                update.div_((self._rms(update) / group["clip_threshold"]).clamp_(min=1.0))
                update.mul_(group["lr"])

                if use_first_moment:
                    exp_avg = state["exp_avg"]
                    exp_avg.mul_(group["beta1"]).add_(1 - group["beta1"], update)
                    update = exp_avg

                if group["weight_decay"] != 0:
                    p_data_fp32.add_(-group["weight_decay"] * group["lr"], p_data_fp32)

                p_data_fp32.add_(-update)

                if p.data.dtype in {torch.float16, torch.bfloat16}:
                    p.data.copy_(p_data_fp32)

        return loss


class LAMB(Optimizer):
    """Implements Lamb algorithm.
    It has been proposed in `Large Batch Optimization for Deep Learning:
    Training BERT in 76 minutes`__.
    Arguments:
        net: Network that includes all params to be optimized. Note that
            the second args, `params` should be in `net`.
        params: iterable of parameters to optimize or dicts defining
            parameter groups
        lr: learning rate (default: 1e-3)
        betas: coefficients used for computing
            running averages of gradient and its square (default: (0.9, 0.999))
        eps: term added to the denominator to improve
            numerical stability (default: 1e-8)
        weight_decay: weight decay (L2 penalty) (default: 0)
        exclude_from_weight_decay: List of regex patterns of
              variables excluded from weight decay. Variables whose name
              contain a substring matching the pattern will be excluded.
        exclude_from_layer_adaptation: List of regex patterns of
              variables excluded from layer adaptation. Variables whose name
              contain a substring matching the pattern will be excluded.
        adam: always use trust ratio = 1, which turns this
            into Adam. Useful for comparison purposes. (default: False)
        bias_correction: bias_correction adam by (1 - beta**step) (default: False)
        clamp_value: clamp weight_norm in (0,clamp_value) (default: 10)
            set to a high value to avoid it (e.g 10e3)
        grad_clip_norm: clip gradient by norm,
            -- view all gradients of all `param` as a single vector.
        grad_clip_value: clip gradient by value, with the constraint that
            all gradient values lie in (-grad_clip_value, grad_clip_value)
        **kwargs: keyword arguments. Allowed to be {`clipnorm`,
              `clipvalue`}. `clipnorm` is clip gradients by
              norm; `clipvalue` is clip gradients by value
    Example:
        >> from LAMB import Lamb
        >> optimizer = Lamb(model, model.parameters(), lr=0.1)
        >> optimizer.zero_grad()
        >> loss_fn(model(input), target).backward()
        >> optimizer.step()
    __ https://arxiv.org/abs/1904.00962
    Note:
        + Reference code:
        #1 https://github.com/cybertronai/pytorch-lamb
        #2 https://github.com/jettify/pytorch-optimizer/blob/master/torch_optimizer/lamb.py
        #3 https://github.com/tensorflow/addons/blob/master/tensorflow_addons/optimizers/lamb.py [Official]
        #4 https://github.com/fastalgo/imagenet_resnet50_lamb/blob/master/optimization.py
        + This is different from some Pytorch optimizers, which does not need to pass a `net` argument.
        Adapt to `exculde_from_weight_decay` and `exclude_from_layer_adaptation` by including this args.
        See Reference code #3 or #4
    """

    def __init__(
            self,
            net,
            params,
            lr=1e-3,
            betas=(0.9, 0.999),
            eps=1e-6,
            weight_decay=0,
            exclude_from_weight_decay=None,
            exclude_from_layer_adaptation=None,
            adam=False,
            bias_correction =False,
            clamp_value=10,
            grad_clip_norm=1.0,
            grad_clip_value=None,
            **kwargs
    ):
        if lr <= 0.0:
            raise ValueError('Invalid learning rate: {}'.format(lr))
        if eps < 0.0:
            raise ValueError('Invalid epsilon value: {}'.format(eps))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError(
                'Invalid beta parameter at index 0: {}'.format(betas[0])
            )
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError(
                'Invalid beta parameter at index 1: {}'.format(betas[1])
            )
        if weight_decay < 0:
            raise ValueError(
                'Invalid weight_decay value: {}'.format(weight_decay)
            )
        if clamp_value is not None and clamp_value < 0.0:
            raise ValueError('Invalid clamp value: {}'.format(clamp_value))

        if grad_clip_norm is not None and grad_clip_norm < 0.0:
            raise ValueError(
                'Invalid grad_clip_norm value: {}'.format(grad_clip_norm)
            )

        if grad_clip_value is not None and grad_clip_value < 0.0:
            raise ValueError(
                'Invalid grad_clip_value value: {}'.format(grad_clip_value)
            )

        if grad_clip_norm and grad_clip_value:
            raise ValueError(
                'Error: grad_clip_norm and grad_clip_value shoule be excluded,'
                'but got grad_clip_norm: {} and grad_clip_value: {}'.format(grad_clip_norm, grad_clip_value)
            )

        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
        self.net = net
        self.exclude_from_weight_decay = exclude_from_weight_decay
        # exclude_from_layer_adaptation is set to exclude_from_weight_decay if
        # the arg is None.
        # Borrow from official tensorflow implementation
        if exclude_from_layer_adaptation:
            self.exclude_from_layer_adaptation = exclude_from_layer_adaptation
        else:
            self.exclude_from_layer_adaptation = exclude_from_weight_decay
        self.adam = adam
        self.bias_correction = bias_correction
        self.clamp_value = clamp_value  # clamp_value see reference code in Pytorch, they clamp value of the weight norm
        self.grad_clip_norm = grad_clip_norm  # clip gradient by norm -- view all grad of all `param` as a single vector
        self.grad_clip_value = grad_clip_value  # clip gradient by value

        super(LAMB, self).__init__(params, defaults)
        self._check()
        self._init_paraName()

    def _check(self):
        r'''
        Check if all `params` are in `net`
        '''
        netDict = defaultdict(dict)
        for p in self.net.parameters():
            netDict[p] = True
        for group in self.param_groups:
            for p in group['params']:
                if netDict.get(p) is None:
                    msg = (
                        'All `params` must be in `net` '
                        'but got unexpected parameter(s). '
                        'Please check.'
                    )
                    raise RuntimeError(msg)
        del netDict

    def _init_paraName(self):
        r'''
        Get all parameters' name in `self.net` and then store it in `self.state`
        Do it in initialzation.
        '''
        for name, para in self.net.named_parameters():
            module_top2bottom = name.split('.')
            cursor = self.net
            for i in range(len(module_top2bottom) - 1):
                cursor = getattr(cursor, module_top2bottom[i])
            bottom_m_name = repr(cursor).split('(')[0]
            this_para_name = '.'.join([bottom_m_name, module_top2bottom[-1]])

            # Adding name for each parameter
            # e.g. Conv2d.weight, BatchNorm2d.bias, etc.
            # This is for `exclude_weight_dacay` and `exculde_layer_adaptation`
            self.state[para]['para_name'] = this_para_name

    def _do_layer_adaptation(self, para):
        r"""
        Whether to do layer-wise learning rate adaptation for `para`.
        """
        para_name = self.state[para]['para_name']
        if self.exclude_from_layer_adaptation:
            for r in self.exclude_from_layer_adaptation:
                if re.search(r, para_name, re.I) is not None:
                    return False
        return True

    def _do_use_weight_decay(self, para):
        r"""Whether to use L2 weight decay for `param`."""
        para_name = self.state[para]['para_name']
        if self.exclude_from_weight_decay:
            for r in self.exclude_from_weight_decay:
                if re.search(r, para_name, re.I) is not None:
                    return False
        return True

    def gradient_clipping(self):
        r'''
        Gradient clipping.
        `grad_clip_norm` and `grad_clip_value` should be excluded.
        '''
        if self.grad_clip_norm:
            torch.nn.utils.clip_grad_norm_(
                parameters=[p for group in self.param_groups for p in group['params']],
                max_norm=self.grad_clip_norm,
                norm_type=2
            )

        if self.grad_clip_value:
            torch.nn.utils.clip_grad_value_(
                parameters=[p for group in self.param_groups for p in group['params']],
                clip_value=self.grad_clip_value
            )

    def step(self, closure=None):
        r"""Performs a single optimization step.
        Arguments:
            closure: A closure that reevaluates the model and returns the loss.
        """
        loss = None
        if closure is not None:
            loss = closure()

        # Be Cautious if gradient clipping is done outside this optimizer.
        # If so, SET `grad_clip_norm = None` and `grad_clip_value = None`.
        self.gradient_clipping()

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    msg = (
                        'Lamb does not support sparse gradients, '
                        'please consider SparseAdam instead'
                    )
                    raise RuntimeError(msg)

                state = self.state[p]

                # State initialization
                # Modified len(state) == 0 to len(state)<=1 because para_name is added to
                # self.state in initialization stage
                if len(state) <= 1:
                    state['step'] = 0
                    # Exponential moving average of gradient values
                    state['exp_avg'] = torch.zeros_like(p)
                    # Exponential moving average of squared gradient values
                    state['exp_avg_sq'] = torch.zeros_like(p)

                exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']
                beta1, beta2 = group['betas']

                state['step'] += 1

                # Decay the first and second moment running average coefficient
                # m_t
                exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                # v_t
                exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)

                # Paper v3 does not use bias_correction.
                if self.bias_correction:
                    bias_correction = math.sqrt(1 - beta2 ** state['step'])
                    bias_correction /= 1 - beta1 ** state['step']
                else:
                    bias_correction = 1

                # Apply bias to lr to avoid broadcast.
                step_size = group['lr'] * bias_correction

                weight_norm = torch.norm(p.data)
                if self.clamp_value:
                    weight_norm.clamp_(0, self.clamp_value)

                adam_step = exp_avg / exp_avg_sq.sqrt().add(group['eps'])
                if group['weight_decay'] != 0 and self._do_use_weight_decay(p):
                    adam_step.add_(p.data, alpha=group['weight_decay'])

                adam_norm = torch.norm(adam_step)

                if weight_norm == 0 or adam_norm == 0 or not self._do_layer_adaptation(p):
                    trust_ratio = 1
                else:
                    trust_ratio = weight_norm / adam_norm
                state['weight_norm'] = weight_norm
                state['adam_norm'] = adam_norm
                state['trust_ratio'] = trust_ratio

                if self.adam:
                    trust_ratio = 1

                p.data.add_(adam_step, alpha=-step_size * trust_ratio)

        return loss


str2optimizer = {"adamw": AdamW, "adafactor": Adafactor}


str2scheduler = {"linear": get_linear_schedule_with_warmup, "cosine": get_cosine_schedule_with_warmup,
              "cosine_with_restarts": get_cosine_with_hard_restarts_schedule_with_warmup,
              "polynomial": get_polynomial_decay_schedule_with_warmup,
              "constant": get_constant_schedule, "constant_with_warmup": get_constant_schedule_with_warmup}
