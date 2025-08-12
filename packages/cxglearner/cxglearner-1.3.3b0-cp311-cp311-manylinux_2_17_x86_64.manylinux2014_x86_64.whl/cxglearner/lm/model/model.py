import torch.nn as nn
from ...config.config import Config


class UniModel(nn.Module):
    def __init__(self, config: Config, embedding, selection, encoder, target):
        super(UniModel, self).__init__()
        self.embedding = embedding
        self.selection = selection
        self.encoder = encoder
        self.target = target

        if config.lm.target == "mlm" and config.lm.tie_weights:
            self.target.mlm_linear_2.weight = self.embedding.word_embedding.weight
        elif config.lm.target == "lm" and config.lm.tie_weights:
            self.target.output_layer.weight = self.embedding.word_embedding.weight

    def forward(self, src, tgt):
        emb = self.embedding(src)
        memory_bank = self.encoder(src, emb)
        loss_info = self.target(memory_bank, tgt)
        return loss_info
