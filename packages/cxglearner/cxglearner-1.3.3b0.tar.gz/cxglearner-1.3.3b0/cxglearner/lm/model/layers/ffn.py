import torch.nn as nn
from ....utils.utils_lm import activate_fns


class PositionwiseFFN(nn.Module):
    def __init__(self, hidden_size, feedforward_size, hidden_act, has_bias=True):
        super(PositionwiseFFN, self).__init__()
        self.linear_1 = nn.Linear(hidden_size, feedforward_size, bias=has_bias)
        self.linear_2 = nn.Linear(feedforward_size, hidden_size, bias=has_bias)
        self.act = activate_fns[hidden_act]

    def forward(self, x):
        inter = self.act(self.linear_1(x))
        output = self.linear_2(inter)
        return output
