"""
Configuration management module for LLMBuilder.

This module provides utilities for loading, validating, and managing
configuration settings for models, training, and other components.
"""

from .defaults import (
    Config,
    ModelConfig,
    TrainingConfig,
    DataConfig,
    TokenizerConfig,
    InferenceConfig,
    SystemConfig,
    PathConfig,
    DefaultConfigs,
)
from .loader import (
    ConfigManager,
    load_config,
    get_default_config,
    save_config,
    merge_configs,
    validate_config as validate_config_basic,
    get_config_template,
)
from .validation import (
    ConfigValidator,
    validate_config,
    validate_config_strict,
)

__all__ = [
    # Configuration classes
    "Config",
    "ModelConfig",
    "TrainingConfig", 
    "DataConfig",
    "TokenizerConfig",
    "InferenceConfig",
    "SystemConfig",
    "PathConfig",
    "DefaultConfigs",
    
    # Configuration management
    "ConfigManager",
    "load_config",
    "get_default_config",
    "save_config",
    "merge_configs",
    "get_config_template",
    
    # Validation
    "ConfigValidator",
    "validate_config",
    "validate_config_strict",
    "validate_config_basic",
]