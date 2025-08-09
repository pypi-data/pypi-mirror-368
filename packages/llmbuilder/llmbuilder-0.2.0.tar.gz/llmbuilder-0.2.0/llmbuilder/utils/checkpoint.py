"""
Checkpoint management utilities for LLMBuilder.

This module provides comprehensive checkpoint management including
saving, loading, validation, and metadata handling for model training.
"""

import os
import json
import torch
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
import hashlib


# Define exceptions locally to avoid circular imports
class CheckpointError(Exception):
    """Checkpoint related errors."""
    def __init__(self, message: str, checkpoint_path: str = None, operation: str = None, cause: Exception = None):
        super().__init__(message)
        self.checkpoint_path = checkpoint_path
        self.operation = operation
        self.cause = cause


class ModelError(Exception):
    """Model related errors."""
    pass


class CheckpointMetadata:
    """Checkpoint metadata container."""
    def __init__(
        self,
        epoch: int = 0,
        step: int = 0,
        loss: float = 0.0,
        metrics: Optional[Dict[str, float]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.epoch = epoch
        self.step = step
        self.loss = loss
        self.metrics = metrics or {}
        self.config = config or {}
        self.timestamp = datetime.now().isoformat()


# Import logger safely
try:
    from .logger import get_logger
    logger = get_logger("checkpoint")
except ImportError:
    import logging
    logger = logging.getLogger("checkpoint")


class CheckpointManager:
    """
    Manages model checkpoints with metadata, validation, and versioning.
    
    Provides functionality for saving and loading model checkpoints with
    comprehensive metadata tracking and validation.
    """
    
    def __init__(self, checkpoint_dir: Union[str, Path] = "checkpoints"):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Registry file for tracking checkpoints
        self.registry_file = self.checkpoint_dir / "checkpoint_registry.json"
        self.registry = self._load_checkpoint_registry()
    
    def save_checkpoint(
        self,
        model: torch.nn.Module,
        optimizer: Optional[torch.optim.Optimizer] = None,
        scheduler: Optional[Any] = None,
        metadata: Optional[CheckpointMetadata] = None,
        checkpoint_name: Optional[str] = None,
        is_best: bool = False,
        keep_last_n: int = 5
    ) -> str:
        """
        Save a model checkpoint with metadata.
        
        Args:
            model: Model to save
            optimizer: Optimizer state (optional)
            scheduler: Learning rate scheduler (optional)
            metadata: Checkpoint metadata
            checkpoint_name: Custom checkpoint name
            is_best: Whether this is the best checkpoint
            keep_last_n: Number of recent checkpoints to keep
            
        Returns:
            str: Path to saved checkpoint
            
        Raises:
            CheckpointError: If saving fails
        """
        try:
            # Create default metadata if not provided
            if metadata is None:
                metadata = CheckpointMetadata()
            
            # Generate checkpoint name if not provided
            if checkpoint_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                checkpoint_name = f"checkpoint_epoch_{metadata.epoch:04d}_step_{metadata.step:06d}_{timestamp}"
            
            checkpoint_path = self.checkpoint_dir / f"{checkpoint_name}.pt"
            
            # Prepare checkpoint data
            checkpoint_data = {
                'model_state_dict': model.state_dict(),
                'metadata': {
                    'epoch': metadata.epoch,
                    'step': metadata.step,
                    'loss': metadata.loss,
                    'metrics': metadata.metrics,
                    'config': metadata.config,
                    'timestamp': metadata.timestamp,
                },
                'pytorch_version': torch.__version__,
            }
            
            # Add optimizer state if provided
            if optimizer is not None:
                checkpoint_data['optimizer_state_dict'] = optimizer.state_dict()
                checkpoint_data['optimizer_type'] = type(optimizer).__name__
            
            # Add scheduler state if provided
            if scheduler is not None:
                checkpoint_data['scheduler_state_dict'] = scheduler.state_dict()
                checkpoint_data['scheduler_type'] = type(scheduler).__name__
            
            # Save checkpoint
            torch.save(checkpoint_data, checkpoint_path)
            
            # Calculate file hash for integrity checking
            file_hash = self._calculate_file_hash(checkpoint_path)
            file_size = checkpoint_path.stat().st_size
            
            # Update registry
            registry_entry = {
                'path': str(checkpoint_path),
                'created_at': metadata.timestamp,
                'size_bytes': file_size,
                'file_hash': file_hash,
                'is_best': is_best,
                'metadata': {
                    'epoch': metadata.epoch,
                    'step': metadata.step,
                    'loss': metadata.loss,
                    'metrics': metadata.metrics,
                }
            }
            
            self.registry[checkpoint_name] = registry_entry
            
            # Mark as best if specified
            if is_best:
                self._update_best_checkpoint(checkpoint_name)
            
            # Clean up old checkpoints
            if keep_last_n > 0:
                self._cleanup_old_checkpoints(keep_last_n)
            
            # Save registry
            self._save_checkpoint_registry()
            
            logger.info(
                f"Checkpoint saved: {checkpoint_name} at {checkpoint_path}"
            )
            
            return str(checkpoint_path)
            
        except Exception as e:
            raise CheckpointError(
                f"Failed to save checkpoint: {str(e)}",
                checkpoint_path=str(checkpoint_path) if 'checkpoint_path' in locals() else None,
                operation="save",
                cause=e
            ) from e
    
    def load_checkpoint(
        self,
        checkpoint_path: Union[str, Path],
        model: Optional[torch.nn.Module] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        scheduler: Optional[Any] = None,
        device: Optional[Union[str, torch.device]] = None,
        strict: bool = True
    ) -> Dict[str, Any]:
        """
        Load a model checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint file
            model: Optional model to load state into
            optimizer: Optional optimizer to load state into
            scheduler: Optional scheduler to load state into
            device: Device to load checkpoint on
            strict: Whether to strictly enforce state dict matching
            
        Returns:
            Dict[str, Any]: Checkpoint data including metadata
            
        Raises:
            CheckpointError: If loading fails
        """
        try:
            checkpoint_path = Path(checkpoint_path)
            
            if not checkpoint_path.exists():
                raise CheckpointError(
                    f"Checkpoint file not found: {checkpoint_path}",
                    checkpoint_path=str(checkpoint_path),
                    operation="load"
                )
            
            # Load checkpoint data
            if device:
                checkpoint_data = torch.load(checkpoint_path, map_location=device)
            else:
                checkpoint_data = torch.load(checkpoint_path)
            
            # Validate checkpoint structure
            if 'model_state_dict' not in checkpoint_data:
                raise CheckpointError(
                    "Invalid checkpoint format: missing model_state_dict",
                    checkpoint_path=str(checkpoint_path),
                    operation="load"
                )
            
            # Load model state
            if model is not None:
                try:
                    model.load_state_dict(checkpoint_data['model_state_dict'], strict=strict)
                    logger.info(f"Model state loaded from {checkpoint_path}")
                except Exception as e:
                    if strict:
                        raise CheckpointError(
                            f"Failed to load model state: {str(e)}",
                            checkpoint_path=str(checkpoint_path),
                            operation="load_model",
                            cause=e
                        )
                    else:
                        logger.warning(f"Partial model state loaded: {str(e)}")
            
            # Load optimizer state
            if optimizer is not None and 'optimizer_state_dict' in checkpoint_data:
                try:
                    optimizer.load_state_dict(checkpoint_data['optimizer_state_dict'])
                    logger.info("Optimizer state loaded")
                except Exception as e:
                    logger.warning(f"Failed to load optimizer state: {str(e)}")
            
            # Load scheduler state
            if scheduler is not None and 'scheduler_state_dict' in checkpoint_data:
                try:
                    scheduler.load_state_dict(checkpoint_data['scheduler_state_dict'])
                    logger.info("Scheduler state loaded")
                except Exception as e:
                    logger.warning(f"Failed to load scheduler state: {str(e)}")
            
            logger.info(f"Checkpoint loaded successfully: {checkpoint_path}")
            return checkpoint_data
            
        except CheckpointError:
            raise
        except Exception as e:
            raise CheckpointError(
                f"Failed to load checkpoint: {str(e)}",
                checkpoint_path=str(checkpoint_path),
                operation="load",
                cause=e
            ) from e
    
    def list_checkpoints(self, sort_by: str = "created_at") -> List[Dict[str, Any]]:
        """
        List all available checkpoints.
        
        Args:
            sort_by: Sort key (created_at, epoch, step, loss)
            
        Returns:
            List[Dict[str, Any]]: List of checkpoint information
        """
        checkpoints = []
        
        for name, info in self.registry.items():
            checkpoint_info = {
                'name': name,
                'path': info['path'],
                'created_at': info['created_at'],
                'size_mb': info['size_bytes'] / (1024 * 1024),
                **info.get('metadata', {})
            }
            checkpoints.append(checkpoint_info)
        
        # Sort checkpoints
        if sort_by == "created_at":
            checkpoints.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif sort_by == "epoch":
            checkpoints.sort(key=lambda x: x.get('epoch', 0), reverse=True)
        elif sort_by == "step":
            checkpoints.sort(key=lambda x: x.get('step', 0), reverse=True)
        elif sort_by == "loss":
            checkpoints.sort(key=lambda x: x.get('loss', float('inf')))
        
        return checkpoints
    
    def get_best_checkpoint(self, metric: str = "loss", minimize: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get the best checkpoint based on a metric.
        
        Args:
            metric: Metric to optimize (loss, epoch, step)
            minimize: Whether to minimize the metric
            
        Returns:
            Optional[Dict[str, Any]]: Best checkpoint info or None
        """
        checkpoints = self.list_checkpoints()
        
        if not checkpoints:
            return None
        
        # Filter checkpoints that have the metric
        valid_checkpoints = [cp for cp in checkpoints if metric in cp and cp[metric] is not None]
        
        if not valid_checkpoints:
            return None
        
        # Find best checkpoint
        if minimize:
            best_checkpoint = min(valid_checkpoints, key=lambda x: x[metric])
        else:
            best_checkpoint = max(valid_checkpoints, key=lambda x: x[metric])
        
        return best_checkpoint
    
    def get_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent checkpoint.
        
        Returns:
            Optional[Dict[str, Any]]: Latest checkpoint info or None
        """
        checkpoints = self.list_checkpoints(sort_by="created_at")
        return checkpoints[0] if checkpoints else None
    
    def delete_checkpoint(self, checkpoint_name: str) -> bool:
        """
        Delete a checkpoint.
        
        Args:
            checkpoint_name: Name of checkpoint to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            if checkpoint_name not in self.registry:
                logger.warning(f"Checkpoint not found in registry: {checkpoint_name}")
                return False
            
            checkpoint_path = Path(self.registry[checkpoint_name]['path'])
            
            # Delete file if it exists
            if checkpoint_path.exists():
                checkpoint_path.unlink()
            
            # Remove from registry
            del self.registry[checkpoint_name]
            self._save_checkpoint_registry()
            
            logger.info(f"Checkpoint deleted: {checkpoint_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete checkpoint {checkpoint_name}: {e}")
            return False
    
    def cleanup_old_checkpoints(self, keep_count: int = 5, keep_best: bool = True) -> int:
        """
        Clean up old checkpoints, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent checkpoints to keep
            keep_best: Whether to always keep the best checkpoint
            
        Returns:
            int: Number of checkpoints deleted
        """
        checkpoints = self.list_checkpoints(sort_by="created_at")
        
        if len(checkpoints) <= keep_count:
            return 0
        
        # Determine which checkpoints to keep
        to_keep = set()
        
        # Keep most recent
        for cp in checkpoints[:keep_count]:
            to_keep.add(cp['name'])
        
        # Keep best checkpoint if requested
        if keep_best:
            best_cp = self.get_best_checkpoint()
            if best_cp:
                to_keep.add(best_cp['name'])
        
        # Delete old checkpoints
        deleted_count = 0
        for cp in checkpoints:
            if cp['name'] not in to_keep:
                if self.delete_checkpoint(cp['name']):
                    deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old checkpoints")
        return deleted_count
    
    def validate_checkpoint(self, checkpoint_path: Union[str, Path]) -> Tuple[bool, List[str]]:
        """
        Validate a checkpoint file.
        
        Args:
            checkpoint_path: Path to checkpoint file
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        checkpoint_path = Path(checkpoint_path)
        
        try:
            # Check if file exists
            if not checkpoint_path.exists():
                errors.append(f"Checkpoint file not found: {checkpoint_path}")
                return False, errors
            
            # Try to load checkpoint
            checkpoint_data = torch.load(checkpoint_path, map_location='cpu')
            
            # Check required fields
            if 'model_state_dict' not in checkpoint_data:
                errors.append("Missing model_state_dict")
            
            # Validate model state dict
            if 'model_state_dict' in checkpoint_data:
                model_state = checkpoint_data['model_state_dict']
                if not isinstance(model_state, dict):
                    errors.append("model_state_dict is not a dictionary")
                elif len(model_state) == 0:
                    errors.append("model_state_dict is empty")
            
            # Check metadata if present
            if 'metadata' in checkpoint_data:
                metadata = checkpoint_data['metadata']
                if not isinstance(metadata, dict):
                    errors.append("metadata is not a dictionary")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Failed to load checkpoint: {str(e)}")
            return False, errors
    
    def _load_checkpoint_registry(self) -> Dict[str, Any]:
        """Load checkpoint registry from file."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load checkpoint registry: {str(e)}")
        return {}
    
    def _save_checkpoint_registry(self) -> None:
        """Save checkpoint registry to file."""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save checkpoint registry: {str(e)}")
    
    def _update_best_checkpoint(self, checkpoint_name: str) -> None:
        """Mark a checkpoint as the best one."""
        # Remove best flag from all other checkpoints
        for info in self.registry.values():
            info['is_best'] = False
        
        # Mark current checkpoint as best
        self.registry[checkpoint_name]['is_best'] = True
    
    def _cleanup_old_checkpoints(self, keep_last_n: int) -> None:
        """Remove old checkpoints, keeping only the last N."""
        checkpoints = self.list_checkpoints(sort_by="created_at")
        
        if len(checkpoints) <= keep_last_n:
            return
        
        # Determine which checkpoints to keep
        to_keep = set()
        
        # Keep most recent
        for cp in checkpoints[:keep_last_n]:
            to_keep.add(cp['name'])
        
        # Always keep best checkpoint
        for name, info in self.registry.items():
            if info.get('is_best', False):
                to_keep.add(name)
        
        # Delete old checkpoints
        to_delete = set(self.registry.keys()) - to_keep
        for name in to_delete:
            self.delete_checkpoint(name)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


# Global checkpoint manager instance
_global_checkpoint_manager = CheckpointManager()


def save_checkpoint(
    model: torch.nn.Module,
    optimizer: Optional[torch.optim.Optimizer] = None,
    scheduler: Optional[Any] = None,
    metadata: Optional[CheckpointMetadata] = None,
    checkpoint_name: Optional[str] = None,
    checkpoint_dir: Optional[Union[str, Path]] = None,
    **kwargs
) -> str:
    """
    Save a checkpoint using the global checkpoint manager.
    
    Args:
        model: PyTorch model to save
        optimizer: Optional optimizer state
        scheduler: Optional scheduler state
        metadata: Checkpoint metadata
        checkpoint_name: Custom checkpoint name
        checkpoint_dir: Custom checkpoint directory
        **kwargs: Additional arguments
        
    Returns:
        str: Path to saved checkpoint
    """
    if checkpoint_dir:
        manager = CheckpointManager(checkpoint_dir)
    else:
        manager = _global_checkpoint_manager
    
    return manager.save_checkpoint(
        model, optimizer, scheduler, metadata, checkpoint_name, **kwargs
    )


def load_checkpoint(
    checkpoint_path: Union[str, Path],
    model: Optional[torch.nn.Module] = None,
    optimizer: Optional[torch.optim.Optimizer] = None,
    scheduler: Optional[Any] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Load a checkpoint using the global checkpoint manager.
    
    Args:
        checkpoint_path: Path to checkpoint file
        model: Optional model to load state into
        optimizer: Optional optimizer to load state into
        scheduler: Optional scheduler to load state into
        **kwargs: Additional arguments
        
    Returns:
        Dict[str, Any]: Checkpoint data
    """
    return _global_checkpoint_manager.load_checkpoint(
        checkpoint_path, model, optimizer, scheduler, **kwargs
    )


def list_checkpoints(**kwargs) -> List[Dict[str, Any]]:
    """List checkpoints using the global checkpoint manager."""
    return _global_checkpoint_manager.list_checkpoints(**kwargs)


def get_best_checkpoint(**kwargs) -> Optional[Dict[str, Any]]:
    """Get best checkpoint using the global checkpoint manager."""
    return _global_checkpoint_manager.get_best_checkpoint(**kwargs)


def get_latest_checkpoint() -> Optional[Dict[str, Any]]:
    """Get latest checkpoint using the global checkpoint manager."""
    return _global_checkpoint_manager.get_latest_checkpoint()