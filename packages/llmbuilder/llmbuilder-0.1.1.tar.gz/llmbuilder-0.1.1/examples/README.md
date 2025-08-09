# llmbuilder Examples

This folder contains small, focused examples that demonstrate how to use the llmbuilder package via both the Python API and the CLI.

## 1) Quickstart: Generate Text (Python API)

Run with paths to your trained model and tokenizer directory:

```bash
python examples/generate_text.py --model path/to/model.pt --tokenizer path/to/tokenizer --prompt "Hello world"
```

## 2) Quickstart: Minimal Training (Python API)

This demonstrates building a small model config preset and showing the high-level calls. It is intentionally light and prints steps without running heavy training by default. Enable the `--run` flag to actually launch a tiny training loop.

```bash
python examples/train_tiny.py --data path/to/text.txt --out ./checkpoints --run
```

## 3) CLI Usage

- Show help:
  - `llmbuilder --help`
- Data preprocess:
  - `llmbuilder data preprocess -i ./data/raw -o ./data/clean.txt`
- Train tokenizer:
  - `llmbuilder data tokenizer -i ./data/clean.txt -o ./tokenizers --vocab-size 16000`
- Train model:
  - `llmbuilder train model -d ./data/clean.txt -t ./tokenizers -o ./checkpoints`
- Generate text (interactive):
  - `llmbuilder generate text --setup`

## Notes
- CPU-only PyTorch can be installed with:
  - `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- For performance tests, install `pytest-benchmark` and set `RUN_PERF=1`.
