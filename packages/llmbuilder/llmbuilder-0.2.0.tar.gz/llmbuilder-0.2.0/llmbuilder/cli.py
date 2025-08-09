"""
Command-line interface for LLMBuilder.

This module provides the main CLI entry point for the llmbuilder package.
"""

import click
from . import __version__

@click.group()
@click.version_option(version=__version__, prog_name="llmbuilder")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def main(ctx, verbose):
    """
    🤖 LLMBuilder - A comprehensive toolkit for building, training, and deploying language models.
    
    Built with ❤️ by Qubase - Empowering developers to create amazing AI applications.
    
    Use 'llmbuilder COMMAND --help' for more information on a specific command.
    
    \b
    Quick Start:
      llmbuilder info                    # Show package information
      llmbuilder config create --help    # Create configuration files
      llmbuilder train model --help      # Train a new model
      llmbuilder generate text --help    # Generate text with trained models
    
    \b
    Visit https://qubase.in for more resources and documentation.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        click.echo("🔧 Verbose mode enabled")

@main.command()
def welcome():
    """🎉 Welcome to LLMBuilder! Get started with guided setup."""
    click.echo("🎉 " + click.style("Welcome to LLMBuilder!", fg="blue", bold=True))
    click.echo("Built with ❤️  by " + click.style("Qubase", fg="cyan", bold=True))
    click.echo()
    
    click.echo("🚀 " + click.style("What would you like to do?", fg="green", bold=True))
    
    options = [
        ("1", "📖 Learn about LLMBuilder", "info"),
        ("2", "⚙️  Create a configuration file", "config create --interactive"),
        ("3", "📁 Load and preprocess data", "data load --interactive"),
        ("4", "🔤 Train a tokenizer", "data tokenizer --interactive"),
        ("5", "🧠 Train a new model", "train model --interactive"),
        ("6", "🎯 Generate text with a model", "generate text --setup"),
        ("7", "📚 View all available commands", "--help")
    ]
    
    for num, desc, _ in options:
        click.echo(f"  {num}. {desc}")
    
    click.echo()
    choice = click.prompt("Choose an option (1-7)", type=click.Choice([str(i) for i in range(1, 8)]))
    
    _, _, command = options[int(choice) - 1]
    
    if command == "info":
        from .cli import info
        ctx = click.get_current_context()
        ctx.invoke(info)
    elif command == "--help":
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
    else:
        click.echo(f"\n🚀 Running: llmbuilder {command}")
        click.echo("💡 You can run this command directly next time!")
        click.echo()
        # Note: In a real implementation, you'd invoke the actual command
        click.echo(f"Command to run: llmbuilder {command}")

@main.command()
def info():
    """Display package information and credits."""
    click.echo("🤖 " + click.style("LLMBuilder", fg="blue", bold=True) + f" version {__version__}")
    click.echo()
    click.echo("📖 " + click.style("Description:", fg="green", bold=True))
    click.echo("   A comprehensive toolkit for building, training, and deploying language models.")
    click.echo()
    click.echo("🏢 " + click.style("Built by Qubase:", fg="cyan", bold=True))
    click.echo("   Qubase is dedicated to empowering developers with cutting-edge AI tools.")
    click.echo("   Visit us at: " + click.style("https://qubase.in", fg="blue", underline=True))
    click.echo()
    click.echo("📦 " + click.style("Available modules:", fg="yellow", bold=True))
    modules = [
        ("data", "Data loading and preprocessing from various formats"),
        ("tokenizer", "Tokenizer training and management with SentencePiece"),
        ("model", "GPT-style transformer model building and management"),
        ("training", "Full training pipeline with checkpointing and metrics"),
        ("finetune", "Fine-tuning with LoRA and domain adaptation"),
        ("inference", "Text generation with various sampling strategies"),
        ("export", "Model export to GGUF, ONNX, and quantized formats"),
        ("config", "Configuration management for different hardware setups"),
        ("utils", "Common utilities for logging and checkpoint management")
    ]
    
    for module, description in modules:
        click.echo(f"  • {click.style(module, fg='cyan'):<12} - {description}")
    
    click.echo()
    click.echo("🚀 " + click.style("Quick Commands:", fg="magenta", bold=True))
    click.echo("   llmbuilder config create --preset cpu_small -o config.json")
    click.echo("   llmbuilder train model --data data.txt --tokenizer tokenizer/ --output model/")
    click.echo("   llmbuilder generate text -m model.pt -t tokenizer/ -p 'Hello world' --interactive")
    click.echo()
    click.echo("💡 " + click.style("Need help?", fg="green", bold=True) + " Use --help with any command for detailed information.")
    click.echo("📚 Documentation: https://github.com/qubasehq/llmbuilder-package/wiki")
    click.echo("🐛 Report issues: https://github.com/qubasehq/llmbuilder-package/issues")

@main.command()
def info():
    """Display package information."""
    click.echo(f"LLMBuilder version {__version__}")
    click.echo("A comprehensive toolkit for building, training, and deploying language models.")
    click.echo("\nAvailable modules:")
    click.echo("  - data: Data loading and preprocessing")
    click.echo("  - tokenizer: Tokenizer training and management") 
    click.echo("  - model: Model building and management")
    click.echo("  - training: Training pipeline")
    click.echo("  - finetune: Fine-tuning capabilities")
    click.echo("  - inference: Text generation and inference")
    click.echo("  - export: Model export utilities")
    click.echo("  - config: Configuration management")
    click.echo("  - utils: Common utilities")

# Data processing commands
@main.group()
def data():
    """Data loading and preprocessing commands."""
    pass

@data.command()
@click.option('--input', '-i', help='Input file or directory path')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', type=click.Choice(['txt', 'pdf', 'docx', 'all']), default='all', help='File format to process')
@click.option('--clean', is_flag=True, help='Clean text during processing')
@click.option('--min-length', default=50, help='Minimum text length to keep')
@click.option('--interactive', is_flag=True, help='Interactive mode with prompts')
def load(input, output, format, clean, min_length, interactive):
    """📁 Load and preprocess text data from various formats."""
    from .data import DataLoader
    from pathlib import Path
    
    # Interactive mode
    if interactive or not input or not output:
        click.echo("🤖 " + click.style("Interactive Data Loading", fg="blue", bold=True))
        click.echo("Let's set up your data loading configuration!\n")
        
        if not input:
            input = click.prompt("📂 Input file or directory path", type=str)
        if not output:
            output = click.prompt("💾 Output file path", type=str)
        
        if click.confirm("🧹 Would you like to clean the text during processing?"):
            clean = True
        
        min_length = click.prompt("📏 Minimum text length to keep", default=min_length, type=int)
        
        click.echo(f"\n🚀 Starting data loading with your settings...")
    
    click.echo(f"📖 Loading data from {click.style(input, fg='cyan')}...")
    
    try:
        loader = DataLoader(min_length=min_length, clean_text=clean)
        input_path = Path(input)
        
        if input_path.is_file():
            with click.progressbar(length=1, label='Processing file') as bar:
                text = loader.load_file(input_path)
                bar.update(1)
            
            if text:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(text)
                click.echo(f"✅ Processed file saved to {click.style(output, fg='green')}")
                click.echo(f"📊 Text length: {len(text):,} characters")
            else:
                click.echo("❌ Failed to load file")
        elif input_path.is_dir():
            texts = []
            files = list(input_path.rglob("*"))
            supported_files = [f for f in files if f.suffix.lower() in loader.get_supported_extensions()]
            
            if not supported_files:
                click.echo("❌ No supported files found in directory")
                return
            
            with click.progressbar(supported_files, label='Processing files') as bar:
                for file_path in bar:
                    try:
                        text = loader.load_file(file_path)
                        if text:
                            texts.append(text)
                            if interactive:
                                click.echo(f"  ✅ {file_path.name}")
                    except Exception as e:
                        if interactive:
                            click.echo(f"  ❌ {file_path.name}: {e}")
            
            if texts:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(texts))
                total_chars = sum(len(text) for text in texts)
                click.echo(f"✅ Combined {len(texts)} files saved to {click.style(output, fg='green')}")
                click.echo(f"📊 Total text length: {total_chars:,} characters")
            else:
                click.echo("❌ No files processed successfully")
        else:
            click.echo(f"❌ Input path not found: {input}")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        if interactive:
            click.echo("💡 Try checking your file paths and permissions.")

@data.command()
@click.option('--input', '-i', required=True, help='Input text file')
@click.option('--output', '-o', required=True, help='Output directory for tokenizer')
@click.option('--vocab-size', default=16000, help='Vocabulary size')
@click.option('--model-type', type=click.Choice(['bpe', 'unigram', 'word', 'char']), default='bpe', help='Tokenizer model type')
def tokenizer(input, output, vocab_size, model_type):
    """Train a tokenizer on text data."""
    from .tokenizer import TokenizerTrainer
    from .config import TokenizerConfig
    from pathlib import Path
    
    click.echo(f"Training {model_type} tokenizer with vocab size {vocab_size}...")
    
    config = TokenizerConfig(vocab_size=vocab_size, model_type=model_type)
    trainer = TokenizerTrainer(config=config)
    
    try:
        results = trainer.train(input_file=input, output_dir=output)
        click.echo(f"✓ Tokenizer training completed!")
        click.echo(f"  Model: {results['model_file']}")
        click.echo(f"  Vocab: {results['vocab_file']}")
        click.echo(f"  Training time: {results['training_time']:.1f}s")
    except Exception as e:
        click.echo(f"✗ Tokenizer training failed: {e}")

# Model training commands
@main.group() 
def train():
    """Model training commands."""
    pass

@train.command()
@click.option('--config', '-c', help='Path to training configuration file')
@click.option('--data', '-d', required=True, help='Path to training data')
@click.option('--tokenizer', '-t', required=True, help='Path to tokenizer directory')
@click.option('--output', '-o', required=True, help='Output directory for model')
@click.option('--epochs', default=10, help='Number of training epochs')
@click.option('--batch-size', default=32, help='Batch size')
@click.option('--lr', default=3e-4, help='Learning rate')
@click.option('--vocab-size', default=16000, help='Vocabulary size')
@click.option('--layers', default=8, help='Number of transformer layers')
@click.option('--heads', default=8, help='Number of attention heads')
@click.option('--dim', default=512, help='Embedding dimension')
def model(config, data, tokenizer, output, epochs, batch_size, lr, vocab_size, layers, heads, dim):
    """Train a new language model from scratch."""
    from .config import ModelConfig, TrainingConfig
    from .model import build_model
    from .training import train_model
    from .data import TextDataset
    from pathlib import Path
    
    click.echo("Setting up model training...")
    
    # Create model config
    model_config = ModelConfig(
        vocab_size=vocab_size,
        num_layers=layers,
        num_heads=heads,
        embedding_dim=dim,
        max_seq_length=1024,
        dropout=0.1
    )
    
    # Create training config
    training_config = TrainingConfig(
        num_epochs=epochs,
        batch_size=batch_size,
        learning_rate=lr,
        save_every=1000,
        eval_every=500
    )
    
    click.echo(f"Building model: {layers} layers, {heads} heads, {dim} dim...")
    model = build_model(model_config)
    
    click.echo(f"Loading dataset from {data}...")
    dataset = TextDataset(data, block_size=model_config.max_seq_length)
    
    click.echo("Starting training...")
    try:
        results = train_model(model, dataset, training_config, checkpoint_dir=output)
        click.echo(f"✓ Training completed!")
        click.echo(f"  Final loss: {results.get('final_loss', 'N/A')}")
        click.echo(f"  Model saved to: {output}")
    except Exception as e:
        click.echo(f"✗ Training failed: {e}")

@train.command()
@click.option('--checkpoint', '-c', required=True, help='Path to checkpoint to resume from')
@click.option('--data', '-d', required=True, help='Path to training data')
@click.option('--output', '-o', help='Output directory (defaults to checkpoint dir)')
def resume(checkpoint, data, output):
    """Resume training from a checkpoint."""
    from .training import resume_training
    from .data import TextDataset
    
    click.echo(f"Resuming training from {checkpoint}...")
    
    try:
        dataset = TextDataset(data)
        results = resume_training(checkpoint, dataset, output_dir=output)
        click.echo(f"✓ Training resumed and completed!")
        click.echo(f"  Final loss: {results.get('final_loss', 'N/A')}")
    except Exception as e:
        click.echo(f"✗ Resume training failed: {e}")

@main.group()
def finetune():
    """Fine-tuning commands."""
    pass

@finetune.command()
@click.option('--model', '-m', required=True, help='Path to pre-trained model')
@click.option('--dataset', '-d', required=True, help='Path to fine-tuning dataset')
@click.option('--output', '-o', required=True, help='Output directory for fine-tuned model')
@click.option('--epochs', default=3, help='Number of training epochs')
@click.option('--lr', default=5e-5, help='Learning rate')
@click.option('--batch-size', default=4, help='Batch size')
@click.option('--use-lora', is_flag=True, help='Use LoRA fine-tuning')
@click.option('--lora-rank', default=4, help='LoRA rank')
def model(model, dataset, output, epochs, lr, batch_size, use_lora, lora_rank):
    """Fine-tune a pre-trained model."""
    from .finetune import FineTuningConfig, finetune_model
    from .model import load_model
    from .data import TextDataset
    
    click.echo(f"Loading model from {model}...")
    model_obj = load_model(model)
    
    click.echo(f"Loading dataset from {dataset}...")
    dataset_obj = TextDataset(dataset)
    
    config = FineTuningConfig(
        num_epochs=epochs,
        learning_rate=lr,
        batch_size=batch_size,
        use_lora=use_lora,
        lora_rank=lora_rank
    )
    
    click.echo("Starting fine-tuning...")
    results = finetune_model(model_obj, dataset_obj, config, checkpoint_dir=output)
    
    click.echo(f"Fine-tuning completed!")
    click.echo(f"Best validation loss: {results['best_val_loss']:.4f}")
    click.echo(f"Final model saved to: {results.get('final_model_path', output)}")

@main.group()
def generate():
    """Text generation commands.

    Includes an interactive mode. See the 'text' subcommand and use the
    --interactive option to start an interactive prompt for generation.
    """
    pass

@generate.command()
@click.option('--model', '-m', help='Path to trained model checkpoint')
@click.option('--tokenizer', '-t', help='Path to tokenizer directory')
@click.option('--prompt', '-p', help='Text prompt for generation')
@click.option('--interactive', '-i', is_flag=True, help='Run in interactive mode')
@click.option('--max-tokens', default=100, help='Maximum tokens to generate')
@click.option('--temperature', default=0.8, help='Sampling temperature (0.1-2.0)')
@click.option('--top-k', default=50, help='Top-k sampling (1-100)')
@click.option('--top-p', default=0.9, help='Top-p sampling (0.1-1.0)')
@click.option('--device', help='Device to use (cpu/cuda)')
@click.option('--setup', is_flag=True, help='Interactive setup mode')
def text(model, tokenizer, prompt, interactive, max_tokens, temperature, top_k, top_p, device, setup):
    """🎯 Generate text using a trained model with advanced sampling options."""
    from .inference import GenerationConfig, interactive_cli, generate_text
    
    # Interactive setup mode
    if setup or not model or not tokenizer:
        click.echo("🤖 " + click.style("LLMBuilder Text Generation Setup", fg="blue", bold=True))
        click.echo("Built by " + click.style("Qubase", fg="cyan", bold=True) + " - Let's generate some amazing text!\n")
        
        if not model:
            model = click.prompt("🧠 Path to your trained model checkpoint", type=str)
        if not tokenizer:
            tokenizer = click.prompt("🔤 Path to your tokenizer directory", type=str)
        
        if not interactive and not prompt:
            mode = click.prompt(
                "🎮 Choose generation mode",
                type=click.Choice(['interactive', 'single']),
                default='interactive'
            )
            interactive = (mode == 'interactive')
        
        if not interactive and not prompt:
            prompt = click.prompt("💭 Enter your text prompt", type=str)
        
        # Advanced settings
        if click.confirm("⚙️  Would you like to customize generation settings?"):
            max_tokens = click.prompt("📏 Maximum tokens to generate", default=max_tokens, type=int)
            temperature = click.prompt("🌡️  Temperature (creativity: 0.1=focused, 2.0=creative)", default=temperature, type=float)
            top_k = click.prompt("🔝 Top-k sampling (diversity)", default=top_k, type=int)
            top_p = click.prompt("🎯 Top-p sampling (nucleus)", default=top_p, type=float)
        
        click.echo(f"\n🚀 Starting text generation...")
    
    config = GenerationConfig(
        max_new_tokens=max_tokens,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p
    )
    
    try:
        if interactive:
            click.echo("🎮 " + click.style("Interactive Text Generation", fg="green", bold=True))
            click.echo("💡 Type your prompts and watch the AI respond!")
            click.echo("🔧 You can adjust settings in real-time during the session.\n")
            interactive_cli(model, tokenizer, device=device, config=config)
        elif prompt:
            click.echo(f"💭 Prompt: {click.style(prompt, fg='yellow')}")
            click.echo("🤔 Generating...")
            
            with click.progressbar(length=1, label='Thinking') as bar:
                result = generate_text(model, tokenizer, prompt, device=device, **config.__dict__)
                bar.update(1)
            
            click.echo(f"\n🎯 " + click.style("Generated Text:", fg="green", bold=True))
            click.echo("─" * 50)
            click.echo(result)
            click.echo("─" * 50)
            click.echo(f"📊 Settings: temp={temperature}, top_k={top_k}, top_p={top_p}, max_tokens={max_tokens}")
            click.echo("\n💡 " + click.style("Tip:", fg="blue") + " Use --interactive for a chat-like experience!")
        else:
            click.echo("❌ Please provide either --prompt or --interactive flag")
            click.echo("💡 Or use --setup for guided configuration")
            click.echo("📚 Use 'llmbuilder generate text --help' for more information")
    
    except Exception as e:
        click.echo(f"❌ Generation failed: {e}")
        click.echo("💡 " + click.style("Troubleshooting tips:", fg="blue"))
        click.echo("   • Check that your model and tokenizer paths are correct")
        click.echo("   • Ensure your model and tokenizer are compatible")
        click.echo("   • Try reducing max_tokens if you're running out of memory")
        click.echo("   • Visit https://github.com/qubasehq/llmbuilder-package/wiki for help")

# Model management commands
@main.group()
def model():
    """Model management commands."""
    pass

@model.command()
@click.option('--config', '-c', help='Path to model configuration file')
@click.option('--vocab-size', default=16000, help='Vocabulary size')
@click.option('--layers', default=8, help='Number of transformer layers')
@click.option('--heads', default=8, help='Number of attention heads')
@click.option('--dim', default=512, help='Embedding dimension')
@click.option('--output', '-o', required=True, help='Output path for model')
def create(config, vocab_size, layers, heads, dim, output):
    """Create a new model with specified architecture."""
    from .config import ModelConfig
    from .model import build_model, save_model
    
    click.echo("Creating new model...")
    
    model_config = ModelConfig(
        vocab_size=vocab_size,
        num_layers=layers,
        num_heads=heads,
        embedding_dim=dim,
        max_seq_length=1024,
        dropout=0.1
    )
    
    model = build_model(model_config)
    save_model(model, output)
    
    num_params = sum(p.numel() for p in model.parameters())
    click.echo(f"✓ Model created with {num_params:,} parameters")
    click.echo(f"✓ Model saved to {output}")

@model.command()
@click.argument('model_path')
def info(model_path):
    """Display information about a model."""
    from .model import load_model
    
    click.echo(f"Loading model from {model_path}...")
    
    try:
        model = load_model(model_path)
        num_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        click.echo(f"✓ Model loaded successfully")
        click.echo(f"  Total parameters: {num_params:,}")
        click.echo(f"  Trainable parameters: {trainable_params:,}")
        click.echo(f"  Model type: {type(model).__name__}")
        
        if hasattr(model, 'get_metadata'):
            metadata = model.get_metadata()
            click.echo(f"  Architecture: {metadata.n_layer} layers, {metadata.n_head} heads")
            click.echo(f"  Embedding dim: {metadata.n_embd}")
            click.echo(f"  Vocab size: {metadata.vocab_size}")
            click.echo(f"  Max sequence length: {metadata.block_size}")
    except Exception as e:
        click.echo(f"✗ Failed to load model: {e}")

@model.command()
@click.argument('model_path')
@click.option('--dataset', '-d', required=True, help='Path to evaluation dataset')
@click.option('--batch-size', default=32, help='Batch size for evaluation')
def evaluate(model_path, dataset, batch_size):
    """Evaluate a model on a dataset."""
    from .model import load_model
    from .training import evaluate_model
    from .data import TextDataset
    
    click.echo(f"Loading model from {model_path}...")
    model = load_model(model_path)
    
    click.echo(f"Loading dataset from {dataset}...")
    eval_dataset = TextDataset(dataset)
    
    click.echo("Evaluating model...")
    try:
        results = evaluate_model(model, eval_dataset, batch_size=batch_size)
        click.echo(f"✓ Evaluation completed!")
        click.echo(f"  Perplexity: {results.get('perplexity', 'N/A')}")
        click.echo(f"  Loss: {results.get('loss', 'N/A')}")
    except Exception as e:
        click.echo(f"✗ Evaluation failed: {e}")

# Export commands
@main.group()
def export():
    """Model export commands."""
    pass

@export.command()
@click.argument('model_path')
@click.option('--output', '-o', required=True, help='Output path for GGUF model')
@click.option('--quantization', type=click.Choice(['f16', 'q8_0', 'q4_0', 'q4_1']), default='f16', help='Quantization type')
def gguf(model_path, output, quantization):
    """Export model to GGUF format for llama.cpp compatibility."""
    from .export import export_gguf
    
    click.echo(f"Exporting model to GGUF format...")
    click.echo(f"  Input: {model_path}")
    click.echo(f"  Output: {output}")
    click.echo(f"  Quantization: {quantization}")
    
    try:
        export_gguf(model_path, output, quantization=quantization)
        click.echo(f"✓ Model exported successfully to {output}")
    except Exception as e:
        click.echo(f"✗ Export failed: {e}")

@export.command()
@click.argument('model_path')
@click.option('--output', '-o', required=True, help='Output path for ONNX model')
@click.option('--opset', default=11, help='ONNX opset version')
def onnx(model_path, output, opset):
    """Export model to ONNX format for mobile/runtime inference."""
    from .export import export_onnx
    
    click.echo(f"Exporting model to ONNX format...")
    click.echo(f"  Input: {model_path}")
    click.echo(f"  Output: {output}")
    click.echo(f"  Opset version: {opset}")
    
    try:
        export_onnx(model_path, output, opset_version=opset)
        click.echo(f"✓ Model exported successfully to {output}")
    except Exception as e:
        click.echo(f"✗ Export failed: {e}")

@export.command()
@click.argument('model_path')
@click.option('--output', '-o', required=True, help='Output path for quantized model')
@click.option('--method', type=click.Choice(['dynamic', 'static', 'qat']), default='dynamic', help='Quantization method')
@click.option('--bits', type=click.Choice([8, 16]), default=8, help='Quantization bits')
def quantize(model_path, output, method, bits):
    """Quantize model for edge deployment."""
    from .export import quantize_model
    
    click.echo(f"Quantizing model...")
    click.echo(f"  Input: {model_path}")
    click.echo(f"  Output: {output}")
    click.echo(f"  Method: {method}")
    click.echo(f"  Bits: {bits}")
    
    try:
        quantize_model(model_path, output, method=method, bits=bits)
        click.echo(f"✓ Model quantized successfully to {output}")
    except Exception as e:
        click.echo(f"✗ Quantization failed: {e}")

# Configuration commands
@main.group()
def config():
    """Configuration management commands."""
    pass

@config.command()
@click.option('--preset', type=click.Choice(['cpu_small', 'gpu_medium', 'gpu_large', 'inference']), help='Configuration preset')
@click.option('--output', '-o', help='Output path for configuration file')
@click.option('--interactive', is_flag=True, help='Interactive configuration creation')
def create(preset, output, interactive):
    """⚙️  Create a configuration file with guided setup."""
    from .config import DefaultConfigs
    import json
    
    # Interactive mode
    if interactive or not preset or not output:
        click.echo("⚙️  " + click.style("LLMBuilder Configuration Creator", fg="blue", bold=True))
        click.echo("Built by " + click.style("Qubase", fg="cyan", bold=True) + " - Let's configure your setup!\n")
        
        if not preset:
            click.echo("🖥️  " + click.style("Available presets:", fg="green", bold=True))
            presets = [
                ("cpu_small", "Small model optimized for CPU training"),
                ("gpu_medium", "Medium model optimized for single GPU"),
                ("gpu_large", "Large model for high-end GPU"),
                ("inference", "Configuration optimized for inference")
            ]
            
            for name, desc in presets:
                click.echo(f"  • {click.style(name, fg='cyan'):<12} - {desc}")
            
            click.echo()
            preset = click.prompt(
                "Choose a preset",
                type=click.Choice(['cpu_small', 'gpu_medium', 'gpu_large', 'inference']),
                default='cpu_small'
            )
        
        if not output:
            output = click.prompt("💾 Output file path", default=f"{preset}_config.json", type=str)
        
        click.echo(f"\n🚀 Creating {click.style(preset, fg='yellow')} configuration...")
    
    try:
        if preset:
            config = DefaultConfigs.get_preset(preset)
            click.echo(f"📋 Using {click.style(preset, fg='cyan')} preset")
        else:
            from .config import Config
            config = Config()
            click.echo("📋 Using default configuration")
        
        # Save configuration
        with open(output, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
        
        click.echo(f"✅ Configuration saved to {click.style(output, fg='green')}")
        
        # Show key settings
        if interactive:
            click.echo(f"\n📊 " + click.style("Key Settings:", fg="blue", bold=True))
            click.echo(f"  • Model layers: {config.model.num_layers}")
            click.echo(f"  • Embedding dim: {config.model.embedding_dim}")
            click.echo(f"  • Vocab size: {config.model.vocab_size}")
            click.echo(f"  • Batch size: {config.training.batch_size}")
            click.echo(f"  • Learning rate: {config.training.learning_rate}")
            click.echo(f"  • Device: {config.system.device}")
            
            click.echo(f"\n💡 " + click.style("Next steps:", fg="green"))
            click.echo(f"   llmbuilder config validate {output}")
            click.echo(f"   llmbuilder train model --config {output}")
    
    except Exception as e:
        click.echo(f"❌ Failed to create configuration: {e}")
        if interactive:
            click.echo("💡 Check that you have write permissions for the output directory")

@config.command()
@click.argument('config_path')
def validate(config_path):
    """Validate a configuration file."""
    from .config import load_config, validate_config
    
    click.echo(f"Validating configuration: {config_path}")
    
    try:
        config = load_config(config_path)
        is_valid = validate_config(config)
        
        if is_valid:
            click.echo("✓ Configuration is valid")
        else:
            click.echo("✗ Configuration has issues")
    except Exception as e:
        click.echo(f"✗ Validation failed: {e}")

@config.command()
def list():
    """List available configuration presets."""
    click.echo("Available configuration presets:")
    click.echo("  cpu_small   - Small model optimized for CPU training")
    click.echo("  gpu_medium  - Medium model optimized for single GPU")
    click.echo("  gpu_large   - Large model for high-end GPU")
    click.echo("  inference   - Configuration optimized for inference")

if __name__ == "__main__":
    main()