"""
Training pipeline module for LLMBuilder.

This module provides the Trainer class for comprehensive model training
with error handling, checkpointing, metrics tracking, and recovery mechanisms.
"""

import os
import time
import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import math

from ..utils import TrainingError, get_logger, save_checkpoint, load_checkpoint
from ..config import TrainingConfig, ModelConfig
from ..model import build_model, load_model, save_model, validate_model
from ..data import TextDataset, create_dataloader, split_dataset

logger = get_logger("training.train")


@dataclass
class TrainingMetrics:
    """Training metrics container."""
    epoch: int
    step: int
    train_loss: float
    val_loss: Optional[float] = None
    learning_rate: float = 0.0
    grad_norm: float = 0.0
    epoch_time: float = 0.0
    samples_per_second: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TrainingState:
    """Training state container."""
    epoch: int = 0
    step: int = 0
    best_val_loss: float = float('inf')
    total_steps: int = 0
    start_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class Trainer:
    """
    Comprehensive trainer for LLM models.
    
    Provides full training pipeline with error handling, checkpointing,
    metrics tracking, and recovery mechanisms.
    """
    
    def __init__(self, 
                 model: Optional[torch.nn.Module] = None,
                 config: Optional[TrainingConfig] = None,
                 model_config: Optional[ModelConfig] = None):
        """
        Initialize trainer.
        
        Args:
            model: Model to train (optional, can be built from config)
            config: Training configuration
            model_config: Model configuration (for building model if not provided)
        """
        self.config = config or TrainingConfig()
        self.model_config = model_config
        self.model = model
        
        # Training state
        self.state = TrainingState()
        self.metrics_history = []
        
        # Components
        self.optimizer = None
        self.scheduler = None
        self.train_loader = None
        self.val_loader = None
        
        # Device management
        self.device = self._setup_device()
        
        logger.info("Trainer initialized")
        logger.info(f"Device: {self.device}")
    
    def _setup_device(self) -> torch.device:
        """Setup training device."""
        if torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name()}")
        else:
            device = torch.device("cpu")
            logger.info("Using CPU device")
        
        return device
    
    def setup_model(self, model: Optional[torch.nn.Module] = None) -> None:
        """
        Setup model for training.
        
        Args:
            model: Model to use (optional, will build from config if not provided)
        """
        if model is not None:
            self.model = model
        elif self.model is None:
            if self.model_config is None:
                raise TrainingError("No model provided and no model config available")
            
            logger.info("Building model from configuration")
            self.model = build_model(self.model_config)
        
        # Validate model
        validation_results = validate_model(self.model)
        if not validation_results['valid']:
            raise TrainingError(f"Model validation failed: {validation_results['errors']}")
        
        # Move to device
        self.model = self.model.to(self.device)
        
        # Log model info
        num_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        logger.info(f"Model setup complete: {num_params:,} trainable parameters")
    
    def setup_optimizer(self) -> None:
        """Setup optimizer and learning rate scheduler."""
        if self.model is None:
            raise TrainingError("Model must be setup before optimizer")
        
        # Create optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            betas=(self.config.beta1, self.config.beta2),
            eps=self.config.eps,
            weight_decay=self.config.weight_decay
        )
        
        # Setup learning rate scheduler if needed
        if hasattr(self.config, 'scheduler_type') and self.config.scheduler_type:
            self._setup_scheduler()
        
        logger.info(f"Optimizer setup: AdamW with lr={self.config.learning_rate}")
    
    def _setup_scheduler(self) -> None:
        """Setup learning rate scheduler."""
        if not hasattr(self.config, 'scheduler_type'):
            return
        
        scheduler_type = self.config.scheduler_type.lower()
        
        if scheduler_type == 'cosine':
            total_steps = self.state.total_steps
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=total_steps,
                eta_min=getattr(self.config, 'min_lr', 1e-6)
            )
        elif scheduler_type == 'linear':
            def lr_lambda(step):
                if step < self.config.warmup_steps:
                    return step / max(1, self.config.warmup_steps)
                return max(0.0, (self.state.total_steps - step) / max(1, self.state.total_steps - self.config.warmup_steps))
            
            self.scheduler = torch.optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda)
        
        if self.scheduler:
            logger.info(f"Learning rate scheduler setup: {scheduler_type}")
    
    def setup_data(self, 
                   train_dataset: torch.utils.data.Dataset,
                   val_dataset: Optional[torch.utils.data.Dataset] = None) -> None:
        """
        Setup data loaders.
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset (optional)
        """
        # Create training data loader
        self.train_loader = create_dataloader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=self.device.type == 'cuda'
        )
        
        # Create validation data loader if dataset provided
        if val_dataset is not None:
            self.val_loader = create_dataloader(
                val_dataset,
                batch_size=self.config.batch_size,
                shuffle=False,
                num_workers=4,
                pin_memory=self.device.type == 'cuda'
            )
        
        # Update total steps
        self.state.total_steps = len(self.train_loader) * self.config.num_epochs
        
        logger.info(f"Data setup complete: {len(train_dataset):,} train samples")
        if val_dataset:
            logger.info(f"Validation samples: {len(val_dataset):,}")
        logger.info(f"Steps per epoch: {len(self.train_loader)}, Total steps: {self.state.total_steps}")
    
    def train_epoch(self, epoch: int) -> TrainingMetrics:
        """
        Train for one epoch.
        
        Args:
            epoch: Current epoch number
            
        Returns:
            TrainingMetrics: Metrics for this epoch
        """
        if self.model is None or self.optimizer is None or self.train_loader is None:
            raise TrainingError("Model, optimizer, and data loader must be setup before training")
        
        self.model.train()
        total_loss = 0.0
        total_samples = 0
        epoch_start_time = time.time()
        
        for step, batch in enumerate(self.train_loader):
            step_start_time = time.time()
            
            try:
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device, non_blocking=True)
                labels = batch['labels'].to(self.device, non_blocking=True)
                
                # Forward pass
                logits, loss = self.model(input_ids, labels)
                
                # Check for NaN/Inf loss
                if torch.isnan(loss) or torch.isinf(loss):
                    logger.warning(f"NaN/Inf loss detected at step {step}, skipping")
                    continue
                
                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                
                # Gradient clipping
                grad_norm = torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    max_norm=self.config.max_grad_norm
                )
                
                # Optimizer step
                self.optimizer.step()
                
                # Scheduler step
                if self.scheduler:
                    self.scheduler.step()
                
                # Update metrics
                batch_size = input_ids.size(0)
                total_loss += loss.item() * batch_size
                total_samples += batch_size
                self.state.step += 1
                
                # Log progress
                if (step + 1) % self.config.log_every == 0:
                    avg_loss = total_loss / total_samples
                    current_lr = self.optimizer.param_groups[0]['lr']
                    step_time = time.time() - step_start_time
                    
                    logger.info(
                        f"Epoch [{epoch+1}/{self.config.num_epochs}] "
                        f"Step [{step+1}/{len(self.train_loader)}] "
                        f"Loss: {avg_loss:.4f} "
                        f"LR: {current_lr:.2e} "
                        f"Grad norm: {grad_norm:.2f} "
                        f"Step time: {step_time:.2f}s"
                    )
                
            except RuntimeError as e:
                if "out of memory" in str(e):
                    logger.error(f"Out of memory at step {step}. Try reducing batch size.")
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    raise TrainingError(f"Out of memory: {str(e)}") from e
                else:
                    logger.error(f"Runtime error in training step {step}: {e}")
                    continue
            except Exception as e:
                logger.error(f"Unexpected error in training step {step}: {e}")
                continue
        
        # Calculate epoch metrics
        epoch_time = time.time() - epoch_start_time
        avg_loss = total_loss / total_samples if total_samples > 0 else float('inf')
        samples_per_second = total_samples / epoch_time if epoch_time > 0 else 0
        current_lr = self.optimizer.param_groups[0]['lr'] if self.optimizer else 0
        
        metrics = TrainingMetrics(
            epoch=epoch,
            step=self.state.step,
            train_loss=avg_loss,
            learning_rate=current_lr,
            epoch_time=epoch_time,
            samples_per_second=samples_per_second
        )
        
        logger.info(
            f"Epoch {epoch+1} completed - "
            f"Loss: {avg_loss:.4f}, "
            f"Time: {epoch_time:.1f}s, "
            f"Speed: {samples_per_second:.1f} samples/s"
        )
        
        return metrics
    
    def validate(self) -> float:
        """
        Validate the model.
        
        Returns:
            float: Validation loss
        """
        if self.model is None or self.val_loader is None:
            logger.warning("Model or validation loader not available, skipping validation")
            return float('inf')
        
        self.model.eval()
        total_loss = 0.0
        total_samples = 0
        
        with torch.no_grad():
            for batch in self.val_loader:
                try:
                    input_ids = batch['input_ids'].to(self.device, non_blocking=True)
                    labels = batch['labels'].to(self.device, non_blocking=True)
                    
                    logits, loss = self.model(input_ids, labels)
                    
                    if not (torch.isnan(loss) or torch.isinf(loss)):
                        batch_size = input_ids.size(0)
                        total_loss += loss.item() * batch_size
                        total_samples += batch_size
                
                except Exception as e:
                    logger.error(f"Error in validation step: {e}")
                    continue
        
        avg_loss = total_loss / total_samples if total_samples > 0 else float('inf')
        logger.info(f"Validation loss: {avg_loss:.4f}")
        
        return avg_loss
    
    def save_checkpoint(self, 
                       checkpoint_dir: Union[str, Path],
                       metrics: Optional[TrainingMetrics] = None,
                       is_best: bool = False) -> str:
        """
        Save training checkpoint.
        
        Args:
            checkpoint_dir: Directory to save checkpoint
            metrics: Current training metrics
            is_best: Whether this is the best checkpoint
            
        Returns:
            str: Path to saved checkpoint
        """
        checkpoint_dir = Path(checkpoint_dir)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare checkpoint data
        checkpoint_data = {
            'model_state_dict': self.model.state_dict() if self.model else None,
            'optimizer_state_dict': self.optimizer.state_dict() if self.optimizer else None,
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'training_state': self.state.to_dict(),
            'config': asdict(self.config),
            'metrics': metrics.to_dict() if metrics else None,
            'metrics_history': [m.to_dict() for m in self.metrics_history],
        }
        
        # Save checkpoint
        if is_best:
            checkpoint_path = checkpoint_dir / "best_checkpoint.pt"
        else:
            checkpoint_path = checkpoint_dir / f"checkpoint_epoch_{self.state.epoch}.pt"
        
        torch.save(checkpoint_data, checkpoint_path)
        
        # Also save as latest
        latest_path = checkpoint_dir / "latest_checkpoint.pt"
        torch.save(checkpoint_data, latest_path)
        
        logger.info(f"Checkpoint saved: {checkpoint_path}")
        return str(checkpoint_path)
    
    def load_checkpoint(self, checkpoint_path: Union[str, Path]) -> bool:
        """
        Load training checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint file
            
        Returns:
            bool: True if loaded successfully
        """
        checkpoint_path = Path(checkpoint_path)
        
        if not checkpoint_path.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_path}")
            return False
        
        try:
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            # Load model state
            if self.model and 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
            
            # Load optimizer state
            if self.optimizer and 'optimizer_state_dict' in checkpoint:
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            
            # Load scheduler state
            if self.scheduler and 'scheduler_state_dict' in checkpoint:
                self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
            
            # Load training state
            if 'training_state' in checkpoint:
                state_dict = checkpoint['training_state']
                self.state = TrainingState(**state_dict)
            
            # Load metrics history
            if 'metrics_history' in checkpoint:
                self.metrics_history = [
                    TrainingMetrics(**m) for m in checkpoint['metrics_history']
                ]
            
            logger.info(f"Checkpoint loaded: epoch {self.state.epoch}, step {self.state.step}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            return False
    
    def train(self, 
              train_dataset: torch.utils.data.Dataset,
              val_dataset: Optional[torch.utils.data.Dataset] = None,
              checkpoint_dir: Union[str, Path] = "checkpoints") -> Dict[str, Any]:
        """
        Execute full training pipeline.
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset (optional)
            checkpoint_dir: Directory for saving checkpoints
            
        Returns:
            Dict[str, Any]: Training results
        """
        logger.info("Starting training pipeline")
        
        try:
            # Setup components
            if self.model is None:
                self.setup_model()
            
            self.setup_optimizer()
            self.setup_data(train_dataset, val_dataset)
            
            # Initialize training state
            self.state.start_time = time.time()
            
            # Training loop
            for epoch in range(self.state.epoch, self.config.num_epochs):
                self.state.epoch = epoch
                
                try:
                    # Train epoch
                    train_metrics = self.train_epoch(epoch)
                    
                    # Validate
                    val_loss = self.validate()
                    train_metrics.val_loss = val_loss
                    
                    # Update metrics history
                    self.metrics_history.append(train_metrics)
                    
                    # Check if best model
                    is_best = val_loss < self.state.best_val_loss
                    if is_best:
                        self.state.best_val_loss = val_loss
                        logger.info(f"New best validation loss: {val_loss:.4f}")
                    
                    # Save checkpoint
                    if (epoch + 1) % self.config.save_every == 0 or is_best:
                        self.save_checkpoint(checkpoint_dir, train_metrics, is_best)
                    
                except KeyboardInterrupt:
                    logger.info("Training interrupted by user")
                    self.save_checkpoint(checkpoint_dir, train_metrics)
                    break
                except Exception as e:
                    logger.error(f"Error in epoch {epoch}: {e}")
                    # Save emergency checkpoint
                    self.save_checkpoint(checkpoint_dir, train_metrics)
                    continue
            
            # Training completed
            total_time = time.time() - self.state.start_time
            logger.info(f"Training completed in {total_time:.1f}s")
            logger.info(f"Best validation loss: {self.state.best_val_loss:.4f}")
            
            return {
                'best_val_loss': self.state.best_val_loss,
                'total_epochs': self.state.epoch + 1,
                'total_steps': self.state.step,
                'total_time': total_time,
                'metrics_history': [m.to_dict() for m in self.metrics_history]
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise TrainingError(f"Training failed: {str(e)}") from e
    
    def evaluate_model(self, 
                      dataset: torch.utils.data.Dataset,
                      metrics: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Evaluate model on dataset.
        
        Args:
            dataset: Dataset to evaluate on
            metrics: List of metrics to compute (default: ['loss', 'perplexity'])
            
        Returns:
            Dict[str, float]: Evaluation metrics
        """
        if self.model is None:
            raise TrainingError("Model must be setup before evaluation")
        
        if metrics is None:
            metrics = ['loss', 'perplexity']
        
        # Create data loader
        eval_loader = create_dataloader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=self.device.type == 'cuda'
        )
        
        self.model.eval()
        total_loss = 0.0
        total_samples = 0
        
        logger.info(f"Evaluating model on {len(dataset)} samples")
        
        with torch.no_grad():
            for batch in eval_loader:
                try:
                    input_ids = batch['input_ids'].to(self.device, non_blocking=True)
                    labels = batch['labels'].to(self.device, non_blocking=True)
                    
                    logits, loss = self.model(input_ids, labels)
                    
                    if not (torch.isnan(loss) or torch.isinf(loss)):
                        batch_size = input_ids.size(0)
                        total_loss += loss.item() * batch_size
                        total_samples += batch_size
                
                except Exception as e:
                    logger.error(f"Error in evaluation step: {e}")
                    continue
        
        # Calculate metrics
        results = {}
        
        if total_samples > 0:
            avg_loss = total_loss / total_samples
            
            if 'loss' in metrics:
                results['loss'] = avg_loss
            
            if 'perplexity' in metrics:
                results['perplexity'] = math.exp(avg_loss)
        else:
            logger.warning("No valid evaluation samples")
            results = {metric: float('inf') for metric in metrics}
        
        logger.info(f"Evaluation results: {results}")
        return results


# Convenience functions for the API
def train_model(model: torch.nn.Module,
                dataset: torch.utils.data.Dataset,
                config: TrainingConfig,
                val_dataset: Optional[torch.utils.data.Dataset] = None,
                checkpoint_dir: Union[str, Path] = "checkpoints") -> Dict[str, Any]:
    """
    Train a model with the given dataset and configuration.
    
    Args:
        model: Model to train
        dataset: Training dataset
        config: Training configuration
        val_dataset: Validation dataset (optional)
        checkpoint_dir: Directory for saving checkpoints
        
    Returns:
        Dict[str, Any]: Training results
    """
    trainer = Trainer(model=model, config=config)
    return trainer.train(dataset, val_dataset, checkpoint_dir)


def resume_training(checkpoint_path: Union[str, Path],
                   train_dataset: torch.utils.data.Dataset,
                   val_dataset: Optional[torch.utils.data.Dataset] = None,
                   checkpoint_dir: Union[str, Path] = "checkpoints") -> Dict[str, Any]:
    """
    Resume training from checkpoint.
    
    Args:
        checkpoint_path: Path to checkpoint file
        train_dataset: Training dataset
        val_dataset: Validation dataset (optional)
        checkpoint_dir: Directory for saving new checkpoints
        
    Returns:
        Dict[str, Any]: Training results
    """
    trainer = Trainer()
    
    if not trainer.load_checkpoint(checkpoint_path):
        raise TrainingError(f"Failed to load checkpoint: {checkpoint_path}")
    
    return trainer.train(train_dataset, val_dataset, checkpoint_dir)


def evaluate_model(model: torch.nn.Module,
                  dataset: torch.utils.data.Dataset,
                  config: Optional[TrainingConfig] = None,
                  metrics: Optional[List[str]] = None) -> Dict[str, float]:
    """
    Evaluate a model on dataset.
    
    Args:
        model: Model to evaluate
        dataset: Dataset to evaluate on
        config: Training configuration (optional)
        metrics: List of metrics to compute
        
    Returns:
        Dict[str, float]: Evaluation metrics
    """
    trainer = Trainer(model=model, config=config or TrainingConfig())
    return trainer.evaluate_model(dataset, metrics)