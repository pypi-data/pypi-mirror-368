# llmbuilder

A modular toolkit for building, training, fine-tuning, generating, and exporting GPT-style language models with CPU-friendly defaults.

## Installation

Python 3.9+ recommended.

- CPU-only PyTorch:
  - `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- Core dependencies:
  - `pip install -e .`

Optional:
- Performance tests: `pip install pytest-benchmark`

## CLI Quickstart

- Show help:
  - `llmbuilder --help`
- Preprocess data from mixed files into a text corpus:
  - `llmbuilder data preprocess -i ./data/raw -o ./data/clean.txt`
- Train tokenizer (BPE via SentencePiece):
  - `llmbuilder data tokenizer -i ./data/clean.txt -o ./tokenizers --vocab-size 16000`
- Train model (tiny CPU-friendly settings):
  - `llmbuilder train model -d ./data/clean.txt -t ./tokenizers -o ./checkpoints`
- Generate text (interactive):
  - `llmbuilder generate text --setup`

## Python API Quickstart

```python
import llmbuilder as lb

# Load a preset config and build a model
cfg = lb.load_config(preset="cpu_small")
model = lb.build_model(cfg.model)

# Train (example; see examples/train_tiny.py for a runnable script)
from llmbuilder.data import TextDataset
dataset = TextDataset("./data/clean.txt", block_size=cfg.model.max_seq_length)
results = lb.train_model(model, dataset, cfg.training)

# Generate text
text = lb.generate_text(
    model_path="./checkpoints/model.pt",
    tokenizer_path="./tokenizers",
    prompt="Hello world",
    max_new_tokens=50,
)
print(text)
```

## More
- Examples: see the `examples/` folder
  - `examples/generate_text.py`
  - `examples/train_tiny.py`
- Migration from older scripts: see `MIGRATION.md`

## For Developers and Advanced Users
- Python API quickstart:
  ```python
  import llmbuilder as lb
  cfg = lb.load_config(preset="cpu_small")
  model = lb.build_model(cfg.model)
  from llmbuilder.data import TextDataset
  dataset = TextDataset("./data/clean.txt", block_size=cfg.model.max_seq_length)
  results = lb.train_model(model, dataset, cfg.training)
  text = lb.generate_text(
      model_path="./checkpoints/model.pt",
      tokenizer_path="./tokenizers",
      prompt="Hello",
      max_new_tokens=64,
      temperature=0.8,
      top_k=50,
      top_p=0.9,
  )
  print(text)
  ```
- Config presets and legacy keys:
  - Use `lb.load_config(preset="cpu_small")` or `path="config.yaml"`.
  - Legacy flat keys like `n_layer`, `n_head`, `n_embd` are accepted and mapped internally.
- Useful CLI flags:
  - Training: `--epochs`, `--batch-size`, `--lr`, `--eval-interval`, `--save-interval` (see `llmbuilder train model --help`).
  - Generation: `--max-new-tokens`, `--temperature`, `--top-k`, `--top-p`, `--device` (see `llmbuilder generate text --help`).
- Environment knobs:
  - Enable slow tests: `set RUN_SLOW=1`
  - Enable performance tests: `set RUN_PERF=1`
- Performance tips:
  - Prefer CPU wheels for broad compatibility; use smaller seq length and batch size.
  - Checkpoints are saved under `checkpoints/`; consider periodic eval to monitor perplexity.

## Testing (developers)
- Fast tests: `python -m pytest -q tests`
- Slow tests: `set RUN_SLOW=1 && python -m pytest -q tests`
- Performance tests: `set RUN_PERF=1 && python -m pytest -q tests\performance`

## License
Apache-2.0 (or project license).
