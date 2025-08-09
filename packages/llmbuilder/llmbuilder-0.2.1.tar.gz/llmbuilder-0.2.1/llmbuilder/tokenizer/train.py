"""
Tokenizer training utilities for LLMBuilder.

This module provides the TokenizerTrainer class for training SentencePiece
tokenizers with comprehensive configuration and validation.
"""

import os
import json
import torch
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict

from ..utils import TokenizerError, get_logger
from ..config import TokenizerConfig

logger = get_logger("tokenizer.train")

# Optional import for SentencePiece
try:
    import sentencepiece as spm
    HAS_SENTENCEPIECE = True
except ImportError:
    HAS_SENTENCEPIECE = False


@dataclass
class TokenizerMetadata:
    """Metadata for a trained tokenizer."""
    vocab_size: int
    model_type: str
    character_coverage: float
    training_data_size: int
    training_time: float
    version: str = "1.0"
    
    def save(self, path: Union[str, Path]) -> None:
        """Save metadata to JSON file."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> 'TokenizerMetadata':
        """Load metadata from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)


class TokenizerTrainer:
    """
    Comprehensive tokenizer trainer using SentencePiece.
    
    Supports various tokenizer types (BPE, Unigram, Word, Char) with
    extensive configuration options and validation.
    """
    
    def __init__(self, config: Optional[TokenizerConfig] = None):
        """
        Initialize tokenizer trainer.
        
        Args:
            config: Tokenizer configuration. If None, uses defaults.
        """
        self.config = config or TokenizerConfig()
        
        if not HAS_SENTENCEPIECE:
            raise TokenizerError(
                "SentencePiece not installed. Install with: pip install sentencepiece"
            )
        
        logger.info(f"TokenizerTrainer initialized with {self.config.model_type} model")
        logger.info(f"Vocab size: {self.config.vocab_size}")
    
    def prepare_training_data(self, 
                            input_paths: Union[str, Path, List[Union[str, Path]]],
                            output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Prepare training data for tokenizer training.
        
        Args:
            input_paths: Path(s) to input text files
            output_path: Output path for combined training data
            
        Returns:
            Path: Path to prepared training data file
        """
        # Handle single path or multiple paths
        if isinstance(input_paths, (str, Path)):
            input_paths = [Path(input_paths)]
        else:
            input_paths = [Path(p) for p in input_paths]
        
        # Validate input files
        for path in input_paths:
            if not path.exists():
                raise TokenizerError(f"Input file not found: {path}")
        
        # Set default output path
        if output_path is None:
            output_path = Path("tokenizer_training_data.txt")
        else:
            output_path = Path(output_path)
        
        logger.info(f"Preparing training data from {len(input_paths)} files")
        
        # Combine all input files
        total_chars = 0
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for input_path in input_paths:
                try:
                    with open(input_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        if content.strip():  # Only write non-empty content
                            outfile.write(content)
                            if not content.endswith('\n'):
                                outfile.write('\n')
                            total_chars += len(content)
                    
                    logger.debug(f"Added {input_path.name}: {len(content):,} chars")
                    
                except Exception as e:
                    logger.error(f"Error reading {input_path}: {e}")
                    continue
        
        if total_chars == 0:
            raise TokenizerError("No valid training data found")
        
        logger.info(f"Training data prepared: {output_path} ({total_chars:,} characters)")
        return output_path
    
    def train(self, 
              input_file: Union[str, Path],
              output_dir: Union[str, Path],
              model_prefix: str = "tokenizer") -> Dict[str, Any]:
        """
        Train a SentencePiece tokenizer.
        
        Args:
            input_file: Path to training data file
            output_dir: Output directory for tokenizer files
            model_prefix: Prefix for output files
            
        Returns:
            Dict[str, Any]: Training results and metadata
        """
        import time
        
        input_file = Path(input_file)
        output_dir = Path(output_dir)
        
        # Validate input
        if not input_file.exists():
            raise TokenizerError(f"Training data file not found: {input_file}")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build training arguments
        model_path = output_dir / model_prefix
        train_args = self._build_training_args(input_file, model_path)
        
        logger.info("Starting tokenizer training...")
        logger.info(f"Input: {input_file} ({input_file.stat().st_size:,} bytes)")
        logger.info(f"Output: {output_dir}")
        logger.info(f"Model type: {self.config.model_type}")
        logger.info(f"Vocab size: {self.config.vocab_size}")
        
        # Train tokenizer
        start_time = time.time()
        try:
            spm.SentencePieceTrainer.train(' '.join(train_args))
            training_time = time.time() - start_time
            
        except Exception as e:
            raise TokenizerError(f"Tokenizer training failed: {str(e)}") from e
        
        # Verify output files
        model_file = Path(f"{model_path}.model")
        vocab_file = Path(f"{model_path}.vocab")
        
        if not model_file.exists() or not vocab_file.exists():
            raise TokenizerError("Training completed but output files not found")
        
        logger.info(f"Training completed in {training_time:.1f}s")
        logger.info(f"Model: {model_file} ({model_file.stat().st_size:,} bytes)")
        logger.info(f"Vocab: {vocab_file} ({vocab_file.stat().st_size:,} bytes)")
        
        # Test the tokenizer
        test_results = self._test_tokenizer(model_file)
        
        # Create and save metadata
        metadata = TokenizerMetadata(
            vocab_size=self.config.vocab_size,
            model_type=self.config.model_type,
            character_coverage=self.config.character_coverage,
            training_data_size=input_file.stat().st_size,
            training_time=training_time
        )
        
        metadata_file = output_dir / f"{model_prefix}_metadata.json"
        metadata.save(metadata_file)
        
        return {
            'model_file': str(model_file),
            'vocab_file': str(vocab_file),
            'metadata_file': str(metadata_file),
            'training_time': training_time,
            'metadata': metadata,
            'test_results': test_results
        }
    
    def _build_training_args(self, input_file: Path, model_path: Path) -> List[str]:
        """Build SentencePiece training arguments."""
        args = [
            f'--input={input_file}',
            f'--model_prefix={model_path}',
            f'--vocab_size={self.config.vocab_size}',
            f'--model_type={self.config.model_type}',
            f'--character_coverage={self.config.character_coverage}',
            f'--max_sentence_length={self.config.max_sentence_length}',
            f'--shuffle_input_sentence={str(self.config.shuffle_input_sentence).lower()}',
            f'--normalization_rule_name={self.config.normalization_rule_name}',
            f'--remove_extra_whitespaces={str(self.config.remove_extra_whitespaces).lower()}',
            f'--add_dummy_prefix={str(self.config.add_dummy_prefix).lower()}',
            f'--num_threads={os.cpu_count() or 4}',
            '--pad_id=0',
            '--unk_id=1', 
            '--bos_id=2',
            '--eos_id=3',
        ]
        
        return args
    
    def _test_tokenizer(self, model_file: Path) -> Dict[str, Any]:
        """Test the trained tokenizer with sample texts."""
        logger.info("Testing trained tokenizer...")
        
        try:
            # Load tokenizer
            sp = spm.SentencePieceProcessor()
            sp.load(str(model_file))
            
            # Test sentences
            test_sentences = [
                "Hello, world!",
                "This is a test sentence for the tokenizer.",
                "The quick brown fox jumps over the lazy dog.",
                "Machine learning and artificial intelligence are fascinating.",
                "Natural language processing enables computers to understand human language."
            ]
            
            results = []
            total_tokens = 0
            
            for sentence in test_sentences:
                # Encode
                tokens = sp.encode(sentence, out_type=int)
                token_pieces = sp.encode(sentence, out_type=str)
                
                # Decode
                decoded = sp.decode(tokens)
                
                result = {
                    'original': sentence,
                    'tokens': tokens,
                    'token_pieces': token_pieces,
                    'decoded': decoded,
                    'num_tokens': len(tokens),
                    'compression_ratio': len(tokens) / len(sentence.split())
                }
                
                results.append(result)
                total_tokens += len(tokens)
                
                logger.debug(f"'{sentence}' -> {len(tokens)} tokens")
            
            # Calculate statistics
            avg_tokens = total_tokens / len(test_sentences)
            avg_compression = sum(r['compression_ratio'] for r in results) / len(results)
            
            test_summary = {
                'test_results': results,
                'avg_tokens_per_sentence': avg_tokens,
                'avg_compression_ratio': avg_compression,
                'actual_vocab_size': sp.get_piece_size(),
                'special_tokens': {
                    'pad_id': sp.pad_id(),
                    'unk_id': sp.unk_id(),
                    'bos_id': sp.bos_id(),
                    'eos_id': sp.eos_id()
                }
            }
            
            logger.info(f"Tokenizer test completed")
            logger.info(f"Average tokens per sentence: {avg_tokens:.1f}")
            logger.info(f"Average compression ratio: {avg_compression:.2f}")
            logger.info(f"Actual vocab size: {sp.get_piece_size()}")
            
            return test_summary
            
        except Exception as e:
            logger.error(f"Tokenizer test failed: {e}")
            return {'test_error': str(e)}
    
    def create_tokenized_dataset(self,
                                input_file: Union[str, Path],
                                tokenizer_model: Union[str, Path],
                                output_file: Union[str, Path],
                                max_length: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a tokenized dataset for training.
        
        Args:
            input_file: Path to input text file
            tokenizer_model: Path to trained tokenizer model
            output_file: Path to output tokenized dataset
            max_length: Maximum sequence length (for truncation)
            
        Returns:
            Dict[str, Any]: Dataset creation results
        """
        input_file = Path(input_file)
        tokenizer_model = Path(tokenizer_model)
        output_file = Path(output_file)
        
        # Validate inputs
        if not input_file.exists():
            raise TokenizerError(f"Input file not found: {input_file}")
        if not tokenizer_model.exists():
            raise TokenizerError(f"Tokenizer model not found: {tokenizer_model}")
        
        logger.info("Creating tokenized dataset...")
        logger.info(f"Input: {input_file}")
        logger.info(f"Tokenizer: {tokenizer_model}")
        logger.info(f"Output: {output_file}")
        
        try:
            # Load tokenizer
            sp = spm.SentencePieceProcessor()
            sp.load(str(tokenizer_model))
            
            # Read input text
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Input text: {len(text):,} characters")
            
            # Tokenize text
            tokens = sp.encode(text, out_type=int)
            
            # Apply max length if specified
            if max_length and len(tokens) > max_length:
                logger.warning(f"Truncating tokens from {len(tokens):,} to {max_length:,}")
                tokens = tokens[:max_length]
            
            logger.info(f"Tokenized: {len(tokens):,} tokens")
            
            # Convert to tensor and save
            token_tensor = torch.tensor(tokens, dtype=torch.long)
            
            # Create output directory
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save dataset
            torch.save(token_tensor, output_file)
            
            logger.info(f"Tokenized dataset saved: {output_file}")
            
            return {
                'input_file': str(input_file),
                'output_file': str(output_file),
                'tokenizer_model': str(tokenizer_model),
                'original_chars': len(text),
                'num_tokens': len(tokens),
                'compression_ratio': len(tokens) / len(text.split()),
                'vocab_size': sp.get_piece_size(),
                'file_size_mb': output_file.stat().st_size / (1024 * 1024)
            }
            
        except Exception as e:
            raise TokenizerError(f"Dataset creation failed: {str(e)}") from e
    
    def validate_tokenizer(self, model_file: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a trained tokenizer.
        
        Args:
            model_file: Path to tokenizer model file
            
        Returns:
            Dict[str, Any]: Validation results
        """
        model_file = Path(model_file)
        
        if not model_file.exists():
            raise TokenizerError(f"Model file not found: {model_file}")
        
        try:
            # Load tokenizer
            sp = spm.SentencePieceProcessor()
            sp.load(str(model_file))
            
            # Basic validation
            vocab_size = sp.get_piece_size()
            
            # Test special tokens
            special_tokens = {
                'pad_id': sp.pad_id(),
                'unk_id': sp.unk_id(),
                'bos_id': sp.bos_id(),
                'eos_id': sp.eos_id()
            }
            
            # Test encoding/decoding
            test_text = "Hello world! This is a test."
            tokens = sp.encode(test_text)
            decoded = sp.decode(tokens)
            
            # Check for round-trip consistency
            roundtrip_ok = test_text.strip() == decoded.strip()
            
            validation_results = {
                'model_file': str(model_file),
                'vocab_size': vocab_size,
                'special_tokens': special_tokens,
                'roundtrip_test': {
                    'original': test_text,
                    'decoded': decoded,
                    'success': roundtrip_ok
                },
                'valid': roundtrip_ok and vocab_size > 0
            }
            
            logger.info(f"Tokenizer validation: {'PASSED' if validation_results['valid'] else 'FAILED'}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Tokenizer validation failed: {e}")
            return {
                'model_file': str(model_file),
                'valid': False,
                'error': str(e)
            }