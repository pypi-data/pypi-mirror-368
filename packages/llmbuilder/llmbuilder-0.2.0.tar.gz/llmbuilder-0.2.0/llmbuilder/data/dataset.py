"""
Dataset utilities for LLMBuilder.

This module provides dataset classes and utilities for handling tokenized
text data for LLM training.
"""

import torch
import numpy as np
from pathlib import Path
from typing import Union, Optional, List, Tuple, Iterator
from torch.utils.data import Dataset, DataLoader, random_split

from ..utils import DataError, get_logger

logger = get_logger("data.dataset")


class TextDataset(Dataset):
    """
    Dataset for tokenized text data with sliding window approach.
    
    Supports both single-file and multi-file datasets with configurable
    block size and stride for creating training samples.
    """
    
    def __init__(self, 
                 data_path: Union[str, Path, List[Union[str, Path]]],
                 block_size: int = 1024,
                 stride: Optional[int] = None,
                 cache_in_memory: bool = True):
        """
        Initialize text dataset.
        
        Args:
            data_path: Path to tokenized data file(s) (.pt or .npy)
            block_size: Context window size
            stride: Stride for sliding window. If None, uses block_size (no overlap)
            cache_in_memory: Whether to cache data in memory
        """
        self.block_size = block_size
        self.stride = stride or block_size
        self.cache_in_memory = cache_in_memory
        
        # Handle single file or multiple files
        if isinstance(data_path, (str, Path)):
            self.data_paths = [Path(data_path)]
        else:
            self.data_paths = [Path(p) for p in data_path]
        
        # Load and validate data
        self.tokens = self._load_tokens()
        self.num_samples = self._calculate_num_samples()
        
        logger.info(f"Dataset initialized: {len(self.tokens):,} tokens, {self.num_samples:,} samples")
        logger.info(f"Block size: {block_size}, Stride: {self.stride}")
    
    def _load_tokens(self) -> torch.Tensor:
        """Load tokenized data from file(s)."""
        all_tokens = []
        
        for data_path in self.data_paths:
            if not data_path.exists():
                raise DataError(f"Data file not found: {data_path}")
            
            try:
                if data_path.suffix == '.pt':
                    tokens = torch.load(data_path, map_location='cpu')
                elif data_path.suffix == '.npy':
                    tokens = torch.from_numpy(np.load(data_path))
                else:
                    raise DataError(f"Unsupported file format: {data_path.suffix}")
                
                # Ensure tokens are long integers
                if tokens.dtype != torch.long:
                    tokens = tokens.long()
                
                all_tokens.append(tokens)
                logger.info(f"Loaded {len(tokens):,} tokens from {data_path}")
                
            except Exception as e:
                raise DataError(f"Error loading {data_path}: {str(e)}") from e
        
        # Concatenate all tokens
        if len(all_tokens) == 1:
            return all_tokens[0]
        else:
            return torch.cat(all_tokens, dim=0)
    
    def _calculate_num_samples(self) -> int:
        """Calculate number of samples based on tokens, block size, and stride."""
        if len(self.tokens) < self.block_size:
            logger.warning(f"Token sequence ({len(self.tokens)}) shorter than block size ({self.block_size})")
            return 0
        
        return max(0, (len(self.tokens) - self.block_size) // self.stride + 1)
    
    def __len__(self) -> int:
        """Return number of samples in dataset."""
        return self.num_samples
    
    def __getitem__(self, idx: int) -> dict:
        """
        Get a training sample.
        
        Args:
            idx: Sample index
            
        Returns:
            dict: Dictionary with 'input_ids' and 'labels' tensors
        """
        if idx >= self.num_samples:
            raise IndexError(f"Index {idx} out of range for dataset of size {self.num_samples}")
        
        # Calculate start position
        start_idx = idx * self.stride
        end_idx = start_idx + self.block_size
        
        # Extract sequence
        sequence = self.tokens[start_idx:end_idx + 1]  # +1 for target
        
        # Split into input and target
        input_ids = sequence[:-1]  # All but last token
        labels = sequence[1:]      # All but first token (shifted by 1)
        
        return {
            'input_ids': input_ids,
            'labels': labels
        }
    
    def get_vocab_size(self) -> int:
        """Get vocabulary size from the data."""
        return int(self.tokens.max().item()) + 1
    
    def get_sample_text(self, idx: int, tokenizer=None) -> str:
        """
        Get sample text for inspection (requires tokenizer).
        
        Args:
            idx: Sample index
            tokenizer: Tokenizer to decode tokens
            
        Returns:
            str: Decoded text sample
        """
        if tokenizer is None:
            return f"Sample {idx}: tokens {self.__getitem__(idx)['input_ids'][:10].tolist()}..."
        
        sample = self.__getitem__(idx)
        return tokenizer.decode(sample['input_ids'].tolist())


class MultiFileDataset(Dataset):
    """
    Dataset that handles multiple tokenized files efficiently.
    
    Useful for very large datasets that don't fit in memory or when
    you want to process files separately.
    """
    
    def __init__(self,
                 data_dir: Union[str, Path],
                 block_size: int = 1024,
                 stride: Optional[int] = None,
                 file_pattern: str = "*.pt"):
        """
        Initialize multi-file dataset.
        
        Args:
            data_dir: Directory containing tokenized files
            block_size: Context window size
            stride: Stride for sliding window
            file_pattern: Pattern to match files
        """
        self.data_dir = Path(data_dir)
        self.block_size = block_size
        self.stride = stride or block_size
        
        # Find all matching files
        self.data_files = list(self.data_dir.glob(file_pattern))
        if not self.data_files:
            raise DataError(f"No files found matching {file_pattern} in {data_dir}")
        
        self.data_files.sort()  # Ensure consistent ordering
        
        # Calculate file offsets and total samples
        self.file_offsets = []
        self.file_samples = []
        total_samples = 0
        
        for file_path in self.data_files:
            # Load file to get size
            tokens = self._load_file(file_path)
            num_samples = max(0, (len(tokens) - block_size) // self.stride + 1)
            
            self.file_offsets.append(total_samples)
            self.file_samples.append(num_samples)
            total_samples += num_samples
            
            logger.debug(f"File {file_path.name}: {len(tokens)} tokens, {num_samples} samples")
        
        self.total_samples = total_samples
        logger.info(f"Multi-file dataset: {len(self.data_files)} files, {total_samples:,} total samples")
    
    def _load_file(self, file_path: Path) -> torch.Tensor:
        """Load tokens from a single file."""
        if file_path.suffix == '.pt':
            return torch.load(file_path, map_location='cpu')
        elif file_path.suffix == '.npy':
            return torch.from_numpy(np.load(file_path))
        else:
            raise DataError(f"Unsupported file format: {file_path.suffix}")
    
    def __len__(self) -> int:
        """Return total number of samples."""
        return self.total_samples
    
    def __getitem__(self, idx: int) -> dict:
        """Get a training sample."""
        if idx >= self.total_samples:
            raise IndexError(f"Index {idx} out of range")
        
        # Find which file contains this sample
        file_idx = 0
        while file_idx < len(self.file_offsets) - 1:
            if idx < self.file_offsets[file_idx + 1]:
                break
            file_idx += 1
        
        # Calculate local index within the file
        local_idx = idx - self.file_offsets[file_idx]
        
        # Load the file and extract sample
        tokens = self._load_file(self.data_files[file_idx])
        start_idx = local_idx * self.stride
        end_idx = start_idx + self.block_size
        
        sequence = tokens[start_idx:end_idx + 1]
        
        return {
            'input_ids': sequence[:-1],
            'labels': sequence[1:]
        }
    
    def get_vocab_size(self) -> int:
        """Get vocabulary size by checking all files."""
        max_token = 0
        for file_path in self.data_files:
            tokens = self._load_file(file_path)
            max_token = max(max_token, int(tokens.max().item()))
        return max_token + 1


def create_dataloader(dataset: Dataset,
                     batch_size: int = 32,
                     shuffle: bool = True,
                     num_workers: int = 0,
                     pin_memory: bool = True,
                     drop_last: bool = True) -> DataLoader:
    """
    Create a DataLoader for training.
    
    Args:
        dataset: Dataset to load from
        batch_size: Batch size
        shuffle: Whether to shuffle data
        num_workers: Number of worker processes
        pin_memory: Whether to pin memory
        drop_last: Whether to drop last incomplete batch
        
    Returns:
        DataLoader: Configured data loader
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=drop_last,
        persistent_workers=num_workers > 0
    )


def split_dataset(dataset: Dataset, 
                 train_ratio: float = 0.8,
                 val_ratio: float = 0.1,
                 test_ratio: float = 0.1,
                 random_seed: Optional[int] = 42) -> Tuple[Dataset, ...]:
    """
    Split dataset into train/validation/test sets.
    
    Args:
        dataset: Dataset to split
        train_ratio: Ratio for training set
        val_ratio: Ratio for validation set
        test_ratio: Ratio for test set
        random_seed: Random seed for reproducible splits
        
    Returns:
        Tuple[Dataset, ...]: Split datasets (train, val, test) or (train, val) if test_ratio=0
    """
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
        raise ValueError("Ratios must sum to 1.0")
    
    total_size = len(dataset)
    train_size = int(train_ratio * total_size)
    val_size = int(val_ratio * total_size)
    test_size = total_size - train_size - val_size
    
    # Set random seed for reproducible splits
    if random_seed is not None:
        generator = torch.Generator().manual_seed(random_seed)
    else:
        generator = None
    
    if test_ratio > 0:
        train_dataset, val_dataset, test_dataset = random_split(
            dataset, [train_size, val_size, test_size], generator=generator
        )
        logger.info(f"Dataset split: {train_size} train, {val_size} val, {test_size} test")
        return train_dataset, val_dataset, test_dataset
    else:
        train_dataset, val_dataset = random_split(
            dataset, [train_size, val_size], generator=generator
        )
        logger.info(f"Dataset split: {train_size} train, {val_size} val")
        return train_dataset, val_dataset


def save_dataset(dataset: Dataset, 
                output_path: Union[str, Path],
                format: str = "pt") -> None:
    """
    Save dataset to file.
    
    Args:
        dataset: Dataset to save
        output_path: Output file path
        format: Output format ("pt" or "npy")
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract all tokens from dataset
    all_tokens = []
    for i in range(len(dataset)):
        sample = dataset[i]
        all_tokens.append(sample['input_ids'])
    
    # Concatenate tokens
    tokens = torch.cat(all_tokens, dim=0)
    
    if format == "pt":
        torch.save(tokens, output_path)
    elif format == "npy":
        np.save(output_path, tokens.numpy())
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    logger.info(f"Dataset saved to {output_path}: {len(tokens):,} tokens")


def load_dataset(data_path: Union[str, Path],
                block_size: int = 1024,
                stride: Optional[int] = None) -> TextDataset:
    """
    Convenience function to load a dataset.
    
    Args:
        data_path: Path to data file or directory
        block_size: Context window size
        stride: Stride for sliding window
        
    Returns:
        TextDataset: Loaded dataset
    """
    data_path = Path(data_path)
    
    if data_path.is_file():
        return TextDataset(data_path, block_size, stride)
    elif data_path.is_dir():
        return MultiFileDataset(data_path, block_size, stride)
    else:
        raise DataError(f"Data path not found: {data_path}")


def get_dataset_info(dataset: Dataset) -> dict:
    """
    Get information about a dataset.
    
    Args:
        dataset: Dataset to analyze
        
    Returns:
        dict: Dataset information
    """
    info = {
        'num_samples': len(dataset),
        'dataset_type': type(dataset).__name__
    }
    
    if hasattr(dataset, 'block_size'):
        info['block_size'] = dataset.block_size
    
    if hasattr(dataset, 'stride'):
        info['stride'] = dataset.stride
    
    if hasattr(dataset, 'get_vocab_size'):
        try:
            info['vocab_size'] = dataset.get_vocab_size()
        except:
            pass
    
    # Sample a few items to get tensor shapes
    if len(dataset) > 0:
        sample = dataset[0]
        info['sample_keys'] = list(sample.keys())
        for key, value in sample.items():
            if isinstance(value, torch.Tensor):
                info[f'{key}_shape'] = list(value.shape)
                info[f'{key}_dtype'] = str(value.dtype)
    
    return info