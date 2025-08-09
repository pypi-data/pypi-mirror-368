"""
Configuration validation utilities for LLMBuilder.

This module provides comprehensive validation for configuration objects
with detailed error messages and suggestions for fixes.
"""

import torch
from typing import List, Dict, Any, Tuple
from ..utils import ConfigurationError
from .defaults import Config, ModelConfig, TrainingConfig, DataConfig, TokenizerConfig, InferenceConfig, SystemConfig


class ConfigValidator:
    """Comprehensive configuration validator with detailed error reporting."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, config: Config) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a complete configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Validate individual components
        self._validate_model_config(config.model)
        self._validate_training_config(config.training)
        self._validate_data_config(config.data)
        self._validate_tokenizer_config(config.tokenizer)
        self._validate_inference_config(config.inference)
        self._validate_system_config(config.system)
        
        # Cross-component validation
        self._validate_cross_component(config)
        
        # Hardware-specific validation
        self._validate_hardware_compatibility(config)
        
        return len(self.errors) == 0, self.errors.copy(), self.warnings.copy()
    
    def _validate_model_config(self, config: ModelConfig) -> None:
        """Validate model configuration."""
        # Architecture constraints
        if config.embedding_dim % config.num_heads != 0:
            self.errors.append(
                f"Model embedding_dim ({config.embedding_dim}) must be divisible by "
                f"num_heads ({config.num_heads}). "
                f"Suggestion: Use embedding_dim={config.embedding_dim - (config.embedding_dim % config.num_heads)} "
                f"or num_heads={self._find_divisor(config.embedding_dim, config.num_heads)}"
            )
        
        # Memory estimation warnings
        param_count = self._estimate_parameters(config)
        if param_count > 1e9:  # 1B parameters
            self.warnings.append(
                f"Large model detected (~{param_count/1e6:.1f}M parameters). "
                "Consider using gradient checkpointing and mixed precision training."
            )
        
        # Sequence length warnings
        if config.max_seq_length > 4096:
            self.warnings.append(
                f"Very long sequence length ({config.max_seq_length}). "
                "This may require significant memory. Consider using gradient checkpointing."
            )
        
        # Dropout validation
        if config.dropout < 0 or config.dropout > 1:
            self.errors.append(f"Dropout must be between 0 and 1, got {config.dropout}")
        
        # Architecture-specific validations
        if config.num_layers > 48:
            self.warnings.append(
                f"Very deep model ({config.num_layers} layers). "
                "Consider using residual scaling or layer normalization adjustments."
            )
    
    def _validate_training_config(self, config: TrainingConfig) -> None:
        """Validate training configuration."""
        # Learning rate validation
        if config.learning_rate > 1e-2:
            self.warnings.append(
                f"High learning rate ({config.learning_rate}). "
                "Consider using a lower learning rate or learning rate scheduling."
            )
        
        if config.learning_rate < 1e-6:
            self.warnings.append(
                f"Very low learning rate ({config.learning_rate}). "
                "Training may be very slow."
            )
        
        # Batch size validation
        if config.batch_size > 128:
            self.warnings.append(
                f"Large batch size ({config.batch_size}). "
                "Ensure sufficient GPU memory is available."
            )
        
        # Gradient clipping
        if config.gradient_clip_norm > 10:
            self.warnings.append(
                f"High gradient clipping norm ({config.gradient_clip_norm}). "
                "Consider using a lower value (typically 0.5-2.0)."
            )
        
        # Optimizer parameters
        if config.beta1 < 0 or config.beta1 >= 1:
            self.errors.append(f"beta1 must be in [0, 1), got {config.beta1}")
        
        if config.beta2 < 0 or config.beta2 >= 1:
            self.errors.append(f"beta2 must be in [0, 1), got {config.beta2}")
    
    def _validate_data_config(self, config: DataConfig) -> None:
        """Validate data configuration."""
        # Split validation
        total_split = config.validation_split + config.test_split
        if total_split >= 1.0:
            self.errors.append(
                f"validation_split + test_split ({total_split}) must be < 1.0. "
                f"Current: validation={config.validation_split}, test={config.test_split}"
            )
        
        # Length validation
        if config.max_length < config.min_length:
            self.errors.append(
                f"max_length ({config.max_length}) must be >= min_length ({config.min_length})"
            )
        
        # Stride validation
        if config.stride > config.max_length:
            self.warnings.append(
                f"Stride ({config.stride}) is larger than max_length ({config.max_length}). "
                "This may cause data loss."
            )
    
    def _validate_tokenizer_config(self, config: TokenizerConfig) -> None:
        """Validate tokenizer configuration."""
        # Vocabulary size validation
        if config.vocab_size < 1000:
            self.warnings.append(
                f"Small vocabulary size ({config.vocab_size}). "
                "Consider using at least 8000 for better performance."
            )
        
        if config.vocab_size > 100000:
            self.warnings.append(
                f"Large vocabulary size ({config.vocab_size}). "
                "This will increase model size and memory usage."
            )
        
        # Character coverage validation
        if config.character_coverage < 0.95:
            self.warnings.append(
                f"Low character coverage ({config.character_coverage}). "
                "Consider increasing to 0.9995 for better text handling."
            )
    
    def _validate_inference_config(self, config: InferenceConfig) -> None:
        """Validate inference configuration."""
        # Temperature validation
        if config.temperature > 2.0:
            self.warnings.append(
                f"High temperature ({config.temperature}) may produce incoherent text."
            )
        
        if config.temperature < 0.1:
            self.warnings.append(
                f"Low temperature ({config.temperature}) may produce repetitive text."
            )
        
        # Top-k validation
        if config.top_k > 200:
            self.warnings.append(
                f"High top_k ({config.top_k}) may slow down generation."
            )
        
        # Repetition penalty validation
        if config.repetition_penalty > 2.0:
            self.warnings.append(
                f"High repetition penalty ({config.repetition_penalty}) may produce unnatural text."
            )
    
    def _validate_system_config(self, config: SystemConfig) -> None:
        """Validate system configuration."""
        # Device validation
        if config.device == "cuda" and not torch.cuda.is_available():
            self.errors.append(
                "CUDA device specified but CUDA is not available. "
                "Install PyTorch with CUDA support or use device='cpu'."
            )
        
        if config.device == "mps" and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
            self.errors.append(
                "MPS device specified but MPS is not available. "
                "Use device='cpu' or 'cuda' instead."
            )
        
        # Mixed precision validation
        if config.mixed_precision and config.device == "cpu":
            self.warnings.append(
                "Mixed precision training is not supported on CPU. "
                "Setting mixed_precision=False."
            )
        
        # Worker validation
        if config.num_workers > 16:
            self.warnings.append(
                f"High number of workers ({config.num_workers}) may cause overhead."
            )
    
    def _validate_cross_component(self, config: Config) -> None:
        """Validate relationships between different configuration components."""
        # Vocabulary size consistency
        if config.model.vocab_size != config.tokenizer.vocab_size:
            self.errors.append(
                f"Model vocab_size ({config.model.vocab_size}) must match "
                f"tokenizer vocab_size ({config.tokenizer.vocab_size})"
            )
        
        # Sequence length consistency
        if config.model.max_seq_length < config.data.max_length:
            self.errors.append(
                f"Model max_seq_length ({config.model.max_seq_length}) must be >= "
                f"data max_length ({config.data.max_length})"
            )
        
        # Memory estimation is done in hardware compatibility check
    
    def _validate_hardware_compatibility(self, config: Config) -> None:
        """Validate hardware compatibility."""
        if config.system.device == "cuda" and torch.cuda.is_available():
            # GPU memory estimation
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9  # GB
            estimated_memory = self._estimate_memory_usage(config)
            
            if estimated_memory > gpu_memory * 0.9:  # 90% threshold
                self.warnings.append(
                    f"Estimated memory usage ({estimated_memory:.1f}GB) may exceed "
                    f"available GPU memory ({gpu_memory:.1f}GB). "
                    "Consider reducing batch size or model size."
                )
    
    def _estimate_parameters(self, config: ModelConfig) -> int:
        """Estimate the number of model parameters."""
        # Embedding parameters
        embedding_params = config.vocab_size * config.embedding_dim
        
        # Transformer block parameters (approximate)
        # Each layer has: attention (4 * d^2) + feedforward (8 * d^2) + layer norms
        layer_params = config.num_layers * (12 * config.embedding_dim ** 2 + 2 * config.embedding_dim)
        
        # Output layer
        output_params = config.vocab_size * config.embedding_dim
        
        return embedding_params + layer_params + output_params
    
    def _estimate_memory_usage(self, config: Config) -> float:
        """Estimate memory usage in GB."""
        param_count = self._estimate_parameters(config.model)
        
        # Model parameters (4 bytes per parameter for float32)
        model_memory = param_count * 4 / 1e9
        
        # Gradients (same size as parameters)
        gradient_memory = model_memory
        
        # Optimizer states (Adam: 2x parameters)
        optimizer_memory = model_memory * 2
        
        # Activations (rough estimate based on batch size and sequence length)
        activation_memory = (
            config.training.batch_size * 
            config.model.max_seq_length * 
            config.model.embedding_dim * 
            config.model.num_layers * 4 / 1e9
        )
        
        total_memory = model_memory + gradient_memory + optimizer_memory + activation_memory
        
        # Mixed precision reduces memory by ~40%
        if config.system.mixed_precision:
            total_memory *= 0.6
        
        return total_memory
    
    def _find_divisor(self, embedding_dim: int, target_heads: int) -> int:
        """Find a suitable number of heads that divides embedding_dim."""
        for heads in range(target_heads, 0, -1):
            if embedding_dim % heads == 0:
                return heads
        return 1


def validate_config(config: Config) -> Tuple[bool, List[str], List[str]]:
    """
    Validate a configuration and return detailed results.
    
    Args:
        config: Configuration to validate
        
    Returns:
        Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
    """
    validator = ConfigValidator()
    return validator.validate(config)


def validate_config_strict(config: Config) -> bool:
    """
    Validate a configuration and raise an exception if invalid.
    
    Args:
        config: Configuration to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    is_valid, errors, warnings = validate_config(config)
    
    if not is_valid:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        if warnings:
            error_msg += "\n\nWarnings:\n" + "\n".join(f"  - {warning}" for warning in warnings)
        raise ConfigurationError(error_msg)
    
    return True