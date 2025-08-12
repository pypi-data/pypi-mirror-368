import torch
import torch.nn as nn
from ..layers.layernorm import LayerNorm
from ..layers.transformer import TransformerLayer

class TransformerEncoder(nn.Module):
    def __init__(self, config):
        super(TransformerEncoder, self).__init__()
        self.mask = config.lm.mask
        self.layers_num = config.lm.layers_num
        self.parameter_sharing = config.lm.parameter_sharing
        self.factorized_embedding_parameterization = config.lm.factorized_embedding_parameterization
        self.layernorm_positioning = config.lm.layernorm_positioning
        self.relative_position_embedding = config.lm.relative_position_embedding
        self.has_residual_attention = config.lm.has_residual_attention

        if self.factorized_embedding_parameterization:
            self.linear = nn.Linear(config.lm.emb_size, config.lm.hidden_size)

        if self.parameter_sharing:
            self.transformer = TransformerLayer(config)
        else:
            self.transformer = nn.ModuleList(
                [TransformerLayer(config) for _ in range(self.layers_num)]
            )
        if self.layernorm_positioning == "pre":
            self.layer_norm = LayerNorm(config.lm.hidden_size)

    def forward(self, src, emb):
        """
        Args:
            src: [batch_size x seq_length]
            emb: [batch_size x seq_length x emb_size]
        Returns:
            hidden: [batch_size x seq_length x hidden_size]
        """
        if self.factorized_embedding_parameterization:
            emb = self.linear(emb)

        batch_size, seq_length, _ = emb.size()
        # Generate mask according to segment indicators.
        # mask: [batch_size x 1 x seq_length x seq_length]
        if self.mask == "fully_visible":
            mask = (src > 0). \
                unsqueeze(1). \
                repeat(1, seq_length, 1). \
                unsqueeze(1)
            mask = mask.float()
            mask = (1.0 - mask) * -10000.0
        elif self.mask == "causal":
            mask = torch.ones(seq_length, seq_length, device=emb.device)
            mask = torch.tril(mask)
            mask = (1.0 - mask) * -10000
            mask = mask.repeat(batch_size, 1, 1, 1)
        else:
            mask_a = (src == 1). \
                unsqueeze(1). \
                repeat(1, seq_length, 1). \
                unsqueeze(1).float()

            mask_b = (src > 0). \
                unsqueeze(1). \
                repeat(1, seq_length, 1). \
                unsqueeze(1).float()

            mask_tril = torch.ones(seq_length, seq_length, device=emb.device)
            mask_tril = torch.tril(mask_tril)
            mask_tril = mask_tril.repeat(batch_size, 1, 1, 1)

            mask = (mask_a + mask_b + mask_tril >= 2).float()
            mask = (1.0 - mask) * -10000.0

        hidden = emb
        prev_attn, position_bias = None, None

        for i in range(self.layers_num):
            if self.parameter_sharing:
                hidden, prev_attn = self.transformer(hidden, mask, position_bias=position_bias,
                                                     has_residual_attention=self.has_residual_attention,
                                                     prev_attn=prev_attn)
            else:
                hidden, prev_attn = self.transformer[i](hidden, mask, position_bias=position_bias,
                                                        has_residual_attention=self.has_residual_attention,
                                                        prev_attn=prev_attn)

        if self.layernorm_positioning == "pre":
            return self.layer_norm(hidden)
        else:
            return hidden
