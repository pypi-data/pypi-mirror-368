import random
import os
import torch
import re
from typing import List, Tuple
import numpy as np
from logging import Logger
from huggingface_hub import HfApi
from huggingface_hub.utils import RepositoryNotFoundError
from .predefine import HF_MAGIC_ENDPOINT, HF_ENDPOINT



def set_seed(seed=42):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


def optimizer_to_cuda(optimizer):
    for state in optimizer.state.values():
        for k, v in state.items():
            if torch.is_tensor(v):
                state[k] = v.cuda()
    return optimizer


def allow_tf324torch(config, logger: Logger = None):
    if 'tf32' not in config.__dict__: return
    torch.backends.cuda.matmul.allow_tf32 = config.tf32
    torch.backends.cudnn.allow_tf32 = config.tf32
    if config.tf32:
        if logger is not None: logger.warning('Allow pytorch to use TF-32 to accelerate model')
        else: print('Allow pytorch to use TF-32 to accelerate model')


def clean_version(version):
    return ''.join(c for c in version if c.isdigit() or c == '.')


def version_key(version):
    parts = clean_version(version).split('.')
    return tuple(int(part) for part in parts)


def get_latest_version(versions):
    if not versions:
        return None
    sorted_versions = sorted(versions, key=version_key)
    return sorted_versions[-1]


class HuggingFaceModelMatcher:
    def __init__(self):
        self.hf_model_pattern = r'^(?![\./\\])[a-zA-Z0-9][a-zA-Z0-9\-\.]{0,38}\/[a-zA-Z0-9][a-zA-Z0-9\-\.\_]{0,96}$'
        self.strict_pattern = r'^(?![\./\\~])(?![A-Za-z]:)(?!.*[\\/]{2,})[a-zA-Z0-9][a-zA-Z0-9\-\.]{0,38}\/[a-zA-Z0-9][a-zA-Z0-9\-\.\_]{0,96}(?<![\\/])$'
        self.path_patterns = [
            r'^[\./\\~]',
            r'^[A-Za-z]:',
            r'.*[\\/]{2,}',
            r'[\\/]$',
            r'.*[\\/]\.\.[\\/]',
            r'^\/[^\/]',
            r'.*\.(exe|bat|sh|py|txt|json|bin|safetensors)$',
        ]

        self.url_pattern = r'https?:\/\/huggingface\.co\/([a-zA-Z0-9][a-zA-Z0-9\-\.]{0,38}\/[a-zA-Z0-9][a-zA-Z0-9\-\.\_]{0,96})'

    def is_local_path(self, path: str) -> bool:
        for pattern in self.path_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        return False

    def is_valid_hf_model(self, model_name: str) -> bool:
        if self.is_local_path(model_name):
            return False
        return bool(re.match(self.strict_pattern, model_name))

    def extract_hf_models_from_text(self, text: str) -> List[str]:
        candidate_pattern = r'\b[a-zA-Z0-9][a-zA-Z0-9\-\.\/\_]{3,100}\b'
        candidates = re.findall(candidate_pattern, text)

        valid_models = []
        for candidate in candidates:
            if self.is_valid_hf_model(candidate):
                valid_models.append(candidate)
        url_models = re.findall(self.url_pattern, text)
        valid_models.extend(url_models)

        return list(set(valid_models))


def hf_model_validation(path_or_model: str) -> Tuple:
    matcher = HuggingFaceModelMatcher()
    is_valid = matcher.is_valid_hf_model(path_or_model)
    if not is_valid:
        return False, ""
    print("[ASE] This appears to be a Hugging Face model. Checking if the model is registered, please wait... ")
    api = HfApi(endpoint=HF_ENDPOINT)
    try:
        api.model_info(path_or_model, timeout=30)
        return True, HF_ENDPOINT
    except RepositoryNotFoundError:
        return False, ""
    except:
        print("[ASE] Your network cannot access Hugging Face, please be patient - we will automatically switch to HF-mirror ...")
        api_magic = HfApi(endpoint=HF_MAGIC_ENDPOINT)
        api_magic.model_info(path_or_model, timeout=30)
        try:
            return True, HF_MAGIC_ENDPOINT
        except:
            return False, ""
