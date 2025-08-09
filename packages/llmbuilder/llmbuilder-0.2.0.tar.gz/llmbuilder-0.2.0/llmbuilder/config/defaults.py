"""
Default configuration classes for LLMBuilder.

This module provides predefined configurations for common use cases
including different hardware setups and model sizes.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import torch


@dataclass
class ModelConfig:
    """Configuration for model architecture."""
    vocab_size: int = 16000
    embedding_dim: int = 512
    num_layers: int = 8
    num_heads: int = 8
    max_seq_length: int = 1024
    dropout: float = 0.1
    layer_norm_eps: float = 1e-5
    use_bias: bool = True
    activation: str = "gelu"
    model_type: str = "gpt"
    
    def __post_init__(self):
        """Validate model configuration."""
        if self.embedding_dim % self.num_heads != 0:
            raise ValueError(f"embedding_dim ({self.embedding_dim}) must be divisible by num_heads ({self.num_heads})")
        if self.vocab_size <= 0:
            raise ValueError(f"vocab_size must be positive, got {self.vocab_size}")
        if self.num_layers <= 0:
            raise ValueError(f"num_layers must be positive, got {self.num_layers}")


@dataclass
class TrainingConfig:
    """Configuration for training parameters."""
    batch_size: int = 32
    learning_rate: float = 3e-4
    num_epochs: int = 10
    weight_decay: float = 0.01
    gradient_clip_norm: float = 1.0
    warmup_steps: int = 1000
    save_every: int = 1000
    eval_every: int = 500
    log_every: int = 100
    max_grad_norm: float = 1.0
    beta1: float = 0.9
    beta2: float = 0.999
    eps: float = 1e-8
    
    def __post_init__(self):
        """Validate training configuration."""
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {self.batch_size}")
        if self.learning_rate <= 0:
            raise ValueError(f"learning_rate must be positive, got {self.learning_rate}")
        if self.num_epochs <= 0:
            raise ValueError(f"num_epochs must be positive, got {self.num_epochs}")


@dataclass
class DataConfig:
    """Configuration for data processing."""
    max_length: int = 1024
    stride: int = 512
    min_length: int = 10
    clean_text: bool = True
    remove_duplicates: bool = True
    shuffle: bool = True
    validation_split: float = 0.1
    test_split: float = 0.1
    
    def __post_init__(self):
        """Validate data configuration."""
        if self.validation_split < 0 or self.validation_split > 1:
            raise ValueError(f"validation_split must be between 0 and 1, got {self.validation_split}")
        if self.test_split < 0 or self.test_split > 1:
            raise ValueError(f"test_split must be between 0 and 1, got {self.test_split}")
        if self.validation_split + self.test_split >= 1:
            raise ValueError("validation_split + test_split must be less than 1")


@dataclass
class TokenizerConfig:
    """Configuration for tokenizer training."""
    vocab_size: int = 16000
    model_type: str = "bpe"  # bpe, unigram, word, char
    character_coverage: float = 0.9995
    max_sentence_length: int = 4192
    shuffle_input_sentence: bool = True
    normalization_rule_name: str = "nmt_nfkc_cf"
    remove_extra_whitespaces: bool = True
    add_dummy_prefix: bool = True
    
    def __post_init__(self):
        """Validate tokenizer configuration."""
        if self.vocab_size <= 0:
            raise ValueError(f"vocab_size must be positive, got {self.vocab_size}")
        if self.model_type not in ["bpe", "unigram", "word", "char"]:
            raise ValueError(f"model_type must be one of ['bpe', 'unigram', 'word', 'char'], got {self.model_type}")


@dataclass
class InferenceConfig:
    """Configuration for text generation."""
    max_new_tokens: int = 100
    temperature: float = 0.8
    top_k: int = 50
    top_p: float = 0.9
    repetition_penalty: float = 1.1
    do_sample: bool = True
    num_beams: int = 1
    early_stopping: bool = False
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
    
    def __post_init__(self):
        """Validate inference configuration."""
        if self.temperature <= 0:
            raise ValueError(f"temperature must be positive, got {self.temperature}")
        if self.top_k <= 0:
            raise ValueError(f"top_k must be positive, got {self.top_k}")
        if self.top_p <= 0 or self.top_p > 1:
            raise ValueError(f"top_p must be between 0 and 1, got {self.top_p}")


@dataclass
class SystemConfig:
    """Configuration for system and hardware settings."""
    device: str = "auto"  # auto, cpu, cuda, mps
    mixed_precision: bool = False
    compile_model: bool = False
    num_workers: int = 4
    pin_memory: bool = True
    persistent_workers: bool = True
    
    def __post_init__(self):
        """Validate and set system configuration."""
        if self.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        
        # Disable mixed precision for CPU
        if self.device == "cpu":
            self.mixed_precision = False


@dataclass
class PathConfig:
    """Configuration for file paths."""
    data_dir: str = "data"
    model_dir: str = "models"
    checkpoint_dir: str = "checkpoints"
    tokenizer_dir: str = "tokenizers"
    output_dir: str = "output"
    log_dir: str = "logs"
    cache_dir: str = "cache"


@dataclass
class Config:
    """Main configuration class combining all sub-configurations."""
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    tokenizer: TokenizerConfig = field(default_factory=TokenizerConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    
    def validate(self) -> bool:
        """Validate the entire configuration."""
        # Cross-validation between configs
        if self.model.vocab_size != self.tokenizer.vocab_size:
            raise ValueError(
                f"Model vocab_size ({self.model.vocab_size}) must match "
                f"tokenizer vocab_size ({self.tokenizer.vocab_size})"
            )
        
        if self.model.max_seq_length < self.data.max_length:
            raise ValueError(
                f"Model max_seq_length ({self.model.max_seq_length}) must be >= "
                f"data max_length ({self.data.max_length})"
            )
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        from dataclasses import asdict
        return asdict(self)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create configuration from dictionary."""
        # Backward-compat: accept flat/legacy keys (e.g., n_layer, n_head, n_embd, block_size, dropout, bias, device, vocab_size)
        legacy_keys = {
            'n_layer', 'n_head', 'n_embd', 'block_size', 'dropout', 'bias', 'device', 'vocab_size'
        }
        cfg = dict(config_dict) if config_dict else {}
        model_over = dict(cfg.get('model', {}))
        data_over = dict(cfg.get('data', {}))
        tokenizer_over = dict(cfg.get('tokenizer', {}))
        system_over = dict(cfg.get('system', {}))

        if any(k in cfg for k in legacy_keys):
            # Map legacy to structured overrides
            if 'vocab_size' in cfg:
                model_over['vocab_size'] = cfg['vocab_size']
                tokenizer_over['vocab_size'] = cfg['vocab_size']
            if 'n_embd' in cfg:
                model_over['embedding_dim'] = cfg['n_embd']
            if 'n_layer' in cfg:
                model_over['num_layers'] = cfg['n_layer']
            if 'n_head' in cfg:
                model_over['num_heads'] = cfg['n_head']
            if 'block_size' in cfg:
                model_over['max_seq_length'] = cfg['block_size']
                data_over['max_length'] = cfg['block_size']
            if 'dropout' in cfg:
                model_over['dropout'] = cfg['dropout']
            if 'bias' in cfg:
                model_over['use_bias'] = cfg['bias']
            if 'device' in cfg:
                system_over['device'] = cfg['device']

        # Extract sub-configs with overrides
        model_config = ModelConfig(**model_over)
        training_config = TrainingConfig(**cfg.get('training', {}))
        data_config = DataConfig(**data_over)
        tokenizer_config = TokenizerConfig(**tokenizer_over)
        inference_config = InferenceConfig(**cfg.get('inference', {}))
        system_config = SystemConfig(**system_over)
        paths_config = PathConfig(**cfg.get('paths', {}))
        
        return cls(
            model=model_config,
            training=training_config,
            data=data_config,
            tokenizer=tokenizer_config,
            inference=inference_config,
            system=system_config,
            paths=paths_config
        )

    # --- Legacy attribute aliases for backward-compatibility (used by tests) ---
    @property
    def n_layer(self) -> int:
        return self.model.num_layers

    @property
    def n_head(self) -> int:
        return self.model.num_heads

    @property
    def n_embd(self) -> int:
        return self.model.embedding_dim

    @property
    def block_size(self) -> int:
        return self.model.max_seq_length

    @property
    def dropout(self) -> float:
        return self.model.dropout

    @property
    def bias(self) -> bool:
        return self.model.use_bias

    @property
    def device(self) -> str:
        return self.system.device

    @property
    def vocab_size(self) -> int:
        return self.model.vocab_size


class DefaultConfigs:
    """Predefined configurations for common use cases."""
    
    @staticmethod
    def cpu_small() -> Config:
        """Small model configuration optimized for CPU training."""
        config = Config()
        
        # Small model for CPU
        config.model.embedding_dim = 256
        config.model.num_layers = 4
        config.model.num_heads = 4
        config.model.max_seq_length = 512
        
        # Adjust data config to match
        config.data.max_length = 512
        
        # CPU-optimized training
        config.training.batch_size = 8
        config.training.learning_rate = 1e-4
        config.system.device = "cpu"
        config.system.mixed_precision = False
        config.system.num_workers = 2
        
        # Smaller tokenizer
        config.tokenizer.vocab_size = 8000
        config.model.vocab_size = 8000
        
        return config
    
    @staticmethod
    def gpu_medium() -> Config:
        """Medium model configuration optimized for single GPU."""
        config = Config()
        
        # Medium model for GPU
        config.model.embedding_dim = 768
        config.model.num_layers = 12
        config.model.num_heads = 12
        config.model.max_seq_length = 1024
        
        # GPU-optimized training
        config.training.batch_size = 16
        config.training.learning_rate = 3e-4
        config.system.device = "cuda"
        config.system.mixed_precision = True
        config.system.num_workers = 4
        
        return config
    
    @staticmethod
    def gpu_large() -> Config:
        """Large model configuration for high-end GPU."""
        config = Config()
        
        # Large model
        config.model.embedding_dim = 1024
        config.model.num_layers = 24
        config.model.num_heads = 16
        config.model.max_seq_length = 2048
        
        # Large model training
        config.training.batch_size = 8
        config.training.learning_rate = 1e-4
        config.training.gradient_clip_norm = 0.5
        config.system.device = "cuda"
        config.system.mixed_precision = True
        config.system.compile_model = True
        
        # Larger tokenizer
        config.tokenizer.vocab_size = 32000
        config.model.vocab_size = 32000
        
        return config
    
    @staticmethod
    def inference_optimized() -> Config:
        """Configuration optimized for inference."""
        config = Config()
        
        # Balanced model for inference
        config.model.embedding_dim = 512
        config.model.num_layers = 8
        config.model.num_heads = 8
        config.model.dropout = 0.0  # No dropout for inference
        
        # Inference settings
        config.inference.temperature = 0.7
        config.inference.top_k = 40
        config.inference.top_p = 0.9
        config.inference.max_new_tokens = 256
        
        config.system.compile_model = True  # Optimize for inference
        
        return config
    
    @staticmethod
    def get_preset(name: str) -> Config:
        """Get a preset configuration by name."""
        presets = {
            "cpu_small": DefaultConfigs.cpu_small,
            "gpu_medium": DefaultConfigs.gpu_medium,
            "gpu_large": DefaultConfigs.gpu_large,
            "inference": DefaultConfigs.inference_optimized,
        }
        
        if name not in presets:
            available = ", ".join(presets.keys())
            raise ValueError(f"Unknown preset '{name}'. Available presets: {available}")
        
        return presets[name]()