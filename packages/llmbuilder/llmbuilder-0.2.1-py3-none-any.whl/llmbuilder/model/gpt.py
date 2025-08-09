"""
GPT model architecture implementation for LLMBuilder.

This module provides a comprehensive GPT-style transformer model implementation
optimized for CPU training with configurable parameters and efficient attention.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

from ..utils import ModelError, get_logger
from ..config import ModelConfig

logger = get_logger("model.gpt")


@dataclass
class GPTModelMetadata:
    """Metadata for GPT model instances."""
    vocab_size: int
    n_layer: int
    n_head: int
    n_embd: int
    block_size: int
    dropout: float
    num_parameters: int
    model_type: str = "gpt"
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'vocab_size': self.vocab_size,
            'n_layer': self.n_layer,
            'n_head': self.n_head,
            'n_embd': self.n_embd,
            'block_size': self.block_size,
            'dropout': self.dropout,
            'num_parameters': self.num_parameters,
            'model_type': self.model_type,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GPTModelMetadata':
        """Create metadata from dictionary."""
        return cls(**data)


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism optimized for CPU."""
    
    def __init__(self, n_embd: int, n_head: int, dropout: float = 0.1, block_size: int = 1024):
        super().__init__()
        if n_embd % n_head != 0:
            raise ModelError(f"Embedding dimension {n_embd} must be divisible by number of heads {n_head}")
        
        self.n_embd = n_embd
        self.n_head = n_head
        self.head_dim = n_embd // n_head
        self.scale = 1.0 / math.sqrt(self.head_dim)
        
        # Combined linear layer for efficiency
        self.qkv_proj = nn.Linear(n_embd, 3 * n_embd, bias=False)
        self.out_proj = nn.Linear(n_embd, n_embd)
        
        # Dropout
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)
        
        # Causal mask
        self.register_buffer(
            "causal_mask",
            torch.tril(torch.ones(block_size, block_size)).view(1, 1, block_size, block_size)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.size()  # batch, sequence, embedding
        
        # Compute Q, K, V
        qkv = self.qkv_proj(x)
        q, k, v = qkv.chunk(3, dim=-1)
        
        # Reshape for multi-head attention
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)  # (B, n_head, T, head_dim)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        
        # Attention scores
        att = torch.matmul(q, k.transpose(-2, -1)) * self.scale  # (B, n_head, T, T)
        
        # Apply causal mask
        att = att.masked_fill(self.causal_mask[:, :, :T, :T] == 0, float('-inf'))
        
        # Softmax and dropout
        att = F.softmax(att, dim=-1)
        att = self.attn_dropout(att)
        
        # Apply attention to values
        out = torch.matmul(att, v)  # (B, n_head, T, head_dim)
        
        # Concatenate heads
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        
        # Output projection
        out = self.out_proj(out)
        out = self.resid_dropout(out)
        
        return out


class MLP(nn.Module):
    """Feed-forward network with GELU activation."""
    
    def __init__(self, n_embd: int, dropout: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(n_embd, 4 * n_embd)
        self.fc2 = nn.Linear(4 * n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = F.gelu(x)
        x = self.fc2(x)
        x = self.dropout(x)
        return x


class TransformerBlock(nn.Module):
    """Single transformer block with attention and MLP."""
    
    def __init__(self, n_embd: int, n_head: int, dropout: float = 0.1, block_size: int = 1024):
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)
        self.attn = MultiHeadAttention(n_embd, n_head, dropout, block_size)
        self.ln2 = nn.LayerNorm(n_embd)
        self.mlp = MLP(n_embd, dropout)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pre-norm architecture for better training stability
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class GPTModel(nn.Module):
    """
    GPT model implementation with configurable architecture.
    
    This implementation provides a complete GPT-style transformer model
    with multi-head attention, feed-forward networks, and causal masking.
    Optimized for CPU training with efficient memory usage.
    """
    
    def __init__(self, 
                 vocab_size: int,
                 n_layer: int = 6,
                 n_head: int = 6,
                 n_embd: int = 512,
                 block_size: int = 256,
                 dropout: float = 0.1):
        """
        Initialize GPT model.
        
        Args:
            vocab_size: Size of vocabulary
            n_layer: Number of transformer layers
            n_head: Number of attention heads
            n_embd: Embedding dimension
            block_size: Maximum sequence length
            dropout: Dropout probability
            
        Raises:
            ModelError: If configuration is invalid
        """
        super().__init__()
        
        # Validate configuration
        self._validate_config(vocab_size, n_layer, n_head, n_embd, block_size, dropout)
        
        # Store configuration
        self.vocab_size = vocab_size
        self.n_layer = n_layer
        self.n_head = n_head
        self.n_embd = n_embd
        self.block_size = block_size
        self.dropout = dropout
        
        # Token and position embeddings
        self.token_embedding = nn.Embedding(vocab_size, n_embd)
        self.position_embedding = nn.Embedding(block_size, n_embd)
        self.dropout_emb = nn.Dropout(dropout)
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(n_embd, n_head, dropout, block_size)
            for _ in range(n_layer)
        ])
        
        # Final layer norm and output projection
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)
        
        # Tie weights between token embedding and output projection
        self.lm_head.weight = self.token_embedding.weight
        
        # Initialize weights
        self.apply(self._init_weights)
        
        # Log model info
        n_params = self.get_num_params()
        logger.info(f"GPT model initialized with {n_params:,} parameters")
        logger.info(f"Architecture: {n_layer} layers, {n_head} heads, {n_embd} embedding dim")
    
    @classmethod
    def from_config(cls, config: ModelConfig) -> 'GPTModel':
        """
        Create GPT model from configuration.
        
        Args:
            config: Model configuration
            
        Returns:
            GPTModel: Initialized model
        """
        return cls(
            vocab_size=config.vocab_size,
            n_layer=config.num_layers,
            n_head=config.num_heads,
            n_embd=config.embedding_dim,
            block_size=config.max_seq_length,
            dropout=config.dropout
        )
    
    def _validate_config(self, vocab_size: int, n_layer: int, n_head: int, 
                        n_embd: int, block_size: int, dropout: float) -> None:
        """Validate model configuration parameters."""
        if n_embd % n_head != 0:
            raise ModelError(f"n_embd ({n_embd}) must be divisible by n_head ({n_head})")
        if vocab_size <= 0:
            raise ModelError("vocab_size must be positive")
        if n_layer <= 0:
            raise ModelError("n_layer must be positive")
        if n_head <= 0:
            raise ModelError("n_head must be positive")
        if n_embd <= 0:
            raise ModelError("n_embd must be positive")
        if block_size <= 0:
            raise ModelError("block_size must be positive")
        if not 0 <= dropout <= 1:
            raise ModelError("dropout must be between 0 and 1")
    
    def _init_weights(self, module):
        """Initialize model weights using GPT-2 style initialization."""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)
    
    def forward(self, 
                input_ids: torch.Tensor, 
                targets: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Forward pass through the model.
        
        Args:
            input_ids: Input token IDs of shape (batch_size, sequence_length)
            targets: Target token IDs for loss computation (optional)
            
        Returns:
            Tuple of (logits, loss). Loss is None if targets not provided.
            
        Raises:
            ModelError: If sequence length exceeds block_size
        """
        B, T = input_ids.size()
        
        # Check sequence length
        if T > self.block_size:
            raise ModelError(f"Sequence length {T} exceeds block_size {self.block_size}")
        
        # Create position indices
        pos = torch.arange(0, T, dtype=torch.long, device=input_ids.device).unsqueeze(0)  # (1, T)
        
        # Token and position embeddings
        tok_emb = self.token_embedding(input_ids)  # (B, T, n_embd)
        pos_emb = self.position_embedding(pos)     # (1, T, n_embd)
        
        # Combine embeddings
        x = self.dropout_emb(tok_emb + pos_emb)
        
        # Pass through transformer blocks
        for block in self.blocks:
            x = block(x)
        
        # Final layer norm
        x = self.ln_f(x)
        
        # Language modeling head
        logits = self.lm_head(x)  # (B, T, vocab_size)
        
        # Compute loss if targets provided
        loss = None
        if targets is not None:
            # Flatten for cross-entropy
            logits_flat = logits.view(-1, logits.size(-1))
            targets_flat = targets.view(-1)
            loss = F.cross_entropy(logits_flat, targets_flat, ignore_index=-1)
        
        return logits, loss
    
    def generate(self, 
                 input_ids: torch.Tensor, 
                 max_new_tokens: int = 100, 
                 temperature: float = 1.0,
                 top_k: Optional[int] = None,
                 top_p: Optional[float] = None) -> torch.Tensor:
        """
        Generate new tokens using the model.
        
        Args:
            input_ids: Starting token sequence
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_k: If set, only sample from top k tokens
            top_p: If set, use nucleus sampling with probability p
            
        Returns:
            Generated token sequence
        """
        self.eval()
        
        with torch.no_grad():
            for _ in range(max_new_tokens):
                # Crop sequence if too long
                input_crop = input_ids if input_ids.size(1) <= self.block_size else input_ids[:, -self.block_size:]
                
                # Forward pass
                logits, _ = self(input_crop)
                
                # Get logits for last token
                logits = logits[:, -1, :] / temperature
                
                # Apply top-k filtering
                if top_k is not None:
                    v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                    logits[logits < v[:, [-1]]] = -float('Inf')
                
                # Apply top-p (nucleus) filtering
                if top_p is not None:
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                    
                    # Remove tokens with cumulative probability above the threshold
                    sorted_indices_to_remove = cumulative_probs > top_p
                    # Shift the indices to the right to keep also the first token above the threshold
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    
                    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                    logits[indices_to_remove] = -float('Inf')
                
                # Sample next token
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # Append to sequence
                input_ids = torch.cat([input_ids, next_token], dim=1)
        
        return input_ids
    
    def get_num_params(self) -> int:
        """Get number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def get_metadata(self) -> GPTModelMetadata:
        """Get model metadata."""
        return GPTModelMetadata(
            vocab_size=self.vocab_size,
            n_layer=self.n_layer,
            n_head=self.n_head,
            n_embd=self.n_embd,
            block_size=self.block_size,
            dropout=self.dropout,
            num_parameters=self.get_num_params()
        )
    
    def estimate_memory_usage(self, batch_size: int, sequence_length: int) -> Dict[str, float]:
        """
        Estimate memory usage for given batch size and sequence length.
        
        Args:
            batch_size: Batch size
            sequence_length: Sequence length
            
        Returns:
            Dict with memory usage estimates in MB
        """
        # Parameter memory (4 bytes per float32)
        param_memory = self.get_num_params() * 4 / (1024 * 1024)
        
        # Activation memory (rough estimate)
        activation_memory = (
            batch_size * sequence_length * self.n_embd * self.n_layer * 8  # rough estimate
        ) / (1024 * 1024)
        
        return {
            'parameters_mb': param_memory,
            'activations_mb': activation_memory,
            'total_mb': param_memory + activation_memory
        }
    
    def validate_compatibility(self, tokenizer_vocab_size: int) -> bool:
        """
        Validate model compatibility with tokenizer.
        
        Args:
            tokenizer_vocab_size: Vocabulary size of tokenizer
            
        Returns:
            bool: True if compatible
            
        Raises:
            ModelError: If incompatible
        """
        if self.vocab_size != tokenizer_vocab_size:
            raise ModelError(
                f"Model vocab_size ({self.vocab_size}) does not match "
                f"tokenizer vocab_size ({tokenizer_vocab_size})"
            )
        return True
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get model configuration as dictionary."""
        return {
            'vocab_size': self.vocab_size,
            'num_layers': self.n_layer,
            'num_heads': self.n_head,
            'embedding_dim': self.n_embd,
            'max_seq_length': self.block_size,
            'dropout': self.dropout,
            'model_type': 'gpt'
        }