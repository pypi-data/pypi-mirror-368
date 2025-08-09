"""
Text generation module for LLMBuilder.

This module provides the TextGenerator class for generating text from trained models
with various sampling strategies and configuration options.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
from dataclasses import dataclass

import torch
import torch.nn.functional as F

from ..utils import get_logger, ModelError, ConfigurationError
from ..model import load_model
from ..tokenizer import TokenizerManager

logger = get_logger("inference.generate")


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_new_tokens: int = 100
    temperature: float = 0.8
    top_k: Optional[int] = 50
    top_p: Optional[float] = 0.9
    do_sample: bool = True
    repetition_penalty: float = 1.0
    length_penalty: float = 1.0
    early_stopping: bool = True
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.max_new_tokens <= 0:
            raise ConfigurationError("max_new_tokens must be positive")
        
        if self.temperature <= 0:
            raise ConfigurationError("temperature must be positive")
        
        if self.top_k is not None and self.top_k <= 0:
            raise ConfigurationError("top_k must be positive")
        
        if self.top_p is not None and not (0 < self.top_p <= 1):
            raise ConfigurationError("top_p must be between 0 and 1")
        
        if self.repetition_penalty <= 0:
            raise ConfigurationError("repetition_penalty must be positive")


class TextGenerator:
    """
    Text generation class for trained LLM models.
    
    This class provides text generation capabilities with various sampling strategies
    including temperature scaling, top-k, top-p (nucleus) sampling, and repetition penalty.
    """
    
    def __init__(self, 
                 model_path: Union[str, Path],
                 tokenizer_path: Union[str, Path],
                 device: Optional[str] = None,
                 config: Optional[GenerationConfig] = None):
        """
        Initialize the text generator.
        
        Args:
            model_path: Path to trained model checkpoint
            tokenizer_path: Path to tokenizer directory or file
            device: Device to run inference on (auto-detect if None)
            config: Generation configuration (uses defaults if None)
        """
        self.model_path = Path(model_path)
        self.tokenizer_path = Path(tokenizer_path)
        self.config = config or GenerationConfig()
        
        # Setup device
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                logger.info("Using CUDA for inference")
            else:
                self.device = torch.device("cpu")
                logger.info("Using CPU for inference")
        else:
            self.device = torch.device(device)
            logger.info(f"Using {device} for inference")
        
        # Load tokenizer and model
        self.tokenizer = self._load_tokenizer()
        self.model = self._load_model()
        
        # Set special token IDs
        if self.config.eos_token_id is None:
            if hasattr(self.tokenizer, 'eos_id'):
                self.config.eos_token_id = self.tokenizer.eos_id()
            elif hasattr(self.tokenizer, 'tokenizer') and hasattr(self.tokenizer.tokenizer, 'eos_id'):
                self.config.eos_token_id = self.tokenizer.tokenizer.eos_id()
        
        if self.config.pad_token_id is None:
            if hasattr(self.tokenizer, 'pad_id'):
                self.config.pad_token_id = self.tokenizer.pad_id()
            elif hasattr(self.tokenizer, 'tokenizer') and hasattr(self.tokenizer.tokenizer, 'pad_id'):
                self.config.pad_token_id = self.tokenizer.tokenizer.pad_id()
        
        logger.info("Text generator initialized successfully")
    
    def _load_tokenizer(self):
        """Load the tokenizer."""
        try:
            # First try to load as SentencePiece tokenizer directly
            import sentencepiece as spm
            
            # Check if it's a SentencePiece tokenizer
            tokenizer_model_path = self.tokenizer_path / "tokenizer.model"
            if tokenizer_model_path.exists():
                tokenizer = spm.SentencePieceProcessor()
                tokenizer.load(str(tokenizer_model_path))
                logger.info(f"Loaded SentencePiece tokenizer from {tokenizer_model_path}")
                logger.info(f"Vocabulary size: {tokenizer.vocab_size()}")
                return tokenizer
            
            # Fallback to TokenizerManager for HuggingFace tokenizers
            tokenizer_manager = TokenizerManager()
            tokenizer_manager.load_tokenizer(self.tokenizer_path)
            logger.info(f"Loaded HuggingFace tokenizer from {self.tokenizer_path}")
            logger.info(f"Vocabulary size: {tokenizer_manager.vocab_size}")
            return tokenizer_manager
            
        except Exception as e:
            logger.error(f"Failed to load tokenizer: {e}")
            raise ModelError(f"Failed to load tokenizer from {self.tokenizer_path}: {e}")
    
    def _load_model(self):
        """Load the trained model."""
        try:
            model = load_model(self.model_path)
            model.to(self.device)
            model.eval()
            
            # Count parameters
            total_params = sum(p.numel() for p in model.parameters())
            logger.info(f"Loaded model with {total_params:,} parameters")
            
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise ModelError(f"Failed to load model from {self.model_path}: {e}")
    
    def generate(self, 
                prompt: str,
                config: Optional[GenerationConfig] = None,
                **kwargs) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration (overrides instance config)
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        # Use provided config or instance config
        gen_config = config or self.config
        
        # Override config with kwargs
        if kwargs:
            gen_config = GenerationConfig(**{**gen_config.__dict__, **kwargs})
        
        logger.info(f"Generating text for prompt: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
        
        try:
            # Tokenize prompt
            if hasattr(self.tokenizer, 'encode'):
                # SentencePiece tokenizer
                input_ids = self.tokenizer.encode(prompt)
            else:
                # HuggingFace tokenizer via TokenizerManager
                input_ids = self.tokenizer.encode(prompt)
            input_tensor = torch.tensor([input_ids], device=self.device)
            
            logger.debug(f"Input tokens: {len(input_ids)}")
            
            # Generate tokens
            with torch.no_grad():
                generated_ids = self._generate_tokens(input_tensor, gen_config)
            
            # Decode generated text
            if hasattr(self.tokenizer, 'decode'):
                # SentencePiece tokenizer
                generated_text = self.tokenizer.decode(generated_ids[0].tolist())
            else:
                # HuggingFace tokenizer via TokenizerManager
                generated_text = self.tokenizer.decode(generated_ids[0].tolist())
            
            logger.info(f"Generated {generated_ids.size(1) - input_tensor.size(1)} new tokens")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise ModelError(f"Text generation failed: {e}")
    
    def _generate_tokens(self, 
                        input_ids: torch.Tensor, 
                        config: GenerationConfig) -> torch.Tensor:
        """
        Generate tokens using the model.
        
        Args:
            input_ids: Input token tensor [batch_size, seq_len]
            config: Generation configuration
            
        Returns:
            Generated token tensor [batch_size, seq_len + new_tokens]
        """
        batch_size, seq_len = input_ids.shape
        generated_ids = input_ids.clone()
        
        for step in range(config.max_new_tokens):
            # Prepare input (crop if too long)
            if generated_ids.size(1) > self.model.block_size:
                model_input = generated_ids[:, -self.model.block_size:]
            else:
                model_input = generated_ids
            
            # Forward pass
            logits, _ = self.model(model_input)
            
            # Get logits for the last token
            next_token_logits = logits[:, -1, :] / config.temperature
            
            # Apply repetition penalty
            if config.repetition_penalty != 1.0:
                next_token_logits = self._apply_repetition_penalty(
                    next_token_logits, generated_ids, config.repetition_penalty
                )
            
            # Apply sampling strategies
            if config.do_sample:
                next_token = self._sample_next_token(next_token_logits, config)
            else:
                # Greedy decoding
                next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            
            # Append to sequence
            generated_ids = torch.cat([generated_ids, next_token], dim=1)
            
            # Check for early stopping
            if config.early_stopping and config.eos_token_id is not None:
                if next_token.item() == config.eos_token_id:
                    break
        
        return generated_ids
    
    def _apply_repetition_penalty(self, 
                                 logits: torch.Tensor, 
                                 generated_ids: torch.Tensor, 
                                 penalty: float) -> torch.Tensor:
        """Apply repetition penalty to logits."""
        for batch_idx in range(logits.size(0)):
            for token_id in set(generated_ids[batch_idx].tolist()):
                if logits[batch_idx, token_id] < 0:
                    logits[batch_idx, token_id] *= penalty
                else:
                    logits[batch_idx, token_id] /= penalty
        return logits
    
    def _sample_next_token(self, 
                          logits: torch.Tensor, 
                          config: GenerationConfig) -> torch.Tensor:
        """Sample next token using configured sampling strategy."""
        # Apply top-k filtering
        if config.top_k is not None and config.top_k > 0:
            top_k = min(config.top_k, logits.size(-1))
            indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
            logits[indices_to_remove] = float('-inf')
        
        # Apply top-p (nucleus) filtering
        if config.top_p is not None and config.top_p < 1.0:
            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
            cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
            
            # Remove tokens with cumulative probability above the threshold
            sorted_indices_to_remove = cumulative_probs > config.top_p
            # Shift the indices to the right to keep also the first token above the threshold
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0
            
            indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
            logits[indices_to_remove] = float('-inf')
        
        # Sample from the filtered distribution
        probs = F.softmax(logits, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)
        
        return next_token
    
    def generate_batch(self, 
                      prompts: List[str],
                      config: Optional[GenerationConfig] = None,
                      **kwargs) -> List[str]:
        """
        Generate text for multiple prompts in batch.
        
        Args:
            prompts: List of input prompts
            config: Generation configuration
            **kwargs: Additional generation parameters
            
        Returns:
            List of generated texts
        """
        logger.info(f"Generating text for {len(prompts)} prompts")
        
        results = []
        for prompt in prompts:
            try:
                result = self.generate(prompt, config, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to generate for prompt '{prompt[:30]}...': {e}")
                results.append("")
        
        return results
    
    def update_config(self, **kwargs):
        """Update generation configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.debug(f"Updated config: {key} = {value}")
            else:
                logger.warning(f"Unknown config parameter: {key}")


def generate_text(model_path: Union[str, Path],
                 tokenizer_path: Union[str, Path],
                 prompt: str,
                 device: Optional[str] = None,
                 **kwargs) -> str:
    """
    Convenience function for single text generation.
    
    Args:
        model_path: Path to trained model checkpoint
        tokenizer_path: Path to tokenizer directory
        prompt: Input text prompt
        device: Device to run inference on
        **kwargs: Generation parameters
        
    Returns:
        Generated text
    """
    generator = TextGenerator(
        model_path=model_path,
        tokenizer_path=tokenizer_path,
        device=device
    )
    
    return generator.generate(prompt, **kwargs)