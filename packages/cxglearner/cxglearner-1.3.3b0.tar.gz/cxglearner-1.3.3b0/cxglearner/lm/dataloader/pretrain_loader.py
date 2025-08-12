from ffrecord import FileReader
import pickle
from ffrecord.torch import Dataset
from ...utils.utils_lm import rescale_level_probs


class PretrainLoader(Dataset):
    def __init__(self, config, fnames, check_data=True):
        super(PretrainLoader, self).__init__(fnames)
        self.reader = FileReader(fnames, check_data)
        self.config = config
        self.vocab = config.lm.tokenizer.vocab
        self.tokenizer = config.lm.tokenizer
        self.seq_length = config.lm.seq_length
        self.whole_word_masking = config.lm.whole_word_masking
        self.legal_levels = config.lm.tokenizer.ava_levels
        self.level_probs = config.lm.selection_probs
        self.mask_ids = self.tokenizer.tokenizer.mask_token_id if 'mask_token_id' in self.tokenizer.tokenizer.__dict__ else None
        self.pad_ids =  self.tokenizer.tokenizer.pad_token_id if 'pad_token_id' in self.tokenizer.tokenizer.__dict__ else None
        self.bos_ids = self.tokenizer.tokenizer.bos_token_id if 'bos_token_id' in self.tokenizer.tokenizer.__dict__ else None
        self.eos_ids = self.tokenizer.tokenizer.eos_token_id if 'eos_token_id' in self.tokenizer.tokenizer.__dict__ else None
        self.special_tokenids = [self.mask_ids, self.pad_ids, self.eos_ids, self.bos_ids]
        # Check and re-scale level information
        self.check_levels()

    def __len__(self):
        return self.reader.n

    def __getitem__(self, indices):
        data = self.reader.read(indices)
        # deserialize data
        samples = [pickle.loads(b) for b in data]
        # process data
        samples = self._processor(samples)
        return samples

    def _processor(self, instances):
        raise NotImplementedError

    def check_levels(self):
        if self.level_probs is None:
            if self.config.lm.logger is not None: self.config.lm.logger.error("The parameter `selectionProbs` or `selection_probs` cannot be None.")
            else: print("The parameter `selectionProbs` or `selection_probs` cannot be None.")
            raise Exception("The parameter `selectionProbs` or `selection_probs` cannot be None.")
        # Check for levels
        filterd_level = []
        for level in self.level_probs:
            if level not in self.legal_levels:
                if self.config.lm.logger is not None:
                    self.config.lm.logger.warning("There is no `{}` level in training data, ignored.".format(level))
                else:
                    print("There is no `{}` level in training data, ignored.".format(level))
                filterd_level.append(level)
        for level in filterd_level: del self.level_probs[level]
        if len(self.level_probs) == 0 or 'lexical' not in self.level_probs:
            if self.config.lm.logger is not None:
                self.config.lm.logger.error("The `lexical` level is necessary. Please double-check the config and training data.")
            else:
                print("The `lexical` level is necessary. Please double-check the config and training data.")
            raise Exception("The `lexical` level is necessary. Please double-check the config and training data.")
        level_probs = [rescale_level_probs(self.level_probs, self.config.lm.logger)[key] for key in self.legal_levels]
        self.level_probs = [{key: i for i, key in enumerate(self.legal_levels)}, [sum(level_probs[:i]) + prob  for i, prob in enumerate(level_probs)]]
