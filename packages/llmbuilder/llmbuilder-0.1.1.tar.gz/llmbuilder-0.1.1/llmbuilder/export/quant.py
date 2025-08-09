"""
Model quantization utilities for LLMBuilder.

This module provides quantization methods to reduce model size and improve
inference speed for edge deployment scenarios.
"""

import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum

from ..utils import get_logger, ExportError, ModelError
from ..model import save_model

logger = get_logger("export.quant")


class QuantizationMethod(Enum):
    """Available quantization methods."""
    DYNAMIC = "dynamic"
    STATIC = "static"
    QAT = "qat"  # Quantization Aware Training
    INT8 = "int8"
    FP16 = "fp16"
    BF16 = "bf16"


@dataclass
class QuantizationConfig:
    """Configuration for model quantization."""
    method: QuantizationMethod = QuantizationMethod.DYNAMIC
    dtype: torch.dtype = torch.qint8
    backend: str = "fbgemm"  # fbgemm, qnnpack
    calibration_data: Optional[torch.utils.data.DataLoader] = None
    num_calibration_batches: int = 100
    preserve_accuracy: bool = True
    
    def __post_init__(self):
        """Validate quantization configuration."""
        if self.method == QuantizationMethod.STATIC and self.calibration_data is None:
            raise ValueError("Static quantization requires calibration_data")
        
        if self.backend not in ["fbgemm", "qnnpack"]:
            raise ValueError(f"Unsupported backend: {self.backend}")


class ModelQuantizer:
    """
    Model quantization utility for reducing model size and improving inference speed.
    
    Supports various quantization methods including dynamic quantization,
    static quantization, and mixed precision.
    """
    
    def __init__(self, config: Optional[QuantizationConfig] = None):
        """
        Initialize model quantizer.
        
        Args:
            config: Quantization configuration
        """
        self.config = config or QuantizationConfig()
        logger.info(f"ModelQuantizer initialized with {self.config.method.value} quantization")
    
    def quantize(self, 
                model: nn.Module,
                output_path: Optional[Union[str, Path]] = None) -> nn.Module:
        """
        Quantize a PyTorch model.
        
        Args:
            model: Model to quantize
            output_path: Optional path to save quantized model
            
        Returns:
            Quantized model
        """
        logger.info(f"Starting {self.config.method.value} quantization")
        
        try:
            # Prepare model for quantization
            model.eval()
            
            # Apply quantization based on method
            if self.config.method == QuantizationMethod.DYNAMIC:
                quantized_model = self._dynamic_quantization(model)
            elif self.config.method == QuantizationMethod.STATIC:
                quantized_model = self._static_quantization(model)
            elif self.config.method == QuantizationMethod.FP16:
                quantized_model = self._fp16_quantization(model)
            elif self.config.method == QuantizationMethod.BF16:
                quantized_model = self._bf16_quantization(model)
            elif self.config.method == QuantizationMethod.INT8:
                quantized_model = self._int8_quantization(model)
            else:
                raise ExportError(f"Unsupported quantization method: {self.config.method}")
            
            # Calculate size reduction
            original_size = self._get_model_size(model)
            quantized_size = self._get_model_size(quantized_model)
            reduction_ratio = (original_size - quantized_size) / original_size * 100
            
            logger.info(f"Quantization completed:")
            logger.info(f"  Original size: {original_size / 1024 / 1024:.1f} MB")
            logger.info(f"  Quantized size: {quantized_size / 1024 / 1024:.1f} MB")
            logger.info(f"  Size reduction: {reduction_ratio:.1f}%")
            
            # Save quantized model if path provided
            if output_path:
                self._save_quantized_model(quantized_model, output_path)
            
            return quantized_model
            
        except Exception as e:
            logger.error(f"Quantization failed: {e}")
            raise ExportError(f"Model quantization failed: {str(e)}") from e
    
    def _dynamic_quantization(self, model: nn.Module) -> nn.Module:
        """Apply dynamic quantization."""
        logger.info("Applying dynamic quantization")
        
        # Set quantization backend
        torch.backends.quantized.engine = self.config.backend
        
        # Define layers to quantize
        layers_to_quantize = {nn.Linear, nn.Conv1d, nn.Conv2d}
        
        # Apply dynamic quantization
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            qconfig_spec=layers_to_quantize,
            dtype=self.config.dtype
        )
        
        return quantized_model
    
    def _static_quantization(self, model: nn.Module) -> nn.Module:
        """Apply static quantization with calibration."""
        logger.info("Applying static quantization")
        
        if self.config.calibration_data is None:
            raise ExportError("Static quantization requires calibration data")
        
        # Set quantization backend
        torch.backends.quantized.engine = self.config.backend
        
        # Prepare model for static quantization
        model.qconfig = torch.quantization.get_default_qconfig(self.config.backend)
        torch.quantization.prepare(model, inplace=True)
        
        # Calibration phase
        logger.info("Running calibration...")
        model.eval()
        with torch.no_grad():
            for i, batch in enumerate(self.config.calibration_data):
                if i >= self.config.num_calibration_batches:
                    break
                
                # Forward pass for calibration
                if isinstance(batch, dict):
                    input_ids = batch.get('input_ids', batch.get('inputs'))
                else:
                    input_ids = batch
                
                if input_ids is not None:
                    try:
                        model(input_ids)
                    except Exception as e:
                        logger.warning(f"Calibration batch {i} failed: {e}")
                        continue
        
        # Convert to quantized model
        quantized_model = torch.quantization.convert(model, inplace=False)
        
        return quantized_model
    
    def _fp16_quantization(self, model: nn.Module) -> nn.Module:
        """Apply FP16 mixed precision."""
        logger.info("Applying FP16 quantization")
        
        # Convert model to half precision
        quantized_model = model.half()
        
        return quantized_model
    
    def _bf16_quantization(self, model: nn.Module) -> nn.Module:
        """Apply BF16 mixed precision."""
        logger.info("Applying BF16 quantization")
        
        # Convert model to bfloat16
        quantized_model = model.to(torch.bfloat16)
        
        return quantized_model
    
    def _int8_quantization(self, model: nn.Module) -> nn.Module:
        """Apply INT8 quantization."""
        logger.info("Applying INT8 quantization")
        
        # Use dynamic quantization with int8
        config = QuantizationConfig(
            method=QuantizationMethod.DYNAMIC,
            dtype=torch.qint8,
            backend=self.config.backend
        )
        
        quantizer = ModelQuantizer(config)
        return quantizer._dynamic_quantization(model)
    
    def _get_model_size(self, model: nn.Module) -> int:
        """Get model size in bytes."""
        param_size = 0
        buffer_size = 0
        
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        
        return param_size + buffer_size
    
    def _save_quantized_model(self, model: nn.Module, output_path: Union[str, Path]):
        """Save quantized model."""
        output_path = Path(output_path)
        
        try:
            # Create metadata for quantized model
            metadata = {
                'quantization_method': self.config.method.value,
                'quantization_dtype': str(self.config.dtype),
                'quantization_backend': self.config.backend,
                'model_size_bytes': self._get_model_size(model),
                'quantized': True
            }
            
            # Save using the model builder's save function
            save_model(model, output_path, additional_info=metadata)
            
            logger.info(f"Quantized model saved: {output_path}")
            
        except Exception as e:
            raise ExportError(f"Failed to save quantized model: {str(e)}") from e
    
    def benchmark_quantized_model(self, 
                                 original_model: nn.Module,
                                 quantized_model: nn.Module,
                                 test_input: torch.Tensor,
                                 num_runs: int = 100) -> Dict[str, Any]:
        """
        Benchmark quantized model against original.
        
        Args:
            original_model: Original model
            quantized_model: Quantized model
            test_input: Test input tensor
            num_runs: Number of benchmark runs
            
        Returns:
            Benchmark results
        """
        import time
        
        logger.info("Benchmarking quantized model...")
        
        # Warm up
        for _ in range(10):
            with torch.no_grad():
                original_model(test_input)
                quantized_model(test_input)
        
        # Benchmark original model
        original_times = []
        original_model.eval()
        for _ in range(num_runs):
            start_time = time.time()
            with torch.no_grad():
                original_model(test_input)
            original_times.append(time.time() - start_time)
        
        # Benchmark quantized model
        quantized_times = []
        quantized_model.eval()
        for _ in range(num_runs):
            start_time = time.time()
            with torch.no_grad():
                quantized_model(test_input)
            quantized_times.append(time.time() - start_time)
        
        # Calculate statistics
        original_avg = sum(original_times) / len(original_times)
        quantized_avg = sum(quantized_times) / len(quantized_times)
        speedup = original_avg / quantized_avg
        
        original_size = self._get_model_size(original_model)
        quantized_size = self._get_model_size(quantized_model)
        size_reduction = (original_size - quantized_size) / original_size * 100
        
        results = {
            'original_inference_time_ms': original_avg * 1000,
            'quantized_inference_time_ms': quantized_avg * 1000,
            'speedup_ratio': speedup,
            'original_size_mb': original_size / 1024 / 1024,
            'quantized_size_mb': quantized_size / 1024 / 1024,
            'size_reduction_percent': size_reduction,
            'quantization_method': self.config.method.value
        }
        
        logger.info(f"Benchmark results:")
        logger.info(f"  Speedup: {speedup:.2f}x")
        logger.info(f"  Size reduction: {size_reduction:.1f}%")
        logger.info(f"  Original inference: {original_avg * 1000:.2f}ms")
        logger.info(f"  Quantized inference: {quantized_avg * 1000:.2f}ms")
        
        return results


def quantize_model(model: nn.Module,
                  method: Union[str, QuantizationMethod] = "dynamic",
                  output_path: Optional[Union[str, Path]] = None,
                  **kwargs) -> nn.Module:
    """
    Convenience function for model quantization.
    
    Args:
        model: Model to quantize
        method: Quantization method
        output_path: Optional path to save quantized model
        **kwargs: Additional quantization parameters
        
    Returns:
        Quantized model
    """
    if isinstance(method, str):
        method = QuantizationMethod(method)
    
    config = QuantizationConfig(method=method, **kwargs)
    quantizer = ModelQuantizer(config)
    
    return quantizer.quantize(model, output_path)


def get_quantization_methods() -> List[str]:
    """Get list of available quantization methods."""
    return [method.value for method in QuantizationMethod]


def estimate_quantization_benefits(model: nn.Module, 
                                 method: Union[str, QuantizationMethod] = "dynamic") -> Dict[str, Any]:
    """
    Estimate quantization benefits without actually quantizing.
    
    Args:
        model: Model to analyze
        method: Quantization method
        
    Returns:
        Estimated benefits
    """
    if isinstance(method, str):
        method = QuantizationMethod(method)
    
    original_size = sum(p.numel() * p.element_size() for p in model.parameters())
    
    # Estimate size reduction based on method
    if method == QuantizationMethod.FP16:
        estimated_size = original_size / 2  # FP32 -> FP16
        estimated_speedup = 1.5
    elif method == QuantizationMethod.INT8:
        estimated_size = original_size / 4  # FP32 -> INT8
        estimated_speedup = 2.0
    elif method == QuantizationMethod.DYNAMIC:
        estimated_size = original_size * 0.6  # Conservative estimate
        estimated_speedup = 1.3
    else:
        estimated_size = original_size * 0.7
        estimated_speedup = 1.2
    
    size_reduction = (original_size - estimated_size) / original_size * 100
    
    return {
        'method': method.value,
        'original_size_mb': original_size / 1024 / 1024,
        'estimated_size_mb': estimated_size / 1024 / 1024,
        'estimated_size_reduction_percent': size_reduction,
        'estimated_speedup': estimated_speedup,
        'note': 'These are estimates. Actual results may vary.'
    }