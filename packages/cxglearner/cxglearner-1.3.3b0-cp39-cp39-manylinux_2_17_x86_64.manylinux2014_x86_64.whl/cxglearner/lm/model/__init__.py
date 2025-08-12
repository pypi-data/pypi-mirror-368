from .embedding.word_embedding import WordEmbedding, WordPosEmbedding
from .encoder.transformer_encoder import TransformerEncoder
from .target.lm_target import LmTarget
from .target.mlm_target import MlmTarget

embeddings = {
    'word': WordEmbedding,
    'word_pos': WordPosEmbedding,
}

encoders = {
    'transformer': TransformerEncoder
}

targets = {
    'mlm': MlmTarget,
    'lm': LmTarget
}

__all__ = ['embeddings', 'encoders', 'targets']
