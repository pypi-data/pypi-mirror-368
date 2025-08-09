"""
LLMBuilder - A comprehensive toolkit for building, training, and deploying language models.

This package provides a modular approach to language model development with support for:
- Data loading and preprocessing
- Tokenizer training and management
- Model building and configuration
- Training and fine-tuning pipelines
- Text generation and inference
- Model export in various formats
"""

__version__ = "0.1.1"
__author__ = "Qubase"
__email__ = "contact@qubase.in"

# Lazy import machinery to keep import time low
from typing import Optional, Any
import importlib

# Main API exports for easy access
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Core modules
    "config",
    "data", 
    "tokenizer",
    "model",
    "training",
    "finetune",
    "inference",
    "export",
    "utils",
    
    # Convenience functions (to be implemented)
    "load_config",
    "build_model",
    "train_model",
    "generate_text",
    "interactive_cli",
    "finetune_model",
]

# Lazy-load submodules on first attribute access (PEP 562)
_SUBMODULES = {"config", "data", "tokenizer", "model", "training", "finetune", "inference", "export", "utils"}

def __getattr__(name: str):
    if name in _SUBMODULES:
        mod = importlib.import_module(f".{name}", __name__)
        globals()[name] = mod
        return mod
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Convenience functions for common operations
def load_config(path: Optional[str] = None, preset: Optional[str] = None) -> Any:
    """Load configuration from file or use preset.

    Args:
        path: Optional path to a JSON/YAML configuration file.
        preset: Optional name of a built-in preset.

    Returns:
        A configuration object suitable for model/training builders.
    """
    from .config import load_config as _load_config
    return _load_config(path, preset)

def build_model(config: Any) -> Any:
    """Build a model from configuration."""
    from .model import build_model as _build_model
    return _build_model(config)

def train_model(model: Any, dataset: Any, config: Any) -> Any:
    """Train a model with the given dataset and configuration."""
    from .training import train_model as _train_model
    return _train_model(model, dataset, config)

def generate_text(model_path: str, tokenizer_path: str, prompt: str, **kwargs: Any) -> str:
    """
    Generate text using a trained model.
    
    Args:
        model_path: Path to trained model checkpoint
        tokenizer_path: Path to tokenizer directory
        prompt: Input text prompt
        **kwargs: Additional generation parameters (temperature, top_k, top_p, etc.)
        
    Returns:
        Generated text string
        
    Example:
        >>> text = llmbuilder.generate_text(
        ...     model_path="model.pt",
        ...     tokenizer_path="tokenizer/",
        ...     prompt="Hello world",
        ...     max_new_tokens=50,
        ...     temperature=0.8
        ... )
    """
    from .inference import generate_text as _generate_text
    return _generate_text(model_path, tokenizer_path, prompt, **kwargs)

def interactive_cli(model_path: str, tokenizer_path: str, **kwargs: Any) -> Any:
    """
    Start an interactive CLI for text generation.
    
    Args:
        model_path: Path to trained model checkpoint
        tokenizer_path: Path to tokenizer directory
        **kwargs: Additional configuration parameters
        
    Example:
        >>> llmbuilder.interactive_cli(
        ...     model_path="model.pt",
        ...     tokenizer_path="tokenizer/"
        ... )
    """
    from .inference import interactive_cli as _interactive_cli
    return _interactive_cli(model_path, tokenizer_path, **kwargs)

def finetune_model(model: Any, dataset: Any, config: Any, **kwargs: Any) -> Any:
    """Fine-tune a model with the given dataset and configuration."""
    from .finetune import finetune_model as _finetune_model
    return _finetune_model(model, dataset, config, **kwargs)