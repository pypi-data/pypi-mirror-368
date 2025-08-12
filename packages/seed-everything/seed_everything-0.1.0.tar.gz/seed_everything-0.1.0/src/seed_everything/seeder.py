import os
from .seeds import (
    is_imported,
    seed_random,
    seed_numpy,
    seed_torch,
    seed_tensorflow,
    seed_jax
)


def seed_everything(seed: int = 42):
    """
    Seed everything to make experiments reproducible.
    Checks if libraries are imported before seeding.
    """
    os.environ['PYTHONHASHSEED'] = str(seed)
    seed_random(seed)

    # Seed numpy if it is imported
    if is_imported("numpy"):
        seed_numpy(seed)

    # Seed torch if it is imported
    if is_imported("torch"):
        seed_torch(seed)

    # Seed tensorflow if it is imported
    if is_imported("tensorflow"):
        seed_tensorflow(seed)

    # Seed jax if it is imported
    if is_imported("jax"):
        seed_jax(seed)
