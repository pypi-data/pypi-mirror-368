import torch.nn as nn
from .layernorm import LayerNorm
from .ffn import PositionwiseFFN
from .attention import MultiHeadedAttention


class TransformerLayer(nn.Module):
    def __init__(self, config):
        super(TransformerLayer, self).__init__()
        self.layernorm_positioning = config.lm.layernorm_positioning
        if hasattr(config.lm, "attention_head_size"):
            attention_head_size = config.lm.attention_head_size
        else:
            attention_head_size = config.lm.hidden_size // config.lm.heads_num

        has_bias = bool(1 - config.lm.remove_transformer_bias)
        with_scale = bool(1 - config.lm.remove_attention_scale)
        offbyone = config.lm.offbyone

        # Multi-headed self-attention.
        self.self_attn = MultiHeadedAttention(
            config.lm.hidden_size, config.lm.heads_num, attention_head_size, config.lm.dropout, has_bias=has_bias,
            with_scale=with_scale, offbyone=offbyone
        )
        self.dropout_1 = nn.Dropout(config.lm.dropout)

        # Feed forward layer.
        self.feed_forward = PositionwiseFFN(
            config.lm.hidden_size, config.lm.feedforward_size, config.lm.hidden_act, has_bias
        )
        self.dropout_2 = nn.Dropout(config.lm.dropout)

        self.layer_norm_1 = LayerNorm(config.lm.hidden_size)
        self.layer_norm_2 = LayerNorm(config.lm.hidden_size)

    def forward(self, hidden, mask, position_bias = None, has_residual_attention=False, prev_attn=None):
        """
        Args:
            hidden: [batch_size x seq_length x emb_size]
            mask: [batch_size x 1 x seq_length x seq_length]
            position_bias: [1 x heads_num x seq_length x seq_length]
        Returns:
            output: [batch_size x seq_length x hidden_size]
        """

        if self.layernorm_positioning == "post":
            inter, prev_attn_out = self.self_attn(hidden, hidden, hidden, mask, position_bias, has_residual_attention, prev_attn)
            inter = self.dropout_1(inter)
            inter = self.layer_norm_1(inter + hidden)
            output = self.dropout_2(self.feed_forward(inter))
            output = self.layer_norm_2(output + inter)
        else:
            inter = self.layer_norm_1(hidden)
            inter, prev_attn_out = self.self_attn(inter, inter, inter, mask, position_bias, has_residual_attention, prev_attn)
            inter = self.dropout_1(inter)
            hidden = hidden + inter
            output = self.layer_norm_2(hidden)
            output = self.dropout_2(self.feed_forward(output)) + hidden
        return output, prev_attn_out