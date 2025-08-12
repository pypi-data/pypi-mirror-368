import torch.nn as nn
from logging import Logger
from typing import Optional

import os
import torch
import collections

from ..model import embeddings, encoders, targets
from ...config.config import Config
from ...utils.misc import hf_model_validation


class LMHead(nn.Module):
    """
    Language Model Head class that combines embeddings, encoder, and target layer.
    """
    def __init__(self, config: Config, logger: Logger):
        super(LMHead, self).__init__()
        self.logger = logger
        self.embedding = embeddings[config.lm.embedding](config)
        self.encoder = encoders[config.lm.encoder](config)
        self.target = targets[config.lm.target](config, config.lm.vocab_size)

    def from_pretrained(self, path: str, device: Optional[torch.device] = None):
        # Determine whether path belongs to huggingface model
        model_or_path, endpoint = hf_model_validation(path)
        if model_or_path:
            from huggingface_hub import hf_hub_download
            self.logger.info(f"[ASE] Downloading model `{path}` to cache dir.")
            try:
                path = hf_hub_download(
                    repo_id=path,
                    filename="pytorch_model.bin",
                    endpoint="https://hf-mirror.com"
                )
            except Exception:
                self.logger.info(
                    f"[ASE] Download procedure failed. You can browse https://huggingface.co/CxGrammar for manual download and set config.lm.output_path")
                import traceback
                traceback.print_exc()
        else:
            if path.split('.')[-1] not in ['pt', 'pth', 'bin']: path = os.path.join(path, 'pytorch_model.bin')
            if not os.path.exists(path):
                if self.logger is not None: self.logger.error(
                    'the model checkpint path `{}` seems incorrect.'.format(path))
                raise Exception('the model checkpint path `{}` seems incorrect.'.format(path))
        parameters = torch.load(path, map_location="cpu")
        if isinstance(parameters, dict):
            if 'model' not in parameters:
                if self.logger is not None: self.logger.error(
                    "the checkpoint is dict format, but do not contain the key of model.")
                assert 'model' in parameters, "the checkpoint is dict format, but do not contain the key of model."
            parameters = parameters['model']
        elif isinstance(parameters, collections.OrderedDict):
            pass
        else:
            if self.logger is not None: self.logger.error(
                "the format of checkpoint is invalid, only can be dict or OrderedDict.")
            raise Exception('the format of checkpoint is invalid, only can be dict or OrderedDict.')
        if hasattr(self, "module"):
            self.module.load_state_dict(parameters, strict=False)
        else:
            self.load_state_dict(parameters, strict=False)

    def forward(self, src: torch.Tensor, only_hidden: bool = False) -> torch.Tensor:
        """
        Forward pass through the language model head.
        """
        emb = self.embedding(src)
        memory_bank = self.encoder(src, emb)
        if only_hidden:
            return memory_bank
        output = self.target.output_layer(memory_bank)
        return output
