# Simple Guide: Using llmbuilder (No Tech Jargon)

This guide explains how to use llmbuilder in very simple steps.
You only need Windows and Python installed.

## What does this do?
- It turns your documents (text/PDF/Word) into a small local AI model.
- You can ask it to write text or continue a sentence.
- Everything runs on your own computer.

## What you need
- Windows PC
- Python 3.9 or newer (download from python.org)

## Step 1 — Open the folder
1) Download or open the `llmbuilder_package` folder.
2) Right‑click inside the folder and choose “Open in Terminal” (or open PowerShell here).

## Step 2 — Set up (one‑time)
Copy and paste these commands, one by one:

1) Make a safe Python space (virtual environment):
```
python -m venv venv
```
2) Turn it on:
```
venv\Scripts\Activate.ps1
```
3) Install the needed packages (works on most PCs):
```
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e .
```
If an error appears, close the window and open it again. Then try step 2 and 3 again.

## Step 3 — Prepare your files
1) Create a folder: `data/raw`
2) Put your files in it (text/PDF/Word). Start small (5–10 files).
3) Turn them into one clean text file:
```
llmbuilder data preprocess -i .\data\raw -o .\data\clean.txt
```

## Step 4 — Make a tokenizer
This helps the model read text:
```
llmbuilder data tokenizer -i .\data\clean.txt -o .\tokenizers --vocab-size 16000
```

## Step 5 — Train a small model
This teaches the model from your text. It can take some time.
```
llmbuilder train model -d .\data\clean.txt -t .\tokenizers -o .\checkpoints
```
Tip: You can stop anytime with Ctrl + C. Try with fewer files if it’s slow.

## Step 6 — Try it!
Start interactive text generation:
```
llmbuilder generate text --setup
```
Follow the on‑screen steps to pick your model and tokenizer.

## Where are my files?
- Clean text: `data/clean.txt`
- Tokenizer: `tokenizers/`
- Trained model: `checkpoints/`

## Quick fixes
- “llmbuilder is not recognized” → Close and reopen PowerShell, then run `pip install -e .` again.
- “No module named torch” → Run: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- “Permission denied” on venv → Run: `Set-ExecutionPolicy -Scope Process Bypass`, then activate venv again.
- Too slow → Use fewer files, or stop with Ctrl + C.

## Want more?
See the main README for advanced options and examples.
