"""
Inference and text generation module for LLMBuilder.

This module provides text generation capabilities, interactive CLI,
and various sampling strategies for trained models.
"""

from .generate import TextGenerator, GenerationConfig, generate_text
from .cli import InferenceCLI, interactive_cli

__all__ = [
    # Core generation classes
    "TextGenerator",
    "GenerationConfig",
    "generate_text",
    
    # Interactive CLI
    "InferenceCLI", 
    "interactive_cli",
]