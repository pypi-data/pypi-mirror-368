import random
import os
import sys


def is_imported(module_name: str) -> bool:
    """Checks if a module is imported."""
    return module_name in sys.modules


def seed_random(seed: int):
    """Seeds the `random` module."""
    random.seed(seed)

def seed_numpy(seed: int):
    """Seeds the `numpy` module."""
    import numpy as np
    np.random.seed(seed)


def seed_torch(seed: int):
    """Seeds the `torch` module."""
    import torch
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def seed_tensorflow(seed: int):
    """Seeds the `tensorflow` module."""
    import tensorflow as tf
    tf.random.set_seed(seed)


def seed_jax(seed: int):
    """Seeds the `jax` module."""
    import jax
    jax.random.PRNGKey(seed)
