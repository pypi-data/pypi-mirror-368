import torch
from .model import embeddings, encoders, targets
from .model.model import UniModel


def build_model(config):
    embedding = embeddings[config.lm.embedding](config)
    encoder = encoders[config.lm.encoder](config)
    target = targets[config.lm.target](config, config.lm.vocab_size)
    model = UniModel(config, embedding, None, encoder, target)
    return model


def load_model(model, model_path):
    model_dict = torch.load(model_path, map_location="cpu")
    if hasattr(model, "module"):
        model.module.load_state_dict(model_dict['model'], strict=False)
    else:
        model.load_state_dict(model_dict['model'], strict=False)
    optimizer = model_dict['optimizer']
    scheduler = model_dict['scheduler']
    start_step = model_dict['step']
    start_epoch = model_dict['epoch']
    global_step = model_dict['global_step']
    return model, optimizer, scheduler, start_step, start_epoch, global_step


def save_model(model, step, epoch, global_step, optimizer, scheduler, model_path):
    if hasattr(model, "module"):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()
    model_dict = {
        'model': state_dict,
        'optimizer': optimizer.state_dict(),
        'scheduler': scheduler.state_dict(),
        'step': step,
        'epoch' : epoch,
        'global_step' : global_step
    }
    torch.save(model_dict, model_path)
