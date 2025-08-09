"""
Logging utilities for LLMBuilder.

This module provides structured logging with support for multiple outputs,
log levels, and JSON formatting for better log analysis.
"""

import logging
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime
import traceback


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, '')
        reset = self.RESET
        
        # Create colored level name
        colored_level = f"{color}{record.levelname:8}{reset}"
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Format message
        message = record.getMessage()
        
        # Add location info for debug level
        if record.levelno <= logging.DEBUG:
            location = f"{record.module}:{record.funcName}:{record.lineno}"
            return f"{timestamp} {colored_level} [{location}] {message}"
        else:
            return f"{timestamp} {colored_level} {message}"


class LLMBuilderLogger:
    """Main logger class for LLMBuilder with structured logging capabilities."""
    
    def __init__(self, name: str = "llmbuilder"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.handlers_configured = False
    
    def setup(
        self,
        level: Union[str, int] = logging.INFO,
        console_output: bool = True,
        file_output: Optional[str] = None,
        json_format: bool = False,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> None:
        """
        Set up logging configuration.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console_output: Whether to output to console
            file_output: Path to log file (optional)
            json_format: Whether to use JSON formatting
            max_file_size: Maximum log file size in bytes
            backup_count: Number of backup files to keep
        """
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set level
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        self.logger.setLevel(level)
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            if json_format:
                console_handler.setFormatter(JSONFormatter())
            else:
                console_handler.setFormatter(ColoredFormatter())
            self.logger.addHandler(console_handler)
        
        # File handler
        if file_output:
            from logging.handlers import RotatingFileHandler
            
            # Ensure directory exists
            log_path = Path(file_output)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                file_output,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            
            if json_format:
                file_handler.setFormatter(JSONFormatter())
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
                )
                file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
        
        self.handlers_configured = True
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        kwargs['exc_info'] = True
        self._log(logging.ERROR, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal logging method."""
        if not self.handlers_configured:
            self.setup()  # Use default setup
        
        # Extract extra fields
        extra_fields = {k: v for k, v in kwargs.items() if k != 'exc_info'}
        
        # Create log record with extra fields
        extra = {'extra_fields': extra_fields} if extra_fields else {}
        if 'exc_info' in kwargs:
            extra['exc_info'] = kwargs['exc_info']
        
        self.logger.log(level, message, extra=extra)
    
    def log_training_metrics(
        self,
        epoch: int,
        step: int,
        loss: float,
        learning_rate: float,
        **metrics
    ) -> None:
        """Log training metrics in a structured format."""
        self.info(
            f"Training - Epoch {epoch}, Step {step}",
            epoch=epoch,
            step=step,
            loss=loss,
            learning_rate=learning_rate,
            **metrics
        )
    
    def log_model_info(
        self,
        model_name: str,
        parameters: int,
        memory_usage: Optional[float] = None,
        **info
    ) -> None:
        """Log model information."""
        self.info(
            f"Model: {model_name} ({parameters:,} parameters)",
            model_name=model_name,
            parameters=parameters,
            memory_usage=memory_usage,
            **info
        )
    
    def log_data_info(
        self,
        dataset_size: int,
        vocab_size: int,
        sequence_length: int,
        **info
    ) -> None:
        """Log dataset information."""
        self.info(
            f"Dataset: {dataset_size:,} samples, vocab={vocab_size}, seq_len={sequence_length}",
            dataset_size=dataset_size,
            vocab_size=vocab_size,
            sequence_length=sequence_length,
            **info
        )
    
    def create_child_logger(self, name: str) -> 'LLMBuilderLogger':
        """Create a child logger with the same configuration."""
        child_name = f"{self.name}.{name}"
        child_logger = LLMBuilderLogger(child_name)
        
        # Copy handlers from parent
        if self.handlers_configured:
            child_logger.logger.handlers = self.logger.handlers.copy()
            child_logger.logger.setLevel(self.logger.level)
            child_logger.handlers_configured = True
        
        return child_logger


# Global logger instance
_global_logger = LLMBuilderLogger()


def setup_logging(
    level: Union[str, int] = logging.INFO,
    console_output: bool = True,
    file_output: Optional[str] = None,
    json_format: bool = False,
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> LLMBuilderLogger:
    """
    Set up global logging configuration.
    
    Args:
        level: Logging level
        console_output: Whether to output to console
        file_output: Path to log file
        json_format: Whether to use JSON formatting
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup files to keep
        
    Returns:
        LLMBuilderLogger: Configured logger instance
    """
    _global_logger.setup(
        level=level,
        console_output=console_output,
        file_output=file_output,
        json_format=json_format,
        max_file_size=max_file_size,
        backup_count=backup_count
    )
    return _global_logger


def get_logger(name: Optional[str] = None) -> LLMBuilderLogger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (creates child logger if provided)
        
    Returns:
        LLMBuilderLogger: Logger instance
    """
    if name:
        return _global_logger.create_child_logger(name)
    return _global_logger


def log_config(config: Dict[str, Any]) -> None:
    """Log configuration information."""
    _global_logger.info("Configuration loaded", **config)


def log_system_info() -> None:
    """Log system information."""
    import platform
    import torch
    
    system_info = {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'torch_version': torch.__version__,
        'cuda_available': torch.cuda.is_available(),
    }
    
    if torch.cuda.is_available():
        system_info.update({
            'cuda_version': torch.version.cuda,
            'gpu_count': torch.cuda.device_count(),
            'gpu_name': torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else None,
        })
    
    _global_logger.info("System information", **system_info)