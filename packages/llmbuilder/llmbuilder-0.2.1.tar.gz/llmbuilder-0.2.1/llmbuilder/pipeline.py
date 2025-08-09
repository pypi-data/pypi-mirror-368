"""
Training Pipeline for LLMBuilder.

This module provides a high-level training pipeline that handles all the complex
logic of data loading, tokenization, model building, and training.
"""

import os
import logging
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Union, List, Tuple

from .utils import get_logger, DataError, ModelError
from .data import DataLoader, TextDataset, create_dataloader
from .tokenizer import Tokenizer, train_tokenizer
from .model import build_model
from .training import Trainer, TrainingConfig

logger = get_logger("pipeline")

class TrainingPipeline:
    """
    End-to-end training pipeline for LLMBuilder.
    
    Handles all the complex logic of data processing, tokenization,
    model building, and training with proper error handling and logging.
    """
    
    def __init__(self, 
                 data_path: Union[str, Path, List[Union[str, Path]]],
                 output_dir: Union[str, Path],
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the training pipeline.
        
        Args:
            data_path: Path to input data file(s) or directory
            output_dir: Directory to save outputs (tokenizer, checkpoints, etc.)
            config: Optional configuration dictionary
        """
        self.data_path = Path(data_path) if isinstance(data_path, str) else data_path
        self.output_dir = Path(output_dir)
        self.config = config or {}
        
        # Setup paths
        self.tokenizer_dir = self.output_dir / "tokenizer"
        self.checkpoints_dir = self.output_dir / "checkpoints"
        self.processed_data_file = self.output_dir / "processed_data.txt"
        self.tokenized_data_file = self.output_dir / "tokenized_data.pt"
        
        # Ensure output directories exist
        self.tokenizer_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.data_loader = DataLoader()
        self.tokenizer = None
        self.model = None
        self.trainer = None
    
    def run(self, clean: bool = False):
        """
        Run the complete training pipeline.
        
        Args:
            clean: If True, clean up previous outputs before starting
        """
        try:
            if clean:
                self._clean_previous_run()
            
            # Step 1: Process and load data
            logger.info("Processing input data...")
            self._process_data()
            
            # Step 2: Train or load tokenizer
            logger.info("Setting up tokenizer...")
            self._setup_tokenizer()
            
            # Step 3: Prepare dataset
            logger.info("Preparing dataset...")
            dataset = self._prepare_dataset()
            
            # Step 4: Build model
            logger.info("Building model...")
            self._build_model()
            
            # Step 5: Train model
            logger.info("Starting training...")
            self._train_model(dataset)
            
            logger.info("Training completed successfully!")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise
    
    def _clean_previous_run(self):
        """Clean up outputs from previous runs."""
        if self.processed_data_file.exists():
            self.processed_data_file.unlink()
        if self.tokenized_data_file.exists():
            self.tokenized_data_file.unlink()
        if self.tokenizer_dir.exists():
            shutil.rmtree(self.tokenizer_dir)
            self.tokenizer_dir.mkdir()
        if self.checkpoints_dir.exists():
            shutil.rmtree(self.checkpoints_dir)
            self.checkpoints_dir.mkdir()
    
    def _process_data(self):
        """Process input data into a clean text corpus."""
        if self.processed_data_file.exists():
            logger.info(f"Using existing processed data: {self.processed_data_file}")
            return
            
        if isinstance(self.data_path, (list, tuple)):
            # Handle multiple input files
            texts = []
            for path in self.data_path:
                path = Path(path)
                if path.is_file():
                    text = self.data_loader.load_file(path)
                    if text:
                        texts.append(text)
        else:
            # Handle single file or directory
            path = Path(self.data_path)
            if path.is_file():
                text = self.data_loader.load_file(path)
                texts = [text] if text else []
            else:
                # Load all supported files from directory
                texts = []
                for ext in DataLoader.SUPPORTED_EXTENSIONS:
                    for file_path in path.glob(f"*{ext}"):
                        text = self.data_loader.load_file(file_path)
                        if text:
                            texts.append(text)
        
        if not texts:
            raise DataError("No valid text data found in the input path(s)")
        
        # Combine and save processed text
        combined_text = "\n\n".join(texts)
        with open(self.processed_data_file, 'w', encoding='utf-8') as f:
            f.write(combined_text)
        
        logger.info(f"Processed data saved to {self.processed_data_file}")
    
    def _setup_tokenizer(self):
        """Train or load tokenizer."""
        tokenizer_files = list(self.tokenizer_dir.glob("*"))
        
        if tokenizer_files:
            # Load existing tokenizer
            self.tokenizer = Tokenizer.from_pretrained(self.tokenizer_dir)
            logger.info(f"Loaded tokenizer from {self.tokenizer_dir}")
        else:
            # Train new tokenizer
            vocab_size = self.config.get("vocab_size", 8000)
            logger.info(f"Training new tokenizer with vocab_size={vocab_size}...")
            
            self.tokenizer = train_tokenizer(
                self.processed_data_file,
                self.tokenizer_dir,
                vocab_size=vocab_size,
                special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
            )
            logger.info(f"Tokenizer trained and saved to {self.tokenizer_dir}")
    
    def _prepare_dataset(self):
        """Prepare dataset for training."""
        if not self.tokenizer:
            raise ValueError("Tokenizer not initialized")
        
        # Tokenize and save if not already done
        if not self.tokenized_data_file.exists():
            logger.info("Tokenizing data...")
            with open(self.processed_data_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            token_ids = self.tokenizer.encode(text)
            torch.save(token_ids, self.tokenized_data_file)
        else:
            logger.info("Loading pre-tokenized data...")
        
        # Create dataset
        block_size = self.config.get("block_size", 1024)
        return TextDataset(
            self.tokenized_data_file,
            block_size=block_size,
            stride=block_size // 2  # 50% overlap
        )
    
    def _build_model(self):
        """Build model from config."""
        model_config = self.config.get("model", {})
        self.model = build_model(
            vocab_size=len(self.tokenizer),
            **model_config
        )
        logger.info(f"Model built with {sum(p.numel() for p in self.model.parameters()):,} parameters")
    
    def _train_model(self, dataset):
        """Train the model."""
        if not self.model:
            raise ValueError("Model not built")
        
        # Prepare training config
        train_config = TrainingConfig(
            output_dir=self.checkpoints_dir,
            **self.config.get("training", {})
        )
        
        # Initialize and run trainer
        self.trainer = Trainer(
            model=self.model,
            train_dataset=dataset,
            config=train_config,
            tokenizer=self.tokenizer
        )
        
        self.trainer.train()


def train(
    data_path: Union[str, Path, List[Union[str, Path]]],
    output_dir: Union[str, Path],
    config: Optional[Dict[str, Any]] = None,
    clean: bool = False
) -> TrainingPipeline:
    """
    High-level training function that handles the complete training pipeline.
    
    Args:
        data_path: Path to input data file(s) or directory
        output_dir: Directory to save outputs
        config: Optional configuration dictionary
        clean: If True, clean up previous outputs before starting
        
    Returns:
        TrainingPipeline: The trained pipeline instance
    """
    pipeline = TrainingPipeline(data_path, output_dir, config or {})
    pipeline.run(clean=clean)
    return pipeline
