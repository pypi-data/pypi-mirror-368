#!/usr/bin/env python
"""
Example: Generate text using llmbuilder's Python API.

Usage:
  python examples/generate_text.py --model path/to/model.pt --tokenizer path/to/tokenizer --prompt "Hello"
  python examples/generate_text.py --model path/to/model.pt --tokenizer path/to/tokenizer --interactive
"""

import argparse
import sys

import llmbuilder as lb


def main(argv=None):
    p = argparse.ArgumentParser(description="llmbuilder text generation example")
    p.add_argument("--model", "-m", required=True, help="Path to trained model checkpoint")
    p.add_argument("--tokenizer", "-t", required=True, help="Path to tokenizer directory")
    p.add_argument("--prompt", "-p", help="Prompt text (omit if using --interactive)")
    p.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    p.add_argument("--max-new-tokens", type=int, default=100)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--top-k", type=int, default=50)
    p.add_argument("--top-p", type=float, default=0.9)
    p.add_argument("--device", default=None, help="cpu/cuda (auto if omitted)")
    args = p.parse_args(argv)

    if args.interactive:
        lb.interactive_cli(args.model, args.tokenizer, device=args.device)
        return 0

    if not args.prompt:
        print("Please provide --prompt or use --interactive.", file=sys.stderr)
        return 2

    text = lb.generate_text(
        model_path=args.model,
        tokenizer_path=args.tokenizer,
        prompt=args.prompt,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        device=args.device,
    )
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
