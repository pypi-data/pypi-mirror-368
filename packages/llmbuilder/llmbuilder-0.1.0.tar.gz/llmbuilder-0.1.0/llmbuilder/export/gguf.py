"""
GGUF export utilities for LLMBuilder.

This module provides functionality to export trained models to GGUF format
for compatibility with llama.cpp and other GGML-based inference engines.
"""

import struct
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, BinaryIO
from dataclasses import dataclass
from enum import Enum

from ..utils import get_logger, ExportError
from ..model.gpt import GPTModel

logger = get_logger("export.gguf")


class GGUFValueType(Enum):
    """GGUF value types."""
    UINT8 = 0
    INT8 = 1
    UINT16 = 2
    INT16 = 3
    UINT32 = 4
    INT32 = 5
    FLOAT32 = 6
    BOOL = 7
    STRING = 8
    ARRAY = 9
    UINT64 = 10
    INT64 = 11
    FLOAT64 = 12


class GGUFTensorType(Enum):
    """GGUF tensor types."""
    F32 = 0
    F16 = 1
    Q4_0 = 2
    Q4_1 = 3
    Q5_0 = 6
    Q5_1 = 7
    Q8_0 = 8
    Q8_1 = 9
    Q2_K = 10
    Q3_K = 11
    Q4_K = 12
    Q5_K = 13
    Q6_K = 14
    Q8_K = 15


@dataclass
class GGUFExportConfig:
    """Configuration for GGUF export."""
    tensor_type: GGUFTensorType = GGUFTensorType.F16
    vocab_only: bool = False
    add_bos_token: bool = True
    add_eos_token: bool = True
    chat_template: Optional[str] = None
    
    def __post_init__(self):
        """Validate GGUF export configuration."""
        if not isinstance(self.tensor_type, GGUFTensorType):
            raise ValueError(f"Invalid tensor type: {self.tensor_type}")


class GGUFExporter:
    """
    GGUF format exporter for llama.cpp compatibility.
    
    Exports trained GPT models to GGUF format which can be used with
    llama.cpp and other GGML-based inference engines.
    """
    
    GGUF_MAGIC = 0x46554747  # "GGUF" in little endian
    GGUF_VERSION = 3
    
    def __init__(self, config: Optional[GGUFExportConfig] = None):
        """
        Initialize GGUF exporter.
        
        Args:
            config: Export configuration
        """
        self.config = config or GGUFExportConfig()
        logger.info(f"GGUFExporter initialized with {self.config.tensor_type.name} precision")
    
    def export(self, 
               model: nn.Module,
               tokenizer_path: Union[str, Path],
               output_path: Union[str, Path]) -> None:
        """
        Export model to GGUF format.
        
        Args:
            model: Trained model to export
            tokenizer_path: Path to tokenizer
            output_path: Output GGUF file path
        """
        output_path = Path(output_path)
        tokenizer_path = Path(tokenizer_path)
        
        logger.info(f"Exporting model to GGUF format: {output_path}")
        
        try:
            # Validate model type
            if not isinstance(model, GPTModel):
                raise ExportError(f"GGUF export only supports GPTModel, got {type(model)}")
            
            # Load tokenizer
            tokenizer = self._load_tokenizer(tokenizer_path)
            
            # Prepare model for export
            model.eval()
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write GGUF file
            with open(output_path, 'wb') as f:
                self._write_gguf_header(f)
                self._write_metadata(f, model, tokenizer)
                self._write_tensors(f, model)
            
            # Verify exported file
            file_size = output_path.stat().st_size
            logger.info(f"GGUF export completed: {output_path}")
            logger.info(f"File size: {file_size / 1024 / 1024:.1f} MB")
            
        except Exception as e:
            logger.error(f"GGUF export failed: {e}")
            raise ExportError(f"GGUF export failed: {str(e)}") from e
    
    def _load_tokenizer(self, tokenizer_path: Path):
        """Load tokenizer for vocabulary extraction."""
        try:
            # Try to load SentencePiece tokenizer
            import sentencepiece as spm
            
            tokenizer_model_path = tokenizer_path / "tokenizer.model"
            if tokenizer_model_path.exists():
                tokenizer = spm.SentencePieceProcessor()
                tokenizer.load(str(tokenizer_model_path))
                return tokenizer
            else:
                raise ExportError(f"Tokenizer model not found: {tokenizer_model_path}")
                
        except ImportError:
            raise ExportError("SentencePiece not installed. Required for GGUF export.")
        except Exception as e:
            raise ExportError(f"Failed to load tokenizer: {str(e)}")
    
    def _write_gguf_header(self, f: BinaryIO):
        """Write GGUF file header."""
        # Magic number
        f.write(struct.pack('<I', self.GGUF_MAGIC))
        
        # Version
        f.write(struct.pack('<I', self.GGUF_VERSION))
        
        # Placeholder for tensor count and metadata count (will be updated later)
        self.tensor_count_offset = f.tell()
        f.write(struct.pack('<Q', 0))  # tensor_count
        
        self.metadata_count_offset = f.tell()
        f.write(struct.pack('<Q', 0))  # metadata_count
    
    def _write_metadata(self, f: BinaryIO, model: GPTModel, tokenizer):
        """Write model metadata."""
        metadata_start = f.tell()
        metadata_count = 0
        
        # Model architecture
        self._write_metadata_kv(f, "general.architecture", "gpt")
        metadata_count += 1
        
        # Model name
        self._write_metadata_kv(f, "general.name", "llmbuilder-gpt")
        metadata_count += 1
        
        # Model parameters
        self._write_metadata_kv(f, "gpt.context_length", model.block_size)
        metadata_count += 1
        
        self._write_metadata_kv(f, "gpt.embedding_length", model.n_embd)
        metadata_count += 1
        
        self._write_metadata_kv(f, "gpt.block_count", model.n_layer)
        metadata_count += 1
        
        self._write_metadata_kv(f, "gpt.attention.head_count", model.n_head)
        metadata_count += 1
        
        # Vocabulary size
        self._write_metadata_kv(f, "tokenizer.ggml.model", "gpt2")
        metadata_count += 1
        
        # Tokenizer tokens
        vocab_size = tokenizer.vocab_size()
        tokens = []
        scores = []
        
        for i in range(vocab_size):
            token = tokenizer.id_to_piece(i)
            score = tokenizer.get_score(i)
            tokens.append(token)
            scores.append(score)
        
        self._write_metadata_kv(f, "tokenizer.ggml.tokens", tokens)
        metadata_count += 1
        
        self._write_metadata_kv(f, "tokenizer.ggml.scores", scores)
        metadata_count += 1
        
        # Special tokens
        self._write_metadata_kv(f, "tokenizer.ggml.bos_token_id", tokenizer.bos_id())
        metadata_count += 1
        
        self._write_metadata_kv(f, "tokenizer.ggml.eos_token_id", tokenizer.eos_id())
        metadata_count += 1
        
        self._write_metadata_kv(f, "tokenizer.ggml.unknown_token_id", tokenizer.unk_id())
        metadata_count += 1
        
        self._write_metadata_kv(f, "tokenizer.ggml.padding_token_id", tokenizer.pad_id())
        metadata_count += 1
        
        # Update metadata count in header
        current_pos = f.tell()
        f.seek(self.metadata_count_offset)
        f.write(struct.pack('<Q', metadata_count))
        f.seek(current_pos)
        
        logger.info(f"Wrote {metadata_count} metadata entries")
    
    def _write_metadata_kv(self, f: BinaryIO, key: str, value):
        """Write a metadata key-value pair."""
        # Write key
        key_bytes = key.encode('utf-8')
        f.write(struct.pack('<Q', len(key_bytes)))
        f.write(key_bytes)
        
        # Write value based on type
        if isinstance(value, str):
            self._write_value(f, GGUFValueType.STRING, value)
        elif isinstance(value, int):
            self._write_value(f, GGUFValueType.UINT32, value)
        elif isinstance(value, float):
            self._write_value(f, GGUFValueType.FLOAT32, value)
        elif isinstance(value, bool):
            self._write_value(f, GGUFValueType.BOOL, value)
        elif isinstance(value, list):
            self._write_array_value(f, value)
        else:
            raise ExportError(f"Unsupported metadata value type: {type(value)}")
    
    def _write_value(self, f: BinaryIO, value_type: GGUFValueType, value):
        """Write a typed value."""
        f.write(struct.pack('<I', value_type.value))
        
        if value_type == GGUFValueType.STRING:
            value_bytes = value.encode('utf-8')
            f.write(struct.pack('<Q', len(value_bytes)))
            f.write(value_bytes)
        elif value_type == GGUFValueType.UINT32:
            f.write(struct.pack('<I', value))
        elif value_type == GGUFValueType.FLOAT32:
            f.write(struct.pack('<f', value))
        elif value_type == GGUFValueType.BOOL:
            f.write(struct.pack('<B', 1 if value else 0))
        else:
            raise ExportError(f"Unsupported value type for writing: {value_type}")
    
    def _write_array_value(self, f: BinaryIO, array):
        """Write an array value."""
        f.write(struct.pack('<I', GGUFValueType.ARRAY.value))
        
        if not array:
            f.write(struct.pack('<I', GGUFValueType.STRING.value))
            f.write(struct.pack('<Q', 0))
            return
        
        # Determine array element type
        first_element = array[0]
        if isinstance(first_element, str):
            element_type = GGUFValueType.STRING
        elif isinstance(first_element, int):
            element_type = GGUFValueType.UINT32
        elif isinstance(first_element, float):
            element_type = GGUFValueType.FLOAT32
        else:
            raise ExportError(f"Unsupported array element type: {type(first_element)}")
        
        # Write array type and length
        f.write(struct.pack('<I', element_type.value))
        f.write(struct.pack('<Q', len(array)))
        
        # Write array elements
        for element in array:
            if element_type == GGUFValueType.STRING:
                element_bytes = element.encode('utf-8')
                f.write(struct.pack('<Q', len(element_bytes)))
                f.write(element_bytes)
            elif element_type == GGUFValueType.UINT32:
                f.write(struct.pack('<I', element))
            elif element_type == GGUFValueType.FLOAT32:
                f.write(struct.pack('<f', element))
    
    def _write_tensors(self, f: BinaryIO, model: GPTModel):
        """Write model tensors."""
        tensor_count = 0
        
        # Get model state dict
        state_dict = model.state_dict()
        
        # Write tensor info first
        tensor_info_start = f.tell()
        
        for name, tensor in state_dict.items():
            # Convert tensor name to GGUF format
            gguf_name = self._convert_tensor_name(name)
            
            # Write tensor name
            name_bytes = gguf_name.encode('utf-8')
            f.write(struct.pack('<Q', len(name_bytes)))
            f.write(name_bytes)
            
            # Write tensor dimensions
            shape = list(tensor.shape)
            f.write(struct.pack('<I', len(shape)))
            for dim in reversed(shape):  # GGUF uses reverse dimension order
                f.write(struct.pack('<Q', dim))
            
            # Write tensor type
            f.write(struct.pack('<I', self.config.tensor_type.value))
            
            # Write tensor data offset (placeholder, will be updated)
            f.write(struct.pack('<Q', 0))
            
            tensor_count += 1
        
        # Align to 32-byte boundary for tensor data
        current_pos = f.tell()
        alignment = 32
        padding = (alignment - (current_pos % alignment)) % alignment
        f.write(b'\x00' * padding)
        
        # Write actual tensor data
        tensor_data_start = f.tell()
        tensor_offsets = []
        
        for name, tensor in state_dict.items():
            tensor_offset = f.tell() - tensor_data_start
            tensor_offsets.append(tensor_offset)
            
            # Convert tensor to target precision
            if self.config.tensor_type == GGUFTensorType.F16:
                tensor_data = tensor.half().numpy().tobytes()
            elif self.config.tensor_type == GGUFTensorType.F32:
                tensor_data = tensor.float().numpy().tobytes()
            else:
                # For quantized formats, we'd need more complex conversion
                logger.warning(f"Quantized tensor type {self.config.tensor_type.name} not fully implemented, using F32")
                tensor_data = tensor.float().numpy().tobytes()
            
            f.write(tensor_data)
            
            # Align to 32-byte boundary
            current_pos = f.tell()
            padding = (alignment - (current_pos % alignment)) % alignment
            f.write(b'\x00' * padding)
        
        # Update tensor count in header
        current_pos = f.tell()
        f.seek(self.tensor_count_offset)
        f.write(struct.pack('<Q', tensor_count))
        
        # Update tensor offsets
        f.seek(tensor_info_start)
        offset_idx = 0
        
        for name, tensor in state_dict.items():
            # Skip to offset field
            gguf_name = self._convert_tensor_name(name)
            name_bytes = gguf_name.encode('utf-8')
            f.seek(f.tell() + 8 + len(name_bytes))  # Skip length and name
            f.seek(f.tell() + 4 + len(tensor.shape) * 8)  # Skip ndim and dimensions
            f.seek(f.tell() + 4)  # Skip tensor type
            
            # Write actual offset
            f.write(struct.pack('<Q', tensor_offsets[offset_idx]))
            offset_idx += 1
        
        f.seek(current_pos)
        logger.info(f"Wrote {tensor_count} tensors")
    
    def _convert_tensor_name(self, pytorch_name: str) -> str:
        """Convert PyTorch tensor name to GGUF format."""
        # Map PyTorch parameter names to GGUF names
        name_mapping = {
            'token_embedding.weight': 'token_embd.weight',
            'position_embedding.weight': 'pos_embd.weight',
            'ln_f.weight': 'output_norm.weight',
            'ln_f.bias': 'output_norm.bias',
            'lm_head.weight': 'output.weight',
        }
        
        # Handle transformer blocks
        if pytorch_name.startswith('blocks.'):
            parts = pytorch_name.split('.')
            block_idx = parts[1]
            
            if 'ln1' in pytorch_name:
                return pytorch_name.replace(f'blocks.{block_idx}.ln1', f'blk.{block_idx}.attn_norm')
            elif 'ln2' in pytorch_name:
                return pytorch_name.replace(f'blocks.{block_idx}.ln2', f'blk.{block_idx}.ffn_norm')
            elif 'attn.qkv_proj' in pytorch_name:
                return pytorch_name.replace(f'blocks.{block_idx}.attn.qkv_proj', f'blk.{block_idx}.attn_qkv')
            elif 'attn.out_proj' in pytorch_name:
                return pytorch_name.replace(f'blocks.{block_idx}.attn.out_proj', f'blk.{block_idx}.attn_output')
            elif 'mlp.fc1' in pytorch_name:
                return pytorch_name.replace(f'blocks.{block_idx}.mlp.fc1', f'blk.{block_idx}.ffn_up')
            elif 'mlp.fc2' in pytorch_name:
                return pytorch_name.replace(f'blocks.{block_idx}.mlp.fc2', f'blk.{block_idx}.ffn_down')
        
        return name_mapping.get(pytorch_name, pytorch_name)
    
    def validate_export(self, gguf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate exported GGUF file.
        
        Args:
            gguf_path: Path to GGUF file
            
        Returns:
            Validation results
        """
        gguf_path = Path(gguf_path)
        
        if not gguf_path.exists():
            return {'valid': False, 'error': 'File does not exist'}
        
        try:
            with open(gguf_path, 'rb') as f:
                # Check magic number
                magic = struct.unpack('<I', f.read(4))[0]
                if magic != self.GGUF_MAGIC:
                    return {'valid': False, 'error': f'Invalid magic number: {magic:08x}'}
                
                # Check version
                version = struct.unpack('<I', f.read(4))[0]
                if version != self.GGUF_VERSION:
                    return {'valid': False, 'error': f'Unsupported version: {version}'}
                
                # Read counts
                tensor_count = struct.unpack('<Q', f.read(8))[0]
                metadata_count = struct.unpack('<Q', f.read(8))[0]
                
                file_size = gguf_path.stat().st_size
                
                return {
                    'valid': True,
                    'version': version,
                    'tensor_count': tensor_count,
                    'metadata_count': metadata_count,
                    'file_size_mb': file_size / 1024 / 1024
                }
                
        except Exception as e:
            return {'valid': False, 'error': str(e)}


def export_gguf(model: nn.Module,
               tokenizer_path: Union[str, Path],
               output_path: Union[str, Path],
               tensor_type: str = "f16") -> None:
    """
    Convenience function for GGUF export.
    
    Args:
        model: Model to export
        tokenizer_path: Path to tokenizer
        output_path: Output GGUF file path
        tensor_type: Tensor precision type
    """
    # Convert string to enum
    if isinstance(tensor_type, str):
        tensor_type_map = {
            'f32': GGUFTensorType.F32,
            'f16': GGUFTensorType.F16,
            'q4_0': GGUFTensorType.Q4_0,
            'q4_1': GGUFTensorType.Q4_1,
            'q8_0': GGUFTensorType.Q8_0,
        }
        tensor_type = tensor_type_map.get(tensor_type.lower(), GGUFTensorType.F16)
    
    config = GGUFExportConfig(tensor_type=tensor_type)
    exporter = GGUFExporter(config)
    
    exporter.export(model, tokenizer_path, output_path)