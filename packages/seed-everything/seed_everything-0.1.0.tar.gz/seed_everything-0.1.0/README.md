# Seed Everything

A lightweight library to seed everything for reproducible experiments in deep learning.

## Installation

```bash
pip install seed-everything
```

## Usage

```python
from seed_everything import seed_everything

seed_everything(42)
```

This will seed:
- `random`
- `os`
- `numpy`
- `torch` (if available)
- `tensorflow` (if available)
- `jax` (if available)
