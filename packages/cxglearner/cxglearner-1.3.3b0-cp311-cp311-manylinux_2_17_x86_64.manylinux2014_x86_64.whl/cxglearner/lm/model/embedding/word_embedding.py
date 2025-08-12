import torch
import torch.nn as nn
from ..layers.layernorm import LayerNorm


class WordEmbedding(nn.Module):
    def __init__(self, config):
        super(WordEmbedding, self).__init__()
        self.remove_embedding_layernorm = config.lm.remove_embedding_layernorm
        self.vocab_size = config.lm.vocab_size
        self.dropout = nn.Dropout(config.lm.dropout)
        padding_idx = config.lm.tokenizer.tokenizer.pad_token_id if 'pad_token_id' in config.lm.tokenizer.tokenizer.__dict__ else config.lm.tokenizer.tokenizer.eos_token_id
        self.word_embedding = nn.Embedding(
            self.vocab_size, config.lm.emb_size, padding_idx=padding_idx)
        if not self.remove_embedding_layernorm:
            self.layer_norm = LayerNorm(config.lm.emb_size)

    def forward(self, src):
        """
        Args:
            src: [batch_size x seq_length]
        Returns:
            emb: [batch_size x seq_length x hidden_size]
        """
        emb = self.word_embedding(src)
        if not self.remove_embedding_layernorm:
            emb = self.layer_norm(emb)
        emb = self.dropout(emb)
        return emb


class WordPosEmbedding(WordEmbedding):
    """
    GPT embedding consists of two parts:
    word embedding and position embedding.
    """

    def __init__(self, config):
        super(WordPosEmbedding, self).__init__(config)
        self.max_seq_length = config.lm.max_seq_length
        self.position_embedding = nn.Embedding(
            self.max_seq_length, config.lm.emb_size)

    def forward(self, src):
        """
        Args:
            src: [batch_size x seq_length]
            seg: [batch_size x seq_length]
        Returns:
            emb: [batch_size x seq_length x hidden_size]
        """
        word_emb = self.word_embedding(src)
        pos_emb = self.position_embedding(
            torch.arange(0, word_emb.size(
                1), device=word_emb.device, dtype=torch.long)
            .unsqueeze(0)
            .repeat(word_emb.size(0), 1)
        )

        emb = word_emb + pos_emb
        if not self.remove_embedding_layernorm:
            emb = self.layer_norm(emb)
        emb = self.dropout(emb)
        return emb
