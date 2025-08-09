"""
Data processing module for LLMBuilder.

This module provides comprehensive data loading, cleaning, and dataset
management utilities for LLM training pipelines.
"""

from .loader import DataLoader, DocumentMetadata
from .cleaner import TextCleaner, CleaningStats
from .dataset import (
    TextDataset, 
    MultiFileDataset, 
    create_dataloader, 
    split_dataset,
    save_dataset,
    load_dataset,
    get_dataset_info
)

__all__ = [
    # Data loading
    'DataLoader',
    'DocumentMetadata',
    
    # Text cleaning
    'TextCleaner',
    'CleaningStats',
    
    # Dataset management
    'TextDataset',
    'MultiFileDataset',
    'create_dataloader',
    'split_dataset',
    'save_dataset',
    'load_dataset',
    'get_dataset_info',
]