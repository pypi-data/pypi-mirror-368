"""
Model builder and management utilities for LLMBuilder.

This module provides the ModelBuilder factory class for creating, loading,
and saving models with comprehensive validation and metadata management.
"""

import json
import torch
from pathlib import Path
from typing import Dict, Any, Optional, Union, Type
from dataclasses import asdict

from ..utils import ModelError, get_logger, save_checkpoint, load_checkpoint
from ..config import ModelConfig
from .gpt import GPTModel, GPTModelMetadata

logger = get_logger("model.builder")


class ModelBuilder:
    """
    Factory class for building and managing models.
    
    Provides a unified interface for creating different model types,
    loading/saving models, and managing model metadata.
    """
    
    # Registry of available model types
    MODEL_REGISTRY = {
        'gpt': GPTModel,
    }
    
    def __init__(self):
        """Initialize model builder."""
        logger.info("ModelBuilder initialized")
    
    @classmethod
    def build_model(cls, config: Union[ModelConfig, Dict[str, Any]]) -> GPTModel:
        """
        Build a model from configuration.
        
        Args:
            config: Model configuration (ModelConfig or dict)
            
        Returns:
            Model instance
            
        Raises:
            ModelError: If model type is unsupported or config is invalid
        """
        # Convert dict to ModelConfig if needed
        if isinstance(config, dict):
            try:
                config = ModelConfig(**config)
            except Exception as e:
                raise ModelError(f"Invalid model configuration: {str(e)}") from e
        
        # Validate configuration
        cls._validate_config(config)
        
        # Get model class
        model_type = config.model_type.lower()
        if model_type not in cls.MODEL_REGISTRY:
            raise ModelError(f"Unsupported model type: {model_type}")
        
        model_class = cls.MODEL_REGISTRY[model_type]
        
        logger.info(f"Building {model_type} model with vocab_size={config.vocab_size}")
        
        try:
            # Create model
            if model_type == 'gpt':
                model = model_class(
                    vocab_size=config.vocab_size,
                    n_layer=config.num_layers,
                    n_head=config.num_heads,
                    n_embd=config.embedding_dim,
                    block_size=config.max_seq_length,
                    dropout=config.dropout
                )
            else:
                # For future model types
                model = model_class.from_config(config)
            
            logger.info(f"Model built successfully: {model.get_num_params():,} parameters")
            return model
            
        except Exception as e:
            raise ModelError(f"Failed to build model: {str(e)}") from e
    
    @classmethod
    def load_model(cls, 
                   model_path: Union[str, Path],
                   device: Optional[str] = None,
                   strict: bool = True) -> GPTModel:
        """
        Load a model from checkpoint.
        
        Args:
            model_path: Path to model checkpoint
            device: Device to load model on (cpu/cuda)
            strict: Whether to strictly enforce state dict matching
            
        Returns:
            Loaded model
            
        Raises:
            ModelError: If loading fails
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise ModelError(f"Model checkpoint not found: {model_path}")
        
        logger.info(f"Loading model from {model_path}")
        
        try:
            # Load checkpoint
            checkpoint = load_checkpoint(model_path, device=device)
            
            # Extract model configuration
            if 'model_config' in checkpoint:
                config_dict = checkpoint['model_config']
            elif 'config' in checkpoint:
                config_dict = checkpoint['config']
            else:
                raise ModelError("No model configuration found in checkpoint")
            
            # Build model from config
            model = cls.build_model(config_dict)
            
            # Load state dict
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                raise ModelError("No model state dict found in checkpoint")
            
            model.load_state_dict(state_dict, strict=strict)
            
            # Log loading info
            if 'metadata' in checkpoint:
                metadata = checkpoint['metadata']
                logger.info(f"Loaded model: {metadata.get('num_parameters', 'unknown')} parameters")
            
            logger.info("Model loaded successfully")
            return model
            
        except Exception as e:
            raise ModelError(f"Failed to load model: {str(e)}") from e
    
    @classmethod
    def save_model(cls, 
                   model: GPTModel, 
                   save_path: Union[str, Path],
                   include_optimizer: bool = False,
                   optimizer_state: Optional[Dict] = None,
                   additional_info: Optional[Dict[str, Any]] = None) -> None:
        """
        Save a model checkpoint.
        
        Args:
            model: Model to save
            save_path: Path to save checkpoint
            include_optimizer: Whether to include optimizer state
            optimizer_state: Optimizer state dict (if include_optimizer=True)
            additional_info: Additional information to save
            
        Raises:
            ModelError: If saving fails
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving model to {save_path}")
        
        try:
            # Prepare checkpoint data
            checkpoint_data = {
                'model_state_dict': model.state_dict(),
                'model_config': model.get_config_dict(),
                'metadata': asdict(model.get_metadata()),
                'model_type': 'gpt'
            }
            
            # Add optimizer state if requested
            if include_optimizer and optimizer_state is not None:
                checkpoint_data['optimizer_state_dict'] = optimizer_state
            
            # Add additional info
            if additional_info:
                checkpoint_data.update(additional_info)
            
            # Save checkpoint directly with torch.save
            torch.save(checkpoint_data, save_path)
            
            # Save metadata separately for easy access
            metadata_path = save_path.with_suffix('.metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(checkpoint_data['metadata'], f, indent=2)
            
            logger.info(f"Model saved successfully: {save_path}")
            logger.info(f"Metadata saved: {metadata_path}")
            
        except Exception as e:
            raise ModelError(f"Failed to save model: {str(e)}") from e
    
    @classmethod
    def validate_model(cls, model: GPTModel) -> Dict[str, Any]:
        """
        Validate a model instance.
        
        Args:
            model: Model to validate
            
        Returns:
            Dict with validation results
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        try:
            # Basic model checks
            if not isinstance(model, torch.nn.Module):
                validation_results['errors'].append("Model is not a PyTorch module")
                validation_results['valid'] = False
            
            # Parameter count check
            num_params = model.get_num_params()
            validation_results['info']['num_parameters'] = num_params
            
            if num_params == 0:
                validation_results['errors'].append("Model has no parameters")
                validation_results['valid'] = False
            
            # Architecture validation
            if hasattr(model, 'vocab_size') and model.vocab_size <= 0:
                validation_results['errors'].append("Invalid vocab_size")
                validation_results['valid'] = False
            
            if hasattr(model, 'n_layer') and model.n_layer <= 0:
                validation_results['errors'].append("Invalid n_layer")
                validation_results['valid'] = False
            
            if hasattr(model, 'n_head') and model.n_head <= 0:
                validation_results['errors'].append("Invalid n_head")
                validation_results['valid'] = False
            
            # Memory usage estimation
            if hasattr(model, 'estimate_memory_usage'):
                memory_info = model.estimate_memory_usage(batch_size=1, sequence_length=256)
                validation_results['info']['memory_usage'] = memory_info
                
                # Warning for large models
                if memory_info['total_mb'] > 1000:  # > 1GB
                    validation_results['warnings'].append(
                        f"Large model detected: {memory_info['total_mb']:.1f} MB estimated memory usage"
                    )
            
            # Test forward pass with dummy input
            try:
                model.eval()
                with torch.no_grad():
                    dummy_input = torch.randint(0, min(model.vocab_size, 100), (1, 10))
                    logits, _ = model(dummy_input)
                    
                    if logits.shape != (1, 10, model.vocab_size):
                        validation_results['errors'].append(
                            f"Unexpected output shape: {logits.shape}"
                        )
                        validation_results['valid'] = False
                    else:
                        validation_results['info']['forward_pass'] = 'success'
                        
            except Exception as e:
                validation_results['errors'].append(f"Forward pass failed: {str(e)}")
                validation_results['valid'] = False
            
            logger.info(f"Model validation: {'PASSED' if validation_results['valid'] else 'FAILED'}")
            
        except Exception as e:
            validation_results['errors'].append(f"Validation error: {str(e)}")
            validation_results['valid'] = False
        
        return validation_results
    
    @classmethod
    def get_model_info(cls, model_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about a saved model without loading it.
        
        Args:
            model_path: Path to model checkpoint
            
        Returns:
            Dict with model information
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise ModelError(f"Model checkpoint not found: {model_path}")
        
        try:
            # Try to load just the metadata
            checkpoint = torch.load(model_path, map_location='cpu')
            
            info = {
                'path': str(model_path),
                'file_size_mb': model_path.stat().st_size / (1024 * 1024),
                'exists': True
            }
            
            # Extract available information
            if 'metadata' in checkpoint:
                info.update(checkpoint['metadata'])
            
            if 'model_config' in checkpoint:
                info['config'] = checkpoint['model_config']
            
            if 'model_type' in checkpoint:
                info['model_type'] = checkpoint['model_type']
            
            return info
            
        except Exception as e:
            return {
                'path': str(model_path),
                'exists': model_path.exists(),
                'error': str(e)
            }
    
    @classmethod
    def _validate_config(cls, config: ModelConfig) -> None:
        """Validate model configuration."""
        if config.vocab_size <= 0:
            raise ModelError("vocab_size must be positive")
        
        if config.num_layers <= 0:
            raise ModelError("num_layers must be positive")
        
        if config.num_heads <= 0:
            raise ModelError("num_heads must be positive")
        
        if config.embedding_dim <= 0:
            raise ModelError("embedding_dim must be positive")
        
        if config.embedding_dim % config.num_heads != 0:
            raise ModelError(f"embedding_dim ({config.embedding_dim}) must be divisible by num_heads ({config.num_heads})")
        
        if config.max_seq_length <= 0:
            raise ModelError("max_seq_length must be positive")
        
        if not 0 <= config.dropout <= 1:
            raise ModelError("dropout must be between 0 and 1")
    
    @classmethod
    def list_supported_models(cls) -> Dict[str, Type]:
        """Get list of supported model types."""
        return cls.MODEL_REGISTRY.copy()
    
    @classmethod
    def register_model(cls, name: str, model_class: Type) -> None:
        """
        Register a new model type.
        
        Args:
            name: Model type name
            model_class: Model class
        """
        cls.MODEL_REGISTRY[name.lower()] = model_class
        logger.info(f"Registered model type: {name}")


# Convenience functions for the API
def build_model(config: Union[ModelConfig, Dict[str, Any]]) -> GPTModel:
    """Build a model from configuration."""
    return ModelBuilder.build_model(config)


def load_model(model_path: Union[str, Path], 
               device: Optional[str] = None,
               strict: bool = True) -> GPTModel:
    """Load a model from checkpoint."""
    return ModelBuilder.load_model(model_path, device, strict)


def save_model(model: GPTModel, 
               save_path: Union[str, Path],
               include_optimizer: bool = False,
               optimizer_state: Optional[Dict] = None,
               additional_info: Optional[Dict[str, Any]] = None) -> None:
    """Save a model checkpoint."""
    return ModelBuilder.save_model(model, save_path, include_optimizer, optimizer_state, additional_info)


def validate_model(model: GPTModel) -> Dict[str, Any]:
    """Validate a model instance."""
    return ModelBuilder.validate_model(model)