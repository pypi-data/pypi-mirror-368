#!/usr/bin/env python
"""
Example: Tiny training using llmbuilder's Python API.

This script is CPU-friendly and demonstrates the API. By default it
shows the planned steps. Use --run to actually start a short training run.

Usage:
  python examples/train_tiny.py --data ./data/clean.txt --out ./checkpoints --run
"""

import argparse
from pathlib import Path

import llmbuilder as lb


def main(argv=None):
    p = argparse.ArgumentParser(description="llmbuilder tiny training example")
    p.add_argument("--data", "-d", required=True, help="Path to training text file")
    p.add_argument("--out", "-o", required=True, help="Output directory for checkpoints")
    p.add_argument("--run", action="store_true", help="Execute a brief training run")
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--lr", type=float, default=1e-4)
    args = p.parse_args(argv)

    # Use a small CPU preset
    cfg = lb.load_config(preset="cpu_small")
    cfg.training.num_epochs = args.epochs
    cfg.training.batch_size = args.batch_size
    cfg.training.learning_rate = args.lr
    cfg.system.device = "cpu"

    print("Plan:")
    print(f"  - Load data from: {args.data}")
    print(f"  - Output dir:     {args.out}")
    print("  - Model:           layers=%d heads=%d dim=%d seq=%d vocab=%d" % (
        cfg.model.num_layers, cfg.model.num_heads, cfg.model.embedding_dim, cfg.model.max_seq_length, cfg.model.vocab_size
    ))
    print("  - Training:        epochs=%d batch=%d lr=%.2e" % (
        cfg.training.num_epochs, cfg.training.batch_size, cfg.training.learning_rate
    ))

    if not args.run:
        print("\nTip: run with --run to execute a short training loop.")
        return 0

    # Build model, load dataset, and train
    model = lb.build_model(cfg.model)
    from llmbuilder.data import TextDataset
    dataset = TextDataset(args.data, block_size=cfg.model.max_seq_length)

    Path(args.out).mkdir(parents=True, exist_ok=True)
    results = lb.train_model(model, dataset, cfg.training)
    print("Training finished.")
    print(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
