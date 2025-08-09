"""
Model building and management module for LLMBuilder.

This module provides comprehensive model building, loading, saving,
and management capabilities for GPT-style transformer models.
"""

from .gpt import (
    GPTModel,
    GPTModelMetadata,
    MultiHeadAttention,
    MLP,
    TransformerBlock,
)
from .builder import (
    ModelBuilder,
    build_model,
    load_model,
    save_model,
    validate_model,
)

__all__ = [
    # GPT Model components
    "GPTModel",
    "GPTModelMetadata", 
    "MultiHeadAttention",
    "MLP",
    "TransformerBlock",
    
    # Model builder and management
    "ModelBuilder",
    "build_model",
    "load_model", 
    "save_model",
    "validate_model",
]