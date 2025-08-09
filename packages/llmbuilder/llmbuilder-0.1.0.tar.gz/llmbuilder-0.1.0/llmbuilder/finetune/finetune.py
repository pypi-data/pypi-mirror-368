"""
Fine-tuning module for LLMBuilder.

This module provides the FineTuner class for fine-tuning pre-trained models
with domain-specific data, supporting various fine-tuning strategies and
optimizations for small datasets.
"""

import os
import time
import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import math

from ..utils import TrainingError, get_logger
from ..config import TrainingConfig, ModelConfig
from ..model import load_model, save_model, validate_model
from ..training import Trainer, TrainingMetrics, TrainingState
from ..data import create_dataloader

logger = get_logger("finetune.finetune")


@dataclass
class FineTuningConfig:
    """Configuration for fine-tuning."""
    # Base training config
    batch_size: int = 8
    learning_rate: float = 5e-5  # Lower LR for fine-tuning
    num_epochs: int = 3
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    warmup_steps: int = 100
    
    # Fine-tuning specific
    freeze_layers: int = 0  # Number of layers to freeze from bottom
    freeze_embeddings: bool = False  # Whether to freeze embeddings
    use_lora: bool = False  # Whether to use LoRA (Low-Rank Adaptation)
    lora_rank: int = 8  # LoRA rank
    lora_alpha: float = 32.0  # LoRA alpha
    
    # Regularization for small datasets
    dropout_increase: float = 0.0  # Additional dropout
    label_smoothing: float = 0.0  # Label smoothing
    gradient_accumulation_steps: int = 1  # Gradient accumulation
    
    # Scheduling
    scheduler_type: str = "linear"  # linear, cosine, constant
    min_lr: float = 1e-6
    
    # Checkpointing
    save_every: int = 500
    eval_every: int = 100
    log_every: int = 50
    
    # Versioning
    model_version: str = "v1.0"
    fine_tune_tag: str = "finetuned"
    
    def __post_init__(self):
        """Validate fine-tuning configuration."""
        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        if self.num_epochs <= 0:
            raise ValueError("num_epochs must be positive")
        if self.freeze_layers < 0:
            raise ValueError("freeze_layers must be non-negative")
        if self.lora_rank <= 0:
            raise ValueError("lora_rank must be positive")
        if not 0 <= self.dropout_increase <= 1:
            raise ValueError("dropout_increase must be between 0 and 1")
        if not 0 <= self.label_smoothing <= 1:
            raise ValueError("label_smoothing must be between 0 and 1")


class LoRALayer(nn.Module):
    """
    Low-Rank Adaptation (LoRA) layer.
    
    Implements LoRA for efficient fine-tuning by adding low-rank
    decomposition matrices to existing linear layers.
    """
    
    def __init__(self, 
                 original_layer: nn.Linear,
                 rank: int = 8,
                 alpha: float = 32.0,
                 dropout: float = 0.0):
        """
        Initialize LoRA layer.
        
        Args:
            original_layer: Original linear layer to adapt
            rank: LoRA rank (lower = more efficient)
            alpha: LoRA scaling parameter
            dropout: Dropout probability
        """
        super().__init__()
        
        self.original_layer = original_layer
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank
        
        # Freeze original layer
        for param in self.original_layer.parameters():
            param.requires_grad = False
        
        # LoRA matrices
        self.lora_A = nn.Linear(original_layer.in_features, rank, bias=False)
        self.lora_B = nn.Linear(rank, original_layer.out_features, bias=False)
        
        # Initialize LoRA weights
        nn.init.kaiming_uniform_(self.lora_A.weight, a=math.sqrt(5))
        nn.init.zeros_(self.lora_B.weight)
        
        # Dropout
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with LoRA adaptation."""
        # Original layer output
        original_output = self.original_layer(x)
        
        # LoRA adaptation
        lora_output = self.lora_B(self.dropout(self.lora_A(x)))
        
        return original_output + lora_output * self.scaling


class FineTuner:
    """
    Fine-tuner class extending the training pipeline for domain adaptation.
    
    Provides specialized fine-tuning capabilities including layer freezing,
    LoRA adaptation, and optimizations for small datasets.
    """
    
    def __init__(self, 
                 model: Optional[torch.nn.Module] = None,
                 config: Optional[FineTuningConfig] = None):
        """
        Initialize fine-tuner.
        
        Args:
            model: Pre-trained model to fine-tune
            config: Fine-tuning configuration
        """
        self.config = config or FineTuningConfig()
        self.model = model
        self.original_model = None  # Keep reference to original model
        
        # Training components (will be setup later)
        self.trainer = None
        self.optimizer = None
        self.scheduler = None
        
        # Fine-tuning state
        self.lora_layers = {}
        self.frozen_params = []
        
        # Device management
        self.device = self._setup_device()
        
        logger.info("FineTuner initialized")
        logger.info(f"Config: lr={self.config.learning_rate}, epochs={self.config.num_epochs}")
    
    def _setup_device(self) -> torch.device:
        """Setup training device."""
        if torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name()}")
        else:
            device = torch.device("cpu")
            logger.info("Using CPU device")
        
        return device
    
    def load_pretrained_model(self, model_path: Union[str, Path]) -> None:
        """
        Load pre-trained model for fine-tuning.
        
        Args:
            model_path: Path to pre-trained model checkpoint
        """
        logger.info(f"Loading pre-trained model from {model_path}")
        
        try:
            self.model = load_model(model_path, device=self.device)
            self.original_model = self.model  # Keep reference
            
            # Validate model
            validation_results = validate_model(self.model)
            if not validation_results['valid']:
                raise TrainingError(f"Model validation failed: {validation_results['errors']}")
            
            num_params = sum(p.numel() for p in self.model.parameters())
            logger.info(f"Pre-trained model loaded: {num_params:,} parameters")
            
        except Exception as e:
            raise TrainingError(f"Failed to load pre-trained model: {str(e)}") from e
    
    def setup_model_for_finetuning(self) -> None:
        """Setup model for fine-tuning with freezing and adaptations."""
        if self.model is None:
            raise TrainingError("Model must be loaded before setup")
        
        logger.info("Setting up model for fine-tuning")
        
        # Apply layer freezing
        if self.config.freeze_layers > 0:
            self._freeze_layers()
        
        # Apply embedding freezing
        if self.config.freeze_embeddings:
            self._freeze_embeddings()
        
        # Apply LoRA if requested
        if self.config.use_lora:
            self._apply_lora()
        
        # Increase dropout if requested
        if self.config.dropout_increase > 0:
            self._increase_dropout()
        
        # Move to device
        self.model = self.model.to(self.device)
        
        # Count trainable parameters
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        
        logger.info(f"Fine-tuning setup complete:")
        logger.info(f"  Trainable parameters: {trainable_params:,} ({100*trainable_params/total_params:.1f}%)")
        logger.info(f"  Frozen parameters: {total_params - trainable_params:,}")
    
    def _freeze_layers(self) -> None:
        """Freeze bottom layers of the model."""
        logger.info(f"Freezing bottom {self.config.freeze_layers} layers")
        
        # For GPT models, freeze transformer blocks
        if hasattr(self.model, 'blocks'):
            blocks_to_freeze = min(self.config.freeze_layers, len(self.model.blocks))
            
            for i in range(blocks_to_freeze):
                for param in self.model.blocks[i].parameters():
                    param.requires_grad = False
                    self.frozen_params.append(param)
            
            logger.info(f"Froze {blocks_to_freeze} transformer blocks")
    
    def _freeze_embeddings(self) -> None:
        """Freeze embedding layers."""
        logger.info("Freezing embedding layers")
        
        # Freeze token and position embeddings
        if hasattr(self.model, 'token_embedding'):
            for param in self.model.token_embedding.parameters():
                param.requires_grad = False
                self.frozen_params.append(param)
        
        if hasattr(self.model, 'position_embedding'):
            for param in self.model.position_embedding.parameters():
                param.requires_grad = False
                self.frozen_params.append(param)
        
        logger.info("Embedding layers frozen")
    
    def _apply_lora(self) -> None:
        """Apply LoRA adaptation to linear layers."""
        logger.info(f"Applying LoRA adaptation (rank={self.config.lora_rank})")
        
        # Apply LoRA to attention and MLP layers
        lora_count = 0
        
        if hasattr(self.model, 'blocks'):
            for block_idx, block in enumerate(self.model.blocks):
                # Apply to attention layers
                if hasattr(block, 'attn'):
                    attn = block.attn
                    
                    # QKV projection
                    if hasattr(attn, 'qkv_proj'):
                        lora_layer = LoRALayer(
                            attn.qkv_proj,
                            rank=self.config.lora_rank,
                            alpha=self.config.lora_alpha
                        )
                        setattr(attn, 'qkv_proj', lora_layer)
                        self.lora_layers[f'block_{block_idx}_attn_qkv'] = lora_layer
                        lora_count += 1
                    
                    # Output projection
                    if hasattr(attn, 'out_proj'):
                        lora_layer = LoRALayer(
                            attn.out_proj,
                            rank=self.config.lora_rank,
                            alpha=self.config.lora_alpha
                        )
                        setattr(attn, 'out_proj', lora_layer)
                        self.lora_layers[f'block_{block_idx}_attn_out'] = lora_layer
                        lora_count += 1
                
                # Apply to MLP layers
                if hasattr(block, 'mlp'):
                    mlp = block.mlp
                    
                    # First linear layer
                    if hasattr(mlp, 'fc1'):
                        lora_layer = LoRALayer(
                            mlp.fc1,
                            rank=self.config.lora_rank,
                            alpha=self.config.lora_alpha
                        )
                        setattr(mlp, 'fc1', lora_layer)
                        self.lora_layers[f'block_{block_idx}_mlp_fc1'] = lora_layer
                        lora_count += 1
                    
                    # Second linear layer
                    if hasattr(mlp, 'fc2'):
                        lora_layer = LoRALayer(
                            mlp.fc2,
                            rank=self.config.lora_rank,
                            alpha=self.config.lora_alpha
                        )
                        setattr(mlp, 'fc2', lora_layer)
                        self.lora_layers[f'block_{block_idx}_mlp_fc2'] = lora_layer
                        lora_count += 1
        
        logger.info(f"Applied LoRA to {lora_count} layers")
    
    def _increase_dropout(self) -> None:
        """Increase dropout rates for regularization."""
        logger.info(f"Increasing dropout by {self.config.dropout_increase}")
        
        def increase_dropout_recursive(module):
            for child in module.children():
                if isinstance(child, nn.Dropout):
                    child.p = min(child.p + self.config.dropout_increase, 0.9)
                else:
                    increase_dropout_recursive(child)
        
        increase_dropout_recursive(self.model)
    
    def setup_optimizer(self) -> None:
        """Setup optimizer for fine-tuning."""
        if self.model is None:
            raise TrainingError("Model must be setup before optimizer")
        
        # Get trainable parameters
        trainable_params = [p for p in self.model.parameters() if p.requires_grad]
        
        if not trainable_params:
            raise TrainingError("No trainable parameters found")
        
        # Create optimizer with fine-tuning specific settings
        self.optimizer = torch.optim.AdamW(
            trainable_params,
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            eps=1e-8
        )
        
        logger.info(f"Optimizer setup: AdamW with lr={self.config.learning_rate}")
        logger.info(f"Trainable parameters: {len(trainable_params)}")
    
    def setup_scheduler(self, total_steps: int) -> None:
        """Setup learning rate scheduler."""
        if self.optimizer is None:
            raise TrainingError("Optimizer must be setup before scheduler")
        
        if self.config.scheduler_type == "linear":
            def lr_lambda(step):
                if step < self.config.warmup_steps:
                    return step / max(1, self.config.warmup_steps)
                return max(0.0, (total_steps - step) / max(1, total_steps - self.config.warmup_steps))
            
            self.scheduler = torch.optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda)
            
        elif self.config.scheduler_type == "cosine":
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=total_steps,
                eta_min=self.config.min_lr
            )
        elif self.config.scheduler_type == "constant":
            self.scheduler = None
        else:
            logger.warning(f"Unknown scheduler type: {self.config.scheduler_type}")
            self.scheduler = None
        
        if self.scheduler:
            logger.info(f"Learning rate scheduler setup: {self.config.scheduler_type}")
    
    def finetune(self, 
                 train_dataset: torch.utils.data.Dataset,
                 val_dataset: Optional[torch.utils.data.Dataset] = None,
                 checkpoint_dir: Union[str, Path] = "finetune_checkpoints") -> Dict[str, Any]:
        """
        Execute fine-tuning pipeline.
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset (optional)
            checkpoint_dir: Directory for saving checkpoints
            
        Returns:
            Dict[str, Any]: Fine-tuning results
        """
        logger.info("Starting fine-tuning pipeline")
        
        if self.model is None:
            raise TrainingError("Model must be loaded before fine-tuning")
        
        try:
            # Setup model for fine-tuning
            self.setup_model_for_finetuning()
            
            # Setup optimizer
            self.setup_optimizer()
            
            # Create data loaders with gradient accumulation consideration
            effective_batch_size = self.config.batch_size * self.config.gradient_accumulation_steps
            
            train_loader = create_dataloader(
                train_dataset,
                batch_size=self.config.batch_size,
                shuffle=True,
                num_workers=4,
                pin_memory=self.device.type == 'cuda'
            )
            
            val_loader = None
            if val_dataset is not None:
                val_loader = create_dataloader(
                    val_dataset,
                    batch_size=self.config.batch_size,
                    shuffle=False,
                    num_workers=4,
                    pin_memory=self.device.type == 'cuda'
                )
            
            # Setup scheduler
            total_steps = len(train_loader) * self.config.num_epochs // self.config.gradient_accumulation_steps
            self.setup_scheduler(total_steps)
            
            # Fine-tuning loop
            best_val_loss = float('inf')
            start_time = time.time()
            global_step = 0
            
            logger.info(f"Fine-tuning for {self.config.num_epochs} epochs")
            logger.info(f"Effective batch size: {effective_batch_size}")
            logger.info(f"Total steps: {total_steps}")
            
            for epoch in range(self.config.num_epochs):
                # Training epoch
                train_loss = self._finetune_epoch(
                    train_loader, epoch, global_step
                )
                
                # Validation
                val_loss = float('inf')
                if val_loader is not None:
                    val_loss = self._validate_epoch(val_loader)
                
                # Update global step
                global_step += len(train_loader) // self.config.gradient_accumulation_steps
                
                # Check if best model
                is_best = val_loss < best_val_loss
                if is_best:
                    best_val_loss = val_loss
                    logger.info(f"New best validation loss: {val_loss:.4f}")
                
                # Save checkpoint
                if (epoch + 1) % (self.config.save_every // len(train_loader) + 1) == 0 or is_best:
                    self._save_finetune_checkpoint(
                        checkpoint_dir, epoch, train_loss, val_loss, is_best
                    )
                
                logger.info(
                    f"Epoch {epoch+1}/{self.config.num_epochs} - "
                    f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}"
                )
            
            # Fine-tuning completed
            total_time = time.time() - start_time
            logger.info(f"Fine-tuning completed in {total_time:.1f}s")
            logger.info(f"Best validation loss: {best_val_loss:.4f}")
            
            # Save final model with versioning
            final_model_path = self._save_final_model(checkpoint_dir)
            
            return {
                'best_val_loss': best_val_loss,
                'total_epochs': self.config.num_epochs,
                'total_steps': global_step,
                'total_time': total_time,
                'final_model_path': final_model_path,
                'config': asdict(self.config)
            }
            
        except Exception as e:
            logger.error(f"Fine-tuning failed: {e}")
            raise TrainingError(f"Fine-tuning failed: {str(e)}") from e
    
    def _finetune_epoch(self, train_loader, epoch: int, global_step: int) -> float:
        """Fine-tune for one epoch."""
        self.model.train()
        total_loss = 0.0
        total_samples = 0
        accumulated_loss = 0.0
        
        for step, batch in enumerate(train_loader):
            try:
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device, non_blocking=True)
                labels = batch['labels'].to(self.device, non_blocking=True)
                
                # Forward pass
                logits, loss = self.model(input_ids, labels)
                
                # Apply label smoothing if configured
                if self.config.label_smoothing > 0:
                    loss = self._apply_label_smoothing(logits, labels, loss)
                
                # Scale loss for gradient accumulation
                loss = loss / self.config.gradient_accumulation_steps
                
                # Backward pass
                loss.backward()
                
                accumulated_loss += loss.item()
                
                # Gradient accumulation
                if (step + 1) % self.config.gradient_accumulation_steps == 0:
                    # Gradient clipping
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(),
                        max_norm=self.config.max_grad_norm
                    )
                    
                    # Optimizer step
                    self.optimizer.step()
                    self.optimizer.zero_grad()
                    
                    # Scheduler step
                    if self.scheduler:
                        self.scheduler.step()
                    
                    # Update metrics
                    batch_size = input_ids.size(0)
                    total_loss += accumulated_loss * batch_size
                    total_samples += batch_size
                    accumulated_loss = 0.0
                    
                    # Log progress
                    if global_step % self.config.log_every == 0:
                        avg_loss = total_loss / total_samples if total_samples > 0 else 0
                        current_lr = self.optimizer.param_groups[0]['lr']
                        
                        logger.info(
                            f"Epoch [{epoch+1}] Step [{step+1}/{len(train_loader)}] "
                            f"Loss: {avg_loss:.4f} LR: {current_lr:.2e}"
                        )
                    
                    global_step += 1
                
            except Exception as e:
                logger.error(f"Error in fine-tuning step {step}: {e}")
                continue
        
        return total_loss / total_samples if total_samples > 0 else float('inf')
    
    def _validate_epoch(self, val_loader) -> float:
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0.0
        total_samples = 0
        
        with torch.no_grad():
            for batch in val_loader:
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
        
        return total_loss / total_samples if total_samples > 0 else float('inf')
    
    def _apply_label_smoothing(self, logits, labels, original_loss):
        """Apply label smoothing to loss."""
        # Simple label smoothing implementation
        vocab_size = logits.size(-1)
        confidence = 1.0 - self.config.label_smoothing
        smooth_loss = -logits.log_softmax(dim=-1).mean(dim=-1).mean()
        
        return confidence * original_loss + self.config.label_smoothing * smooth_loss
    
    def _save_finetune_checkpoint(self, checkpoint_dir, epoch, train_loss, val_loss, is_best):
        """Save fine-tuning checkpoint."""
        checkpoint_dir = Path(checkpoint_dir)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_data = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict() if self.optimizer else None,
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'epoch': epoch,
            'train_loss': train_loss,
            'val_loss': val_loss,
            'config': asdict(self.config),
            'lora_layers': list(self.lora_layers.keys()) if self.lora_layers else [],
        }
        
        # Save checkpoint
        if is_best:
            checkpoint_path = checkpoint_dir / "best_finetune_checkpoint.pt"
        else:
            checkpoint_path = checkpoint_dir / f"finetune_checkpoint_epoch_{epoch}.pt"
        
        torch.save(checkpoint_data, checkpoint_path)
        
        # Also save as latest
        latest_path = checkpoint_dir / "latest_finetune_checkpoint.pt"
        torch.save(checkpoint_data, latest_path)
        
        logger.info(f"Fine-tune checkpoint saved: {checkpoint_path}")
    
    def _save_final_model(self, checkpoint_dir) -> str:
        """Save final fine-tuned model with versioning."""
        checkpoint_dir = Path(checkpoint_dir)
        
        # Create versioned filename
        model_name = f"{self.config.fine_tune_tag}_{self.config.model_version}"
        final_path = checkpoint_dir / f"{model_name}.pt"
        
        # Save model using the model builder's save function
        save_model(
            self.model,
            final_path,
            additional_info={
                'fine_tuning_config': asdict(self.config),
                'model_version': self.config.model_version,
                'fine_tune_tag': self.config.fine_tune_tag,
                'lora_applied': self.config.use_lora,
                'frozen_layers': self.config.freeze_layers,
            }
        )
        
        logger.info(f"Final fine-tuned model saved: {final_path}")
        return str(final_path)


# Convenience functions for the API
def finetune_model(model: torch.nn.Module,
                   dataset: torch.utils.data.Dataset,
                   config: FineTuningConfig,
                   val_dataset: Optional[torch.utils.data.Dataset] = None,
                   checkpoint_dir: Union[str, Path] = "finetune_checkpoints") -> Dict[str, Any]:
    """
    Fine-tune a model with the given dataset and configuration.
    
    Args:
        model: Pre-trained model to fine-tune
        dataset: Fine-tuning dataset
        config: Fine-tuning configuration
        val_dataset: Validation dataset (optional)
        checkpoint_dir: Directory for saving checkpoints
        
    Returns:
        Dict[str, Any]: Fine-tuning results
    """
    finetuner = FineTuner(model=model, config=config)
    return finetuner.finetune(dataset, val_dataset, checkpoint_dir)


def create_lora_config(rank: int = 8, 
                      alpha: float = 32.0,
                      learning_rate: float = 5e-5,
                      **kwargs) -> FineTuningConfig:
    """
    Create a LoRA fine-tuning configuration.
    
    Args:
        rank: LoRA rank
        alpha: LoRA alpha parameter
        learning_rate: Learning rate
        **kwargs: Additional config parameters
        
    Returns:
        FineTuningConfig: Configuration with LoRA enabled
    """
    return FineTuningConfig(
        use_lora=True,
        lora_rank=rank,
        lora_alpha=alpha,
        learning_rate=learning_rate,
        **kwargs
    )


def create_small_dataset_config(learning_rate: float = 1e-5,
                               dropout_increase: float = 0.1,
                               label_smoothing: float = 0.1,
                               **kwargs) -> FineTuningConfig:
    """
    Create a configuration optimized for small datasets.
    
    Args:
        learning_rate: Lower learning rate for small datasets
        dropout_increase: Additional dropout for regularization
        label_smoothing: Label smoothing factor
        **kwargs: Additional config parameters
        
    Returns:
        FineTuningConfig: Configuration optimized for small datasets
    """
    return FineTuningConfig(
        learning_rate=learning_rate,
        dropout_increase=dropout_increase,
        label_smoothing=label_smoothing,
        gradient_accumulation_steps=4,  # Larger effective batch size
        **kwargs
    )