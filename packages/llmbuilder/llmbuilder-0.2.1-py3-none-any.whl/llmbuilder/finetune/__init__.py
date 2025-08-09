"""
Fine-tuning module for LLMBuilder.

This module provides comprehensive fine-tuning capabilities including
the FineTuner class, LoRA adaptation, and optimizations for small datasets.
"""

from .finetune import (
    FineTuner,
    FineTuningConfig,
    LoRALayer,
    finetune_model,
    create_lora_config,
    create_small_dataset_config,
)

__all__ = [
    # Main fine-tuning components
    "FineTuner",
    "FineTuningConfig",
    "LoRALayer",
    
    # Fine-tuning API functions
    "finetune_model",
    
    # Configuration helpers
    "create_lora_config",
    "create_small_dataset_config",
]