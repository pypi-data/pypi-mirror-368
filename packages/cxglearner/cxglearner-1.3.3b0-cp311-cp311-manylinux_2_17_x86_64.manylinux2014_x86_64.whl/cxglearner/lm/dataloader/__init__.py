from .lmloader import LearnerLMLoader, LearnerGPTLoader

dataloaders = {
    'base': LearnerLMLoader,
    'gpt': LearnerGPTLoader
}
