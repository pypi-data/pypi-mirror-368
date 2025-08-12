from .lmtrainer import LMTrainer
from .mlmtrainer import MLMTrainer

trainers = {
    'base': MLMTrainer,
    'gpt': LMTrainer,
}
