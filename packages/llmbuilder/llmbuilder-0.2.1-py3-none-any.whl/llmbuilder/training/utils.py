"""
Training utilities for LLMBuilder.

This module provides training-specific utilities including metrics tracking,
learning rate scheduling, gradient utilities, and training helpers.
"""

import time
import torch
import torch.nn as nn
from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path
import json
import math

from ..utils import TrainingError, get_logger

logger = get_logger("training.utils")


class MetricsTracker:
    """
    Tracks and manages training metrics.
    
    Provides functionality for recording, aggregating, and saving
    training metrics throughout the training process.
    """
    
    def __init__(self):
        """Initialize metrics tracker."""
        self.metrics = {}
        self.history = []
        self.start_time = time.time()
        
    def update(self, **kwargs) -> None:
        """
        Update metrics with new values.
        
        Args:
            **kwargs: Metric name-value pairs
        """
        timestamp = time.time() - self.start_time
        
        # Update current metrics
        for key, value in kwargs.items():
            if key not in self.metrics:
                self.metrics[key] = []
            self.metrics[key].append(value)
        
        # Add to history with timestamp
        entry = {'timestamp': timestamp, **kwargs}
        self.history.append(entry)
    
    def get_latest(self, metric_name: str) -> Optional[float]:
        """
        Get latest value for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Latest value or None if metric doesn't exist
        """
        if metric_name in self.metrics and self.metrics[metric_name]:
            return self.metrics[metric_name][-1]
        return None
    
    def get_average(self, metric_name: str, last_n: Optional[int] = None) -> Optional[float]:
        """
        Get average value for a metric.
        
        Args:
            metric_name: Name of the metric
            last_n: Number of recent values to average (None for all)
            
        Returns:
            Average value or None if metric doesn't exist
        """
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return None
        
        values = self.metrics[metric_name]
        if last_n is not None:
            values = values[-last_n:]
        
        return sum(values) / len(values)
    
    def get_best(self, metric_name: str, minimize: bool = True) -> Optional[float]:
        """
        Get best value for a metric.
        
        Args:
            metric_name: Name of the metric
            minimize: Whether lower values are better
            
        Returns:
            Best value or None if metric doesn't exist
        """
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return None
        
        values = self.metrics[metric_name]
        return min(values) if minimize else max(values)
    
    def save_history(self, filepath: Union[str, Path]) -> None:
        """
        Save metrics history to file.
        
        Args:
            filepath: Path to save file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        logger.info(f"Metrics history saved to {filepath}")
    
    def load_history(self, filepath: Union[str, Path]) -> None:
        """
        Load metrics history from file.
        
        Args:
            filepath: Path to load file
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.warning(f"Metrics file not found: {filepath}")
            return
        
        with open(filepath, 'r') as f:
            self.history = json.load(f)
        
        # Rebuild metrics dict
        self.metrics = {}
        for entry in self.history:
            for key, value in entry.items():
                if key != 'timestamp':
                    if key not in self.metrics:
                        self.metrics[key] = []
                    self.metrics[key].append(value)
        
        logger.info(f"Metrics history loaded from {filepath}")
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics = {}
        self.history = []
        self.start_time = time.time()
    
    def summary(self) -> Dict[str, Any]:
        """
        Get summary of all metrics.
        
        Returns:
            Dict with metric summaries
        """
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    'count': len(values),
                    'latest': values[-1],
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        return summary


class LearningRateScheduler:
    """
    Custom learning rate scheduler with various scheduling strategies.
    """
    
    def __init__(self, 
                 optimizer: torch.optim.Optimizer,
                 schedule_type: str = 'cosine',
                 **kwargs):
        """
        Initialize learning rate scheduler.
        
        Args:
            optimizer: PyTorch optimizer
            schedule_type: Type of schedule ('cosine', 'linear', 'exponential', 'step')
            **kwargs: Schedule-specific parameters
        """
        self.optimizer = optimizer
        self.schedule_type = schedule_type.lower()
        self.kwargs = kwargs
        self.step_count = 0
        
        # Store initial learning rates
        self.base_lrs = [group['lr'] for group in optimizer.param_groups]
        
        logger.info(f"Learning rate scheduler initialized: {schedule_type}")
    
    def step(self) -> None:
        """Update learning rates."""
        self.step_count += 1
        
        for i, param_group in enumerate(self.optimizer.param_groups):
            param_group['lr'] = self._get_lr(i)
    
    def _get_lr(self, param_group_idx: int) -> float:
        """
        Calculate learning rate for a parameter group.
        
        Args:
            param_group_idx: Index of parameter group
            
        Returns:
            New learning rate
        """
        base_lr = self.base_lrs[param_group_idx]
        
        if self.schedule_type == 'cosine':
            total_steps = self.kwargs.get('total_steps', 1000)
            min_lr = self.kwargs.get('min_lr', 0.0)
            
            progress = min(self.step_count / total_steps, 1.0)
            lr = min_lr + (base_lr - min_lr) * 0.5 * (1 + math.cos(math.pi * progress))
            
        elif self.schedule_type == 'linear':
            total_steps = self.kwargs.get('total_steps', 1000)
            warmup_steps = self.kwargs.get('warmup_steps', 0)
            
            if self.step_count < warmup_steps:
                lr = base_lr * self.step_count / max(1, warmup_steps)
            else:
                progress = (self.step_count - warmup_steps) / max(1, total_steps - warmup_steps)
                lr = base_lr * max(0.0, 1.0 - progress)
            
        elif self.schedule_type == 'exponential':
            decay_rate = self.kwargs.get('decay_rate', 0.95)
            decay_steps = self.kwargs.get('decay_steps', 100)
            
            lr = base_lr * (decay_rate ** (self.step_count // decay_steps))
            
        elif self.schedule_type == 'step':
            step_size = self.kwargs.get('step_size', 100)
            gamma = self.kwargs.get('gamma', 0.1)
            
            lr = base_lr * (gamma ** (self.step_count // step_size))
            
        else:
            lr = base_lr
        
        return lr
    
    def get_last_lr(self) -> List[float]:
        """Get last learning rates for all parameter groups."""
        return [self._get_lr(i) for i in range(len(self.base_lrs))]


class GradientClipper:
    """
    Gradient clipping utilities with various clipping strategies.
    """
    
    @staticmethod
    def clip_grad_norm(parameters, max_norm: float, norm_type: float = 2.0) -> float:
        """
        Clip gradients by norm.
        
        Args:
            parameters: Model parameters
            max_norm: Maximum norm value
            norm_type: Type of norm to use
            
        Returns:
            Total norm of gradients
        """
        return torch.nn.utils.clip_grad_norm_(parameters, max_norm, norm_type)
    
    @staticmethod
    def clip_grad_value(parameters, clip_value: float) -> None:
        """
        Clip gradients by value.
        
        Args:
            parameters: Model parameters
            clip_value: Maximum absolute value
        """
        torch.nn.utils.clip_grad_value_(parameters, clip_value)
    
    @staticmethod
    def get_grad_norm(parameters, norm_type: float = 2.0) -> float:
        """
        Calculate gradient norm.
        
        Args:
            parameters: Model parameters
            norm_type: Type of norm to use
            
        Returns:
            Gradient norm
        """
        parameters = [p for p in parameters if p.grad is not None]
        
        if not parameters:
            return 0.0
        
        device = parameters[0].grad.device
        
        if norm_type == float('inf'):
            total_norm = max(p.grad.detach().abs().max().to(device) for p in parameters)
        else:
            total_norm = torch.norm(
                torch.stack([torch.norm(p.grad.detach(), norm_type).to(device) for p in parameters]),
                norm_type
            )
        
        return total_norm.item()


class EarlyStopping:
    """
    Early stopping utility to prevent overfitting.
    """
    
    def __init__(self, 
                 patience: int = 10,
                 min_delta: float = 0.0,
                 restore_best_weights: bool = True):
        """
        Initialize early stopping.
        
        Args:
            patience: Number of epochs to wait for improvement
            min_delta: Minimum change to qualify as improvement
            restore_best_weights: Whether to restore best weights when stopping
        """
        self.patience = patience
        self.min_delta = min_delta
        self.restore_best_weights = restore_best_weights
        
        self.best_loss = float('inf')
        self.counter = 0
        self.best_weights = None
        self.should_stop = False
    
    def __call__(self, val_loss: float, model: nn.Module) -> bool:
        """
        Check if training should stop.
        
        Args:
            val_loss: Current validation loss
            model: Model to potentially save weights from
            
        Returns:
            True if training should stop
        """
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            
            if self.restore_best_weights:
                self.best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            self.counter += 1
            
            if self.counter >= self.patience:
                self.should_stop = True
                
                if self.restore_best_weights and self.best_weights:
                    model.load_state_dict(self.best_weights)
                    logger.info("Restored best weights")
        
        return self.should_stop


class TrainingTimer:
    """
    Utility for tracking training time and estimating completion.
    """
    
    def __init__(self):
        """Initialize training timer."""
        self.start_time = None
        self.epoch_times = []
        self.step_times = []
    
    def start(self) -> None:
        """Start timing."""
        self.start_time = time.time()
    
    def epoch_start(self) -> float:
        """Mark start of epoch."""
        return time.time()
    
    def epoch_end(self, epoch_start_time: float) -> float:
        """
        Mark end of epoch.
        
        Args:
            epoch_start_time: Time when epoch started
            
        Returns:
            Epoch duration
        """
        epoch_time = time.time() - epoch_start_time
        self.epoch_times.append(epoch_time)
        return epoch_time
    
    def step_start(self) -> float:
        """Mark start of step."""
        return time.time()
    
    def step_end(self, step_start_time: float) -> float:
        """
        Mark end of step.
        
        Args:
            step_start_time: Time when step started
            
        Returns:
            Step duration
        """
        step_time = time.time() - step_start_time
        self.step_times.append(step_time)
        
        # Keep only recent step times
        if len(self.step_times) > 100:
            self.step_times.pop(0)
        
        return step_time
    
    def get_elapsed_time(self) -> float:
        """Get total elapsed time."""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def get_average_epoch_time(self) -> float:
        """Get average epoch time."""
        if not self.epoch_times:
            return 0.0
        return sum(self.epoch_times) / len(self.epoch_times)
    
    def get_average_step_time(self) -> float:
        """Get average step time."""
        if not self.step_times:
            return 0.0
        return sum(self.step_times) / len(self.step_times)
    
    def estimate_remaining_time(self, current_epoch: int, total_epochs: int) -> float:
        """
        Estimate remaining training time.
        
        Args:
            current_epoch: Current epoch number
            total_epochs: Total number of epochs
            
        Returns:
            Estimated remaining time in seconds
        """
        if not self.epoch_times or current_epoch >= total_epochs:
            return 0.0
        
        avg_epoch_time = self.get_average_epoch_time()
        remaining_epochs = total_epochs - current_epoch - 1
        
        return avg_epoch_time * remaining_epochs
    
    def format_time(self, seconds: float) -> str:
        """
        Format seconds to human-readable string.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


def count_parameters(model: nn.Module, trainable_only: bool = True) -> int:
    """
    Count model parameters.
    
    Args:
        model: PyTorch model
        trainable_only: Whether to count only trainable parameters
        
    Returns:
        Number of parameters
    """
    if trainable_only:
        return sum(p.numel() for p in model.parameters() if p.requires_grad)
    else:
        return sum(p.numel() for p in model.parameters())


def get_model_size_mb(model: nn.Module) -> float:
    """
    Get model size in megabytes.
    
    Args:
        model: PyTorch model
        
    Returns:
        Model size in MB
    """
    param_size = 0
    buffer_size = 0
    
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    
    size_mb = (param_size + buffer_size) / (1024 * 1024)
    return size_mb


def calculate_perplexity(loss: float) -> float:
    """
    Calculate perplexity from loss.
    
    Args:
        loss: Cross-entropy loss
        
    Returns:
        Perplexity value
    """
    return math.exp(loss)


def warmup_lr_schedule(step: int, warmup_steps: int, base_lr: float) -> float:
    """
    Linear warmup learning rate schedule.
    
    Args:
        step: Current step
        warmup_steps: Number of warmup steps
        base_lr: Base learning rate
        
    Returns:
        Learning rate for current step
    """
    if step < warmup_steps:
        return base_lr * step / max(1, warmup_steps)
    return base_lr


def cosine_annealing_lr_schedule(step: int, 
                                total_steps: int, 
                                base_lr: float, 
                                min_lr: float = 0.0) -> float:
    """
    Cosine annealing learning rate schedule.
    
    Args:
        step: Current step
        total_steps: Total number of steps
        base_lr: Base learning rate
        min_lr: Minimum learning rate
        
    Returns:
        Learning rate for current step
    """
    progress = min(step / total_steps, 1.0)
    return min_lr + (base_lr - min_lr) * 0.5 * (1 + math.cos(math.pi * progress))


def save_training_config(config: Dict[str, Any], filepath: Union[str, Path]) -> None:
    """
    Save training configuration to file.
    
    Args:
        config: Configuration dictionary
        filepath: Path to save file
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Training config saved to {filepath}")


def load_training_config(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load training configuration from file.
    
    Args:
        filepath: Path to config file
        
    Returns:
        Configuration dictionary
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise TrainingError(f"Config file not found: {filepath}")
    
    with open(filepath, 'r') as f:
        config = json.load(f)
    
    logger.info(f"Training config loaded from {filepath}")
    return config