"""
ONNX export utilities for LLMBuilder.

This module provides functionality to export trained models to ONNX format
for mobile and runtime inference across different platforms.
"""

import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
from dataclasses import dataclass

from ..utils import get_logger, ExportError
from ..model.gpt import GPTModel

logger = get_logger("export.onnx")

# Optional ONNX imports
try:
    import onnx
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False


@dataclass
class ONNXExportConfig:
    """Configuration for ONNX export."""
    opset_version: int = 11
    dynamic_axes: bool = True
    optimize: bool = True
    check_model: bool = True
    export_params: bool = True
    do_constant_folding: bool = True
    input_names: List[str] = None
    output_names: List[str] = None
    
    def __post_init__(self):
        """Set default input/output names if not provided."""
        if self.input_names is None:
            self.input_names = ['input_ids']
        if self.output_names is None:
            self.output_names = ['logits']


class ONNXExporter:
    """
    ONNX format exporter for mobile and runtime inference.
    
    Exports trained models to ONNX format which can be used across
    different platforms and inference engines.
    """
    
    def __init__(self, config: Optional[ONNXExportConfig] = None):
        """
        Initialize ONNX exporter.
        
        Args:
            config: Export configuration
        """
        if not HAS_ONNX:
            raise ExportError(
                "ONNX not installed. Install with: pip install onnx onnxruntime"
            )
        
        self.config = config or ONNXExportConfig()
        logger.info(f"ONNXExporter initialized with opset version {self.config.opset_version}")
    
    def export(self, 
               model: nn.Module,
               output_path: Union[str, Path],
               example_input: Optional[torch.Tensor] = None,
               batch_size: int = 1,
               sequence_length: int = 128) -> None:
        """
        Export model to ONNX format.
        
        Args:
            model: Model to export
            output_path: Output ONNX file path
            example_input: Example input tensor (optional)
            batch_size: Batch size for example input
            sequence_length: Sequence length for example input
        """
        output_path = Path(output_path)
        
        logger.info(f"Exporting model to ONNX format: {output_path}")
        
        try:
            # Prepare model for export
            model.eval()
            
            # Create example input if not provided
            if example_input is None:
                if isinstance(model, GPTModel):
                    example_input = torch.randint(
                        0, model.vocab_size, 
                        (batch_size, sequence_length),
                        dtype=torch.long
                    )
                else:
                    raise ExportError("example_input required for non-GPT models")
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Set up dynamic axes for variable input sizes
            dynamic_axes = {}
            if self.config.dynamic_axes:
                dynamic_axes = {
                    self.config.input_names[0]: {0: 'batch_size', 1: 'sequence_length'},
                    self.config.output_names[0]: {0: 'batch_size', 1: 'sequence_length'}
                }
            
            # Export to ONNX
            with torch.no_grad():
                torch.onnx.export(
                    model,
                    example_input,
                    str(output_path),
                    export_params=self.config.export_params,
                    opset_version=self.config.opset_version,
                    do_constant_folding=self.config.do_constant_folding,
                    input_names=self.config.input_names,
                    output_names=self.config.output_names,
                    dynamic_axes=dynamic_axes if self.config.dynamic_axes else None,
                    verbose=False
                )
            
            # Validate exported model
            if self.config.check_model:
                self._validate_onnx_model(output_path)
            
            # Optimize model if requested
            if self.config.optimize:
                self._optimize_onnx_model(output_path)
            
            # Get file size
            file_size = output_path.stat().st_size
            logger.info(f"ONNX export completed: {output_path}")
            logger.info(f"File size: {file_size / 1024 / 1024:.1f} MB")
            
        except Exception as e:
            logger.error(f"ONNX export failed: {e}")
            raise ExportError(f"ONNX export failed: {str(e)}") from e
    
    def _validate_onnx_model(self, model_path: Path):
        """Validate exported ONNX model."""
        try:
            # Load and check ONNX model
            onnx_model = onnx.load(str(model_path))
            onnx.checker.check_model(onnx_model)
            
            logger.info("ONNX model validation passed")
            
        except Exception as e:
            logger.warning(f"ONNX model validation failed: {e}")
    
    def _optimize_onnx_model(self, model_path: Path):
        """Optimize ONNX model for inference."""
        try:
            # Create optimized model path
            optimized_path = model_path.with_suffix('.optimized.onnx')
            
            # Load model
            onnx_model = onnx.load(str(model_path))
            
            # Apply optimizations
            from onnx import optimizer
            
            # List of optimization passes
            passes = [
                'eliminate_identity',
                'eliminate_nop_dropout',
                'eliminate_nop_monotone_argmax',
                'eliminate_nop_pad',
                'eliminate_nop_transpose',
                'eliminate_unused_initializer',
                'extract_constant_to_initializer',
                'fuse_add_bias_into_conv',
                'fuse_bn_into_conv',
                'fuse_consecutive_concats',
                'fuse_consecutive_log_softmax',
                'fuse_consecutive_reduce_unsqueeze',
                'fuse_consecutive_squeezes',
                'fuse_consecutive_transposes',
                'fuse_matmul_add_bias_into_gemm',
                'fuse_pad_into_conv',
                'fuse_transpose_into_gemm',
            ]
            
            # Apply optimizations
            optimized_model = optimizer.optimize(onnx_model, passes)
            
            # Save optimized model
            onnx.save(optimized_model, str(optimized_path))
            
            # Replace original with optimized
            optimized_path.replace(model_path)
            
            logger.info("ONNX model optimization completed")
            
        except Exception as e:
            logger.warning(f"ONNX model optimization failed: {e}")
    
    def benchmark_onnx_model(self, 
                            onnx_path: Union[str, Path],
                            original_model: nn.Module,
                            test_input: torch.Tensor,
                            num_runs: int = 100) -> Dict[str, Any]:
        """
        Benchmark ONNX model against original PyTorch model.
        
        Args:
            onnx_path: Path to ONNX model
            original_model: Original PyTorch model
            test_input: Test input tensor
            num_runs: Number of benchmark runs
            
        Returns:
            Benchmark results
        """
        import time
        
        logger.info("Benchmarking ONNX model...")
        
        try:
            # Create ONNX Runtime session
            ort_session = ort.InferenceSession(str(onnx_path))
            
            # Get input name
            input_name = ort_session.get_inputs()[0].name
            
            # Prepare input for ONNX Runtime
            ort_input = {input_name: test_input.numpy()}
            
            # Warm up
            for _ in range(10):
                with torch.no_grad():
                    original_model(test_input)
                ort_session.run(None, ort_input)
            
            # Benchmark PyTorch model
            pytorch_times = []
            original_model.eval()
            for _ in range(num_runs):
                start_time = time.time()
                with torch.no_grad():
                    original_model(test_input)
                pytorch_times.append(time.time() - start_time)
            
            # Benchmark ONNX model
            onnx_times = []
            for _ in range(num_runs):
                start_time = time.time()
                ort_session.run(None, ort_input)
                onnx_times.append(time.time() - start_time)
            
            # Calculate statistics
            pytorch_avg = sum(pytorch_times) / len(pytorch_times)
            onnx_avg = sum(onnx_times) / len(onnx_times)
            speedup = pytorch_avg / onnx_avg
            
            # Get file sizes
            onnx_path = Path(onnx_path)
            onnx_size = onnx_path.stat().st_size
            
            # Estimate PyTorch model size
            pytorch_size = sum(p.numel() * p.element_size() for p in original_model.parameters())
            
            results = {
                'pytorch_inference_time_ms': pytorch_avg * 1000,
                'onnx_inference_time_ms': onnx_avg * 1000,
                'speedup_ratio': speedup,
                'pytorch_size_mb': pytorch_size / 1024 / 1024,
                'onnx_size_mb': onnx_size / 1024 / 1024,
                'size_ratio': onnx_size / pytorch_size,
                'opset_version': self.config.opset_version
            }
            
            logger.info(f"Benchmark results:")
            logger.info(f"  Speedup: {speedup:.2f}x")
            logger.info(f"  PyTorch inference: {pytorch_avg * 1000:.2f}ms")
            logger.info(f"  ONNX inference: {onnx_avg * 1000:.2f}ms")
            logger.info(f"  Size ratio: {onnx_size / pytorch_size:.2f}x")
            
            return results
            
        except Exception as e:
            logger.error(f"ONNX benchmarking failed: {e}")
            return {'error': str(e)}
    
    def validate_export(self, 
                       onnx_path: Union[str, Path],
                       original_model: nn.Module,
                       test_input: torch.Tensor,
                       tolerance: float = 1e-5) -> Dict[str, Any]:
        """
        Validate ONNX export by comparing outputs.
        
        Args:
            onnx_path: Path to ONNX model
            original_model: Original PyTorch model
            test_input: Test input tensor
            tolerance: Numerical tolerance for comparison
            
        Returns:
            Validation results
        """
        try:
            # Get PyTorch output
            original_model.eval()
            with torch.no_grad():
                if isinstance(original_model, GPTModel):
                    pytorch_output, _ = original_model(test_input)
                else:
                    pytorch_output = original_model(test_input)
            
            # Get ONNX output
            ort_session = ort.InferenceSession(str(onnx_path))
            input_name = ort_session.get_inputs()[0].name
            ort_input = {input_name: test_input.numpy()}
            onnx_output = ort_session.run(None, ort_input)[0]
            
            # Convert ONNX output to tensor for comparison
            onnx_output_tensor = torch.from_numpy(onnx_output)
            
            # Compare outputs
            max_diff = torch.max(torch.abs(pytorch_output - onnx_output_tensor)).item()
            mean_diff = torch.mean(torch.abs(pytorch_output - onnx_output_tensor)).item()
            
            # Check if within tolerance
            outputs_match = max_diff < tolerance
            
            results = {
                'outputs_match': outputs_match,
                'max_difference': max_diff,
                'mean_difference': mean_diff,
                'tolerance': tolerance,
                'pytorch_output_shape': list(pytorch_output.shape),
                'onnx_output_shape': list(onnx_output.shape)
            }
            
            if outputs_match:
                logger.info(f"ONNX export validation passed (max_diff: {max_diff:.2e})")
            else:
                logger.warning(f"ONNX export validation failed (max_diff: {max_diff:.2e})")
            
            return results
            
        except Exception as e:
            logger.error(f"ONNX validation failed: {e}")
            return {'error': str(e), 'outputs_match': False}
    
    def get_model_info(self, onnx_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about an ONNX model.
        
        Args:
            onnx_path: Path to ONNX model
            
        Returns:
            Model information
        """
        try:
            onnx_model = onnx.load(str(onnx_path))
            
            # Get model info
            info = {
                'ir_version': onnx_model.ir_version,
                'opset_version': onnx_model.opset_import[0].version if onnx_model.opset_import else None,
                'producer_name': onnx_model.producer_name,
                'producer_version': onnx_model.producer_version,
                'model_version': onnx_model.model_version,
                'doc_string': onnx_model.doc_string,
            }
            
            # Get input/output info
            inputs = []
            for input_tensor in onnx_model.graph.input:
                input_info = {
                    'name': input_tensor.name,
                    'type': input_tensor.type.tensor_type.elem_type,
                    'shape': [dim.dim_value for dim in input_tensor.type.tensor_type.shape.dim]
                }
                inputs.append(input_info)
            
            outputs = []
            for output_tensor in onnx_model.graph.output:
                output_info = {
                    'name': output_tensor.name,
                    'type': output_tensor.type.tensor_type.elem_type,
                    'shape': [dim.dim_value for dim in output_tensor.type.tensor_type.shape.dim]
                }
                outputs.append(output_info)
            
            info['inputs'] = inputs
            info['outputs'] = outputs
            info['num_nodes'] = len(onnx_model.graph.node)
            
            # Get file size
            onnx_path = Path(onnx_path)
            info['file_size_mb'] = onnx_path.stat().st_size / 1024 / 1024
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get ONNX model info: {e}")
            return {'error': str(e)}


def export_onnx(model: nn.Module,
               output_path: Union[str, Path],
               example_input: Optional[torch.Tensor] = None,
               opset_version: int = 11,
               dynamic_axes: bool = True,
               optimize: bool = True) -> None:
    """
    Convenience function for ONNX export.
    
    Args:
        model: Model to export
        output_path: Output ONNX file path
        example_input: Example input tensor
        opset_version: ONNX opset version
        dynamic_axes: Whether to use dynamic axes
        optimize: Whether to optimize the model
    """
    config = ONNXExportConfig(
        opset_version=opset_version,
        dynamic_axes=dynamic_axes,
        optimize=optimize
    )
    
    exporter = ONNXExporter(config)
    exporter.export(model, output_path, example_input)


def create_onnx_runtime_session(onnx_path: Union[str, Path],
                               providers: Optional[List[str]] = None) -> 'ort.InferenceSession':
    """
    Create ONNX Runtime inference session.
    
    Args:
        onnx_path: Path to ONNX model
        providers: List of execution providers
        
    Returns:
        ONNX Runtime session
    """
    if not HAS_ONNX:
        raise ExportError("ONNX Runtime not installed")
    
    if providers is None:
        providers = ['CPUExecutionProvider']
    
    try:
        session = ort.InferenceSession(str(onnx_path), providers=providers)
        logger.info(f"Created ONNX Runtime session with providers: {providers}")
        return session
    except Exception as e:
        raise ExportError(f"Failed to create ONNX Runtime session: {str(e)}") from e