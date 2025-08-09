# Migration Guide

This guide helps migrate from legacy scripts/configs to the `llmbuilder` package structure.

## Config Keys

Legacy flat keys map to structured config in `llmbuilder.config.defaults.Config`.

- `n_layer` -> `model.num_layers`
- `n_head` -> `model.num_heads`
- `n_embd` -> `model.embedding_dim`
- `block_size` -> `model.max_seq_length`
- `dropout` -> `model.dropout`
- `bias` -> `model.bias`
- `device` -> `system.device`
- `vocab_size` -> `model.vocab_size`

Backward compatibility:
- Legacy flat keys are accepted in `Config.from_dict()`.
- Legacy attribute aliases (e.g., `cfg.n_layer`) are exposed for read access.

## Loading Configs

Before:
```python
# legacy
cfg = load_config_json("config.json")
```

Now:
```python
import llmbuilder as lb
cfg = lb.load_config(path="config.json")
# or presets
cfg = lb.load_config(preset="cpu_small")
```

## Building and Training

Before:
```python
model = build_gpt(cfg)
train(model, data, cfg)
```

Now:
```python
import llmbuilder as lb
model = lb.build_model(cfg.model)
from llmbuilder.data import TextDataset
dataset = TextDataset("./data/clean.txt", block_size=cfg.model.max_seq_length)
results = lb.train_model(model, dataset, cfg.training)
```

## CLI Changes

- Data preprocess:
  - Legacy: custom scripts
  - Now: `llmbuilder data preprocess -i ./data/raw -o ./data/clean.txt`
- Tokenizer training:
  - Legacy: `training/train_tokenizer.py`
  - Now: `llmbuilder data tokenizer -i ./data/clean.txt -o ./tokenizers --vocab-size 16000`
- Model training:
  - Legacy: `training/train.py` arguments
  - Now: `llmbuilder train model -d ./data/clean.txt -t ./tokenizers -o ./checkpoints`
- Text generation:
  - Legacy: custom generate.py
  - Now: `llmbuilder generate text --setup` (interactive) or use the Python API `llmbuilder.generate_text()`

## Examples
See `examples/`:
- `examples/generate_text.py`
- `examples/train_tiny.py`

## Notes
- CPU-only PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- Tests: `python -m pytest -q tests` (set `RUN_SLOW`/`RUN_PERF` to enable slow/perf).
