# llmbuilder

A modular toolkit for building, training, fine-tuning, generating, and exporting GPT-style language models with CPU-friendly defaults.

## About LLMBuilder Framework

**LLMBuilder** is a production-ready framework for training and fine-tuning Large Language Models (LLMs) — not a model itself. Designed for developers, researchers, and AI engineers, LLMBuilder provides a full pipeline to go from raw text data to deployable, optimized LLMs, all running locally on CPUs or GPUs.

### Complete Framework Structure

The full LLMBuilder framework includes:

```
LLMBuilder/
├── data/                   # Data directories
│   ├── raw/               # Raw input files (.txt, .pdf, .docx)
│   ├── cleaned/           # Processed text files
│   └── tokens/            # Tokenized datasets
│   ├── download_data.py   # Script to download datasets
│   └── SOURCES.md         # Data sources documentation
│
├── debug_scripts/         # Debugging utilities
│   ├── debug_loader.py    # Data loading debugger
│   ├── debug_training.py  # Training process debugger
│   └── debug_timestamps.py # Timing analysis
│
├── eval/                  # Model evaluation
│   └── eval.py           # Evaluation scripts
│
├── exports/               # Output directories
│   ├── checkpoints/      # Training checkpoints
│   ├── gguf/             # GGUF model exports
│   ├── onnx/             # ONNX model exports
│   └── tokenizer/        # Saved tokenizer files
│
├── finetune/             # Fine-tuning scripts
│   ├── finetune.py      # Fine-tuning implementation
│   └── __init__.py      # Package initialization
│
├── logs/                 # Training and evaluation logs
│
├── model/                # Model architecture
│   └── gpt_model.py     # GPT model implementation
│
├── tools/                # Utility scripts
│   ├── analyze_data.ps1  # PowerShell data analysis
│   ├── analyze_data.sh   # Bash data analysis
│   ├── download_hf_model.py # HuggingFace model downloader
│   └── export_gguf.py    # GGUF export utility
│
├── training/             # Training pipeline
│   ├── dataset.py       # Dataset handling
│   ├── preprocess.py    # Data preprocessing
│   ├── quantization.py  # Model quantization
│   ├── train.py         # Main training script
│   ├── train_tokenizer.py # Tokenizer training
│   └── utils.py         # Training utilities
│
├── .gitignore           # Git ignore rules
├── config.json          # Main configuration
├── config_cpu_small.json # Small CPU config
├── config_gpu.json      # GPU configuration
├── inference.py         # Inference script
├── quantize_model.py    # Model quantization
├── README.md           # Documentation
├── requirements.txt    # Python dependencies
├── run.ps1            # PowerShell runner
└── run.sh             # Bash runner
```

🔗 **Full Framework Repository**: [https://github.com/qubasehq/llmbuilder](https://github.com/qubasehq/llmbuilder)

> [!NOTE]
> **This is a separate framework** - The complete LLMBuilder framework shown above is **not related to this package**. It's a standalone, comprehensive framework available at the GitHub repository. This package (`llmbuilder_package`) provides the core modular toolkit, while the complete framework offers additional utilities, debugging tools, and production-ready scripts for comprehensive LLM development workflows.

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
