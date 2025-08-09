"""
Utilities module for LLMBuilder.

This module provides common utilities including logging, checkpoint management,
device management, and other helper functions.
"""

# Import utility modules
from .logger import (
    LLMBuilderLogger,
    setup_logging,
    get_logger,
    log_config,
    log_system_info,
)
from .checkpoint import (
    CheckpointManager,
    save_checkpoint,
    load_checkpoint,
    list_checkpoints,
    get_best_checkpoint,
    get_latest_checkpoint,
)
from .device import (
    DeviceManager,
    get_optimal_device,
    get_device_info,
    get_memory_info,
    clear_memory,
    estimate_model_memory,
    check_memory_requirements,
    get_optimization_recommendations,
    validate_device_compatibility,
)

# Custom exception hierarchy
class LLMBuilderError(Exception):
    """
    Base exception for llmbuilder package.
    
    All custom exceptions in the package inherit from this base class.
    Provides common functionality for error handling and logging.
    """
    
    def __init__(self, message: str, details: dict = None, cause: Exception = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
    
    def __str__(self) -> str:
        """Return formatted error message."""
        msg = self.message
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            msg += f" (Details: {details_str})"
        if self.cause:
            msg += f" (Caused by: {self.cause})"
        return msg
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None
        }


class ConfigurationError(LLMBuilderError):
    """Configuration related errors."""
    
    def __init__(self, message: str, config_path: str = None, invalid_keys: list = None, **kwargs):
        details = {}
        if config_path:
            details["config_path"] = config_path
        if invalid_keys:
            details["invalid_keys"] = invalid_keys
        super().__init__(message, details, **kwargs)


class DataError(LLMBuilderError):
    """Data loading and processing errors."""
    
    def __init__(self, message: str, file_path: str = None, data_format: str = None, **kwargs):
        details = {}
        if file_path:
            details["file_path"] = file_path
        if data_format:
            details["data_format"] = data_format
        super().__init__(message, details, **kwargs)


class TokenizerError(LLMBuilderError):
    """Tokenizer training and loading errors."""
    
    def __init__(self, message: str, tokenizer_path: str = None, vocab_size: int = None, **kwargs):
        details = {}
        if tokenizer_path:
            details["tokenizer_path"] = tokenizer_path
        if vocab_size:
            details["vocab_size"] = vocab_size
        super().__init__(message, details, **kwargs)


class ModelError(LLMBuilderError):
    """Model creation and loading errors."""
    
    def __init__(self, message: str, model_path: str = None, architecture: str = None, **kwargs):
        details = {}
        if model_path:
            details["model_path"] = model_path
        if architecture:
            details["architecture"] = architecture
        super().__init__(message, details, **kwargs)


class TrainingError(LLMBuilderError):
    """Training and fine-tuning errors."""
    
    def __init__(self, message: str, epoch: int = None, step: int = None, loss: float = None, **kwargs):
        details = {}
        if epoch is not None:
            details["epoch"] = epoch
        if step is not None:
            details["step"] = step
        if loss is not None:
            details["loss"] = loss
        super().__init__(message, details, **kwargs)


class InferenceError(LLMBuilderError):
    """Text generation and inference errors."""
    
    def __init__(self, message: str, model_name: str = None, prompt_length: int = None, **kwargs):
        details = {}
        if model_name:
            details["model_name"] = model_name
        if prompt_length is not None:
            details["prompt_length"] = prompt_length
        super().__init__(message, details, **kwargs)


class ExportError(LLMBuilderError):
    """Model export and conversion errors."""
    
    def __init__(self, message: str, export_format: str = None, output_path: str = None, **kwargs):
        details = {}
        if export_format:
            details["export_format"] = export_format
        if output_path:
            details["output_path"] = output_path
        super().__init__(message, details, **kwargs)


class CheckpointError(LLMBuilderError):
    """Checkpoint saving and loading errors."""
    
    def __init__(self, message: str, checkpoint_path: str = None, operation: str = None, **kwargs):
        details = {}
        if checkpoint_path:
            details["checkpoint_path"] = checkpoint_path
        if operation:
            details["operation"] = operation
        super().__init__(message, details, **kwargs)


class DeviceError(LLMBuilderError):
    """Device and hardware related errors."""
    
    def __init__(self, message: str, device: str = None, available_devices: list = None, **kwargs):
        details = {}
        if device:
            details["device"] = device
        if available_devices:
            details["available_devices"] = available_devices
        super().__init__(message, details, **kwargs)

__all__ = [
    # Exceptions
    "LLMBuilderError",
    "ConfigurationError",
    "DataError",
    "TokenizerError",
    "ModelError", 
    "TrainingError",
    "InferenceError",
    "ExportError",
    "CheckpointError",
    "DeviceError",
    
    # Logging utilities
    "LLMBuilderLogger",
    "setup_logging",
    "get_logger",
    "log_config",
    "log_system_info",
    
    # Checkpoint management
    "CheckpointManager",
    "save_checkpoint",
    "load_checkpoint",
    "list_checkpoints",
    "get_best_checkpoint",
    "get_latest_checkpoint",
    
    # Device management
    "DeviceManager",
    "get_optimal_device",
    "get_device_info",
    "get_memory_info",
    "clear_memory",
    "estimate_model_memory",
    "check_memory_requirements",
    "get_optimization_recommendations",
    "validate_device_compatibility",
]