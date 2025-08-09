"""
Tokenizer utilities for LLMBuilder.

This module provides utilities for managing and working with tokenizers,
including loading, saving, and wrapping different tokenizer types.
"""

import json
from pathlib import Path
from typing import Union, Optional, List, Dict, Any

from ..utils import TokenizerError, get_logger

logger = get_logger("tokenizer.utils")

try:
    from tokenizers import Tokenizer
    HAS_TOKENIZERS = True
except ImportError:
    HAS_TOKENIZERS = False
    # Create a dummy Tokenizer class for type hints
    class Tokenizer:
        pass

try:
    from transformers import AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class TokenizerManager:
    """
    Manager for tokenizer operations including loading, saving, and validation.
    """
    
    def __init__(self):
        """Initialize the tokenizer manager."""
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check for required dependencies."""
        if not HAS_TOKENIZERS:
            logger.warning("tokenizers library not found. Install with: pip install tokenizers")
        if not HAS_TRANSFORMERS:
            logger.warning("transformers library not found. Install with: pip install transformers")
    
    def load_tokenizer(self, tokenizer_path: Union[str, Path]) -> Union[Tokenizer, Any]:
        """
        Load a tokenizer from file.
        
        Args:
            tokenizer_path: Path to tokenizer file or directory
            
        Returns:
            Loaded tokenizer object
            
        Raises:
            TokenizerError: If loading fails
        """
        tokenizer_path = Path(tokenizer_path)
        
        if not tokenizer_path.exists():
            raise TokenizerError(f"Tokenizer not found: {tokenizer_path}")
        
        try:
            # Try loading as HuggingFace tokenizer first
            if HAS_TRANSFORMERS and tokenizer_path.is_dir():
                return AutoTokenizer.from_pretrained(str(tokenizer_path))
            
            # Try loading as tokenizers library tokenizer
            if HAS_TOKENIZERS and tokenizer_path.is_file():
                return Tokenizer.from_file(str(tokenizer_path))
            
            raise TokenizerError(f"Could not determine tokenizer format for: {tokenizer_path}")
            
        except Exception as e:
            raise TokenizerError(f"Failed to load tokenizer: {str(e)}", tokenizer_path=str(tokenizer_path)) from e
    
    def save_tokenizer(self, tokenizer: Any, output_path: Union[str, Path], format_type: str = "auto"):
        """
        Save a tokenizer to file.
        
        Args:
            tokenizer: Tokenizer object to save
            output_path: Output path
            format_type: Output format ("auto", "json", "hf")
            
        Raises:
            TokenizerError: If saving fails
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if format_type == "auto":
                # Auto-detect format based on tokenizer type
                if hasattr(tokenizer, 'save_pretrained'):
                    format_type = "hf"
                elif hasattr(tokenizer, 'save'):
                    format_type = "json"
                else:
                    raise TokenizerError("Could not auto-detect tokenizer format")
            
            if format_type == "hf":
                # Save as HuggingFace format
                tokenizer.save_pretrained(str(output_path))
            elif format_type == "json":
                # Save as JSON format
                tokenizer.save(str(output_path))
            else:
                raise TokenizerError(f"Unsupported format: {format_type}")
            
            logger.info(f"Tokenizer saved to {output_path}")
            
        except Exception as e:
            raise TokenizerError(f"Failed to save tokenizer: {str(e)}", tokenizer_path=str(output_path)) from e
    
    def validate_tokenizer(self, tokenizer: Any) -> Dict[str, Any]:
        """
        Validate a tokenizer and return information about it.
        
        Args:
            tokenizer: Tokenizer to validate
            
        Returns:
            Dict with tokenizer information
        """
        info = {
            "type": type(tokenizer).__name__,
            "valid": True,
            "errors": []
        }
        
        try:
            # Test basic functionality
            test_text = "Hello, world! This is a test."
            
            # Test encoding
            if hasattr(tokenizer, 'encode'):
                tokens = tokenizer.encode(test_text)
                info["vocab_size"] = getattr(tokenizer, 'vocab_size', len(tokens) if isinstance(tokens, list) else len(tokens.ids))
                info["test_tokens"] = tokens[:10] if isinstance(tokens, list) else tokens.ids[:10]
            elif hasattr(tokenizer, '__call__'):
                result = tokenizer(test_text)
                info["vocab_size"] = getattr(tokenizer, 'vocab_size', None)
                info["test_tokens"] = result.get('input_ids', [])[:10]
            else:
                info["errors"].append("No encode method found")
                info["valid"] = False
            
            # Test decoding if we have test tokens
            if hasattr(tokenizer, 'decode') and 'test_tokens' in info and info["test_tokens"]:
                try:
                    decoded = tokenizer.decode(info["test_tokens"])
                    info["decode_test"] = decoded
                except Exception as e:
                    info["errors"].append(f"Decode test failed: {str(e)}")
            
            # Get special tokens if available
            special_tokens = {}
            for token_name in ['pad_token', 'unk_token', 'bos_token', 'eos_token']:
                if hasattr(tokenizer, token_name):
                    token = getattr(tokenizer, token_name)
                    if token is not None:
                        special_tokens[token_name] = str(token)
            
            if special_tokens:
                info["special_tokens"] = special_tokens
            
        except Exception as e:
            info["valid"] = False
            info["errors"].append(f"Validation error: {str(e)}")
        
        return info
    
    def get_tokenizer_info(self, tokenizer_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about a tokenizer file.
        
        Args:
            tokenizer_path: Path to tokenizer
            
        Returns:
            Dict with tokenizer file information
        """
        tokenizer_path = Path(tokenizer_path)
        
        info = {
            "path": str(tokenizer_path),
            "exists": tokenizer_path.exists(),
            "is_file": tokenizer_path.is_file(),
            "is_dir": tokenizer_path.is_dir(),
        }
        
        if tokenizer_path.exists():
            try:
                tokenizer = self.load_tokenizer(tokenizer_path)
                info.update(self.validate_tokenizer(tokenizer))
            except Exception as e:
                info["load_error"] = str(e)
        
        return info


class TokenizerWrapper:
    """
    Wrapper class to provide a unified interface for different tokenizer types.
    """
    
    def __init__(self, tokenizer: Any):
        """
        Initialize wrapper with a tokenizer.
        
        Args:
            tokenizer: Tokenizer object to wrap
        """
        self.tokenizer = tokenizer
        self._detect_interface()
    
    def _detect_interface(self):
        """Detect the tokenizer interface type."""
        if hasattr(self.tokenizer, 'encode') and hasattr(self.tokenizer, 'decode'):
            if hasattr(self.tokenizer, 'vocab_size'):
                self.interface_type = "transformers"
            else:
                self.interface_type = "tokenizers"
        elif hasattr(self.tokenizer, '__call__'):
            self.interface_type = "transformers_callable"
        else:
            self.interface_type = "unknown"
    
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Encode text to token IDs.
        
        Args:
            text: Text to encode
            add_special_tokens: Whether to add special tokens
            
        Returns:
            List of token IDs
        """
        if self.interface_type == "transformers":
            return self.tokenizer.encode(text, add_special_tokens=add_special_tokens)
        elif self.interface_type == "tokenizers":
            encoding = self.tokenizer.encode(text, add_special_tokens=add_special_tokens)
            return encoding.ids
        elif self.interface_type == "transformers_callable":
            result = self.tokenizer(text, add_special_tokens=add_special_tokens)
            return result['input_ids']
        else:
            raise TokenizerError(f"Unsupported tokenizer interface: {self.interface_type}")
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs to text.
        
        Args:
            token_ids: Token IDs to decode
            skip_special_tokens: Whether to skip special tokens
            
        Returns:
            Decoded text
        """
        if self.interface_type in ["transformers", "transformers_callable"]:
            return self.tokenizer.decode(token_ids, skip_special_tokens=skip_special_tokens)
        elif self.interface_type == "tokenizers":
            return self.tokenizer.decode(token_ids, skip_special_tokens=skip_special_tokens)
        else:
            raise TokenizerError(f"Unsupported tokenizer interface: {self.interface_type}")
    
    def batch_encode(self, texts: List[str], add_special_tokens: bool = True) -> List[List[int]]:
        """
        Encode multiple texts.
        
        Args:
            texts: List of texts to encode
            add_special_tokens: Whether to add special tokens
            
        Returns:
            List of token ID lists
        """
        return [self.encode(text, add_special_tokens) for text in texts]
    
    def batch_decode(self, token_ids_list: List[List[int]], skip_special_tokens: bool = True) -> List[str]:
        """
        Decode multiple token ID lists.
        
        Args:
            token_ids_list: List of token ID lists
            skip_special_tokens: Whether to skip special tokens
            
        Returns:
            List of decoded texts
        """
        return [self.decode(token_ids, skip_special_tokens) for token_ids in token_ids_list]
    
    @property
    def vocab_size(self) -> int:
        """Get vocabulary size."""
        if hasattr(self.tokenizer, 'vocab_size'):
            return self.tokenizer.vocab_size
        elif hasattr(self.tokenizer, 'get_vocab_size'):
            return self.tokenizer.get_vocab_size()
        else:
            raise TokenizerError("Cannot determine vocabulary size")
    
    @property
    def pad_token_id(self) -> Optional[int]:
        """Get pad token ID."""
        if hasattr(self.tokenizer, 'pad_token_id'):
            return self.tokenizer.pad_token_id
        return None
    
    @property
    def eos_token_id(self) -> Optional[int]:
        """Get end-of-sequence token ID."""
        if hasattr(self.tokenizer, 'eos_token_id'):
            return self.tokenizer.eos_token_id
        return None
    
    @property
    def bos_token_id(self) -> Optional[int]:
        """Get beginning-of-sequence token ID."""
        if hasattr(self.tokenizer, 'bos_token_id'):
            return self.tokenizer.bos_token_id
        return None
    
    @property
    def unk_token_id(self) -> Optional[int]:
        """Get unknown token ID."""
        if hasattr(self.tokenizer, 'unk_token_id'):
            return self.tokenizer.unk_token_id
        return None
    
    def get_special_tokens(self) -> Dict[str, int]:
        """Get all special token IDs."""
        special_tokens = {}
        
        for token_name in ['pad_token_id', 'eos_token_id', 'bos_token_id', 'unk_token_id']:
            token_id = getattr(self, token_name, None)
            if token_id is not None:
                special_tokens[token_name] = token_id
        
        return special_tokens
    
    def save(self, output_path: Union[str, Path], format_type: str = "auto"):
        """
        Save the wrapped tokenizer.
        
        Args:
            output_path: Output path
            format_type: Output format
        """
        manager = TokenizerManager()
        manager.save_tokenizer(self.tokenizer, output_path, format_type)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"TokenizerWrapper({type(self.tokenizer).__name__}, interface={self.interface_type})"