"""
Device management utilities for LLMBuilder.

This module provides utilities for device detection, optimization,
and memory management across different hardware configurations.
"""

import torch
import platform
from typing import Optional, Dict, Any, List, Tuple
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
import gc

# Define exception locally to avoid circular imports
class DeviceError(Exception):
    """Device and hardware related errors."""
    def __init__(self, message: str, device: str = None, available_devices: list = None, cause: Exception = None):
        super().__init__(message)
        self.device = device
        self.available_devices = available_devices
        self.cause = cause
from .logger import get_logger

logger = get_logger("device")


class DeviceManager:
    """
    Manages device selection, optimization, and memory monitoring.
    
    Provides comprehensive device management including automatic device
    selection, memory monitoring, and optimization recommendations.
    """
    
    def __init__(self):
        self._device_info_cache = None
        self._optimal_device_cache = None
    
    def get_optimal_device(self, prefer_gpu: bool = True) -> torch.device:
        """
        Get the optimal device for computation.
        
        Args:
            prefer_gpu: Whether to prefer GPU over CPU
            
        Returns:
            torch.device: Optimal device for computation
        """
        if self._optimal_device_cache is not None:
            return self._optimal_device_cache
        
        try:
            # Check CUDA availability
            if prefer_gpu and torch.cuda.is_available():
                device = torch.device("cuda")
                logger.info(f"Selected CUDA device: {torch.cuda.get_device_name(0)}")
            
            # Check MPS availability (Apple Silicon)
            elif prefer_gpu and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = torch.device("mps")
                logger.info("Selected MPS device (Apple Silicon)")
            
            # Fallback to CPU
            else:
                device = torch.device("cpu")
                logger.info("Selected CPU device")
            
            self._optimal_device_cache = device
            return device
            
        except Exception as e:
            logger.warning(f"Error detecting optimal device: {str(e)}, falling back to CPU")
            device = torch.device("cpu")
            self._optimal_device_cache = device
            return device
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get comprehensive device information.
        
        Returns:
            Dict[str, Any]: Device information dictionary
        """
        if self._device_info_cache is not None:
            return self._device_info_cache
        
        info = {
            'platform': platform.platform(),
            'torch_version': torch.__version__,
        }
        
        if PSUTIL_AVAILABLE:
            info.update({
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'memory_available_gb': psutil.virtual_memory().available / (1024**3),
            })
        else:
            info.update({
                'cpu_count': 'unknown',
                'cpu_count_logical': 'unknown',
                'memory_total_gb': 'unknown',
                'memory_available_gb': 'unknown',
            })
        
        # CUDA information
        if torch.cuda.is_available():
            info.update({
                'cuda_available': True,
                'cuda_version': torch.version.cuda,
                'cudnn_version': torch.backends.cudnn.version(),
                'cuda_device_count': torch.cuda.device_count(),
                'cuda_devices': []
            })
            
            for i in range(torch.cuda.device_count()):
                device_props = torch.cuda.get_device_properties(i)
                device_info = {
                    'id': i,
                    'name': device_props.name,
                    'memory_total_gb': device_props.total_memory / (1024**3),
                    'memory_reserved_gb': torch.cuda.memory_reserved(i) / (1024**3),
                    'memory_allocated_gb': torch.cuda.memory_allocated(i) / (1024**3),
                    'compute_capability': f"{device_props.major}.{device_props.minor}",
                    'multiprocessor_count': device_props.multi_processor_count,
                }
                info['cuda_devices'].append(device_info)
        else:
            info['cuda_available'] = False
        
        # MPS information (Apple Silicon)
        if hasattr(torch.backends, 'mps'):
            info['mps_available'] = torch.backends.mps.is_available()
            if torch.backends.mps.is_available():
                info['mps_built'] = torch.backends.mps.is_built()
        else:
            info['mps_available'] = False
        
        self._device_info_cache = info
        return info
    
    def get_memory_info(self, device: Optional[torch.device] = None) -> Dict[str, float]:
        """
        Get memory information for a specific device.
        
        Args:
            device: Device to get memory info for (defaults to optimal device)
            
        Returns:
            Dict[str, float]: Memory information in GB
        """
        if device is None:
            device = self.get_optimal_device()
        
        if device.type == "cuda":
            return {
                'total_gb': torch.cuda.get_device_properties(device.index or 0).total_memory / (1024**3),
                'reserved_gb': torch.cuda.memory_reserved(device.index or 0) / (1024**3),
                'allocated_gb': torch.cuda.memory_allocated(device.index or 0) / (1024**3),
                'free_gb': (torch.cuda.get_device_properties(device.index or 0).total_memory - 
                           torch.cuda.memory_reserved(device.index or 0)) / (1024**3),
            }
        elif device.type == "cpu":
            if PSUTIL_AVAILABLE:
                vm = psutil.virtual_memory()
                return {
                    'total_gb': vm.total / (1024**3),
                    'available_gb': vm.available / (1024**3),
                    'used_gb': vm.used / (1024**3),
                    'free_gb': vm.free / (1024**3),
                }
            else:
                return {
                    'total_gb': 16.0,  # Default estimate
                    'available_gb': 8.0,
                    'used_gb': 8.0,
                    'free_gb': 8.0,
                }
        else:
            # MPS or other devices
            return {'total_gb': 0.0, 'available_gb': 0.0, 'used_gb': 0.0, 'free_gb': 0.0}
    
    def clear_memory(self, device: Optional[torch.device] = None) -> None:
        """
        Clear memory caches for a device.
        
        Args:
            device: Device to clear memory for (defaults to optimal device)
        """
        if device is None:
            device = self.get_optimal_device()
        
        # Clear Python garbage collection
        gc.collect()
        
        # Clear CUDA cache if using CUDA
        if device.type == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            logger.info("Cleared CUDA memory cache")
        
        # Clear MPS cache if using MPS
        elif device.type == "mps" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            if hasattr(torch.mps, 'empty_cache'):
                torch.mps.empty_cache()
                logger.info("Cleared MPS memory cache")
    
    def estimate_model_memory(
        self,
        num_parameters: int,
        batch_size: int = 1,
        sequence_length: int = 1024,
        dtype: torch.dtype = torch.float32,
        training: bool = True
    ) -> Dict[str, float]:
        """
        Estimate memory requirements for a model.
        
        Args:
            num_parameters: Number of model parameters
            batch_size: Batch size
            sequence_length: Sequence length
            dtype: Data type (affects memory usage)
            training: Whether estimating for training (includes gradients and optimizer)
            
        Returns:
            Dict[str, float]: Memory estimates in GB
        """
        # Bytes per parameter based on dtype
        bytes_per_param = {
            torch.float32: 4,
            torch.float16: 2,
            torch.bfloat16: 2,
            torch.int8: 1,
        }.get(dtype, 4)
        
        # Model parameters
        model_memory = num_parameters * bytes_per_param / (1024**3)
        
        # Activations (rough estimate)
        # Assume embedding dimension is sqrt(num_parameters / layers) for rough estimation
        estimated_hidden_size = max(512, int((num_parameters / 12) ** 0.5))  # Rough heuristic
        activation_memory = (batch_size * sequence_length * estimated_hidden_size * 
                           bytes_per_param * 12) / (1024**3)  # 12 layers assumption
        
        estimates = {
            'model_gb': model_memory,
            'activations_gb': activation_memory,
        }
        
        if training:
            # Gradients (same size as model)
            estimates['gradients_gb'] = model_memory
            
            # Optimizer states (Adam: 2x model size)
            estimates['optimizer_gb'] = model_memory * 2
            
            # Total training memory
            estimates['total_training_gb'] = (
                model_memory + activation_memory + model_memory + model_memory * 2
            )
        else:
            estimates['total_inference_gb'] = model_memory + activation_memory
        
        return estimates
    
    def check_memory_requirements(
        self,
        required_memory_gb: float,
        device: Optional[torch.device] = None,
        safety_margin: float = 0.1
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if device has sufficient memory for requirements.
        
        Args:
            required_memory_gb: Required memory in GB
            device: Device to check (defaults to optimal device)
            safety_margin: Safety margin as fraction of total memory
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (has_sufficient_memory, memory_info)
        """
        if device is None:
            device = self.get_optimal_device()
        
        memory_info = self.get_memory_info(device)
        
        if device.type == "cuda":
            available_memory = memory_info['free_gb']
            total_memory = memory_info['total_gb']
        elif device.type == "cpu":
            available_memory = memory_info['available_gb']
            total_memory = memory_info['total_gb']
        else:
            # Conservative estimate for other devices
            available_memory = 8.0  # Assume 8GB available
            total_memory = 16.0
        
        # Apply safety margin
        safe_available = available_memory * (1 - safety_margin)
        
        has_sufficient = required_memory_gb <= safe_available
        
        result_info = {
            'required_gb': required_memory_gb,
            'available_gb': available_memory,
            'safe_available_gb': safe_available,
            'total_gb': total_memory,
            'has_sufficient': has_sufficient,
            'utilization_percent': (required_memory_gb / total_memory) * 100,
            'device': str(device),
        }
        
        return has_sufficient, result_info
    
    def get_optimization_recommendations(
        self,
        device: Optional[torch.device] = None
    ) -> List[str]:
        """
        Get optimization recommendations for the current device.
        
        Args:
            device: Device to get recommendations for
            
        Returns:
            List[str]: List of optimization recommendations
        """
        if device is None:
            device = self.get_optimal_device()
        
        recommendations = []
        device_info = self.get_device_info()
        
        if device.type == "cuda":
            # CUDA-specific recommendations
            if device_info.get('cuda_device_count', 0) > 1:
                recommendations.append("Consider using DataParallel or DistributedDataParallel for multi-GPU training")
            
            # Check compute capability
            if device_info.get('cuda_devices'):
                compute_cap = device_info['cuda_devices'][0].get('compute_capability', '0.0')
                major_version = float(compute_cap.split('.')[0])
                
                if major_version >= 7.0:
                    recommendations.append("Use mixed precision training (fp16) for better performance")
                
                if major_version >= 8.0:
                    recommendations.append("Consider using bfloat16 for improved numerical stability")
            
            # Memory recommendations
            memory_info = self.get_memory_info(device)
            if memory_info['total_gb'] < 8:
                recommendations.append("Consider gradient checkpointing to reduce memory usage")
                recommendations.append("Use smaller batch sizes or gradient accumulation")
            
        elif device.type == "cpu":
            # CPU-specific recommendations
            cpu_count = device_info.get('cpu_count', 1)
            if isinstance(cpu_count, int) and cpu_count >= 8:
                recommendations.append(f"Set torch.set_num_threads({cpu_count}) for optimal CPU performance")
            
            recommendations.append("Consider using torch.jit.script for model optimization")
            recommendations.append("Use smaller models or quantization for CPU inference")
            
            # Memory recommendations
            memory_gb = device_info.get('memory_total_gb', 0)
            if isinstance(memory_gb, (int, float)) and memory_gb < 16:
                recommendations.append("Consider using smaller batch sizes due to limited RAM")
        
        elif device.type == "mps":
            # MPS-specific recommendations
            recommendations.append("Use mixed precision training if supported")
            recommendations.append("Monitor memory usage as MPS memory management differs from CUDA")
        
        return recommendations
    
    def validate_device_compatibility(self, device: torch.device) -> bool:
        """
        Validate that a device is compatible and available.
        
        Args:
            device: Device to validate
            
        Returns:
            bool: True if device is compatible
            
        Raises:
            DeviceError: If device is not compatible
        """
        if device.type == "cuda":
            if not torch.cuda.is_available():
                raise DeviceError(
                    "CUDA device requested but CUDA is not available",
                    device=str(device),
                    available_devices=["cpu"]
                )
            
            if device.index is not None and device.index >= torch.cuda.device_count():
                raise DeviceError(
                    f"CUDA device {device.index} requested but only {torch.cuda.device_count()} devices available",
                    device=str(device),
                    available_devices=[f"cuda:{i}" for i in range(torch.cuda.device_count())]
                )
        
        elif device.type == "mps":
            if not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
                raise DeviceError(
                    "MPS device requested but MPS is not available",
                    device=str(device),
                    available_devices=["cpu"] + (["cuda"] if torch.cuda.is_available() else [])
                )
        
        elif device.type not in ["cpu", "cuda", "mps"]:
            raise DeviceError(
                f"Unsupported device type: {device.type}",
                device=str(device),
                available_devices=["cpu"] + (["cuda"] if torch.cuda.is_available() else []) + 
                                (["mps"] if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else [])
            )
        
        return True


# Global device manager instance
_global_device_manager = DeviceManager()


def get_optimal_device(prefer_gpu: bool = True) -> torch.device:
    """
    Get the optimal device for computation.
    
    Args:
        prefer_gpu: Whether to prefer GPU over CPU
        
    Returns:
        torch.device: Optimal device
    """
    return _global_device_manager.get_optimal_device(prefer_gpu)


def get_device_info() -> Dict[str, Any]:
    """
    Get comprehensive device information.
    
    Returns:
        Dict[str, Any]: Device information
    """
    return _global_device_manager.get_device_info()


def get_memory_info(device: Optional[torch.device] = None) -> Dict[str, float]:
    """
    Get memory information for a device.
    
    Args:
        device: Device to get memory info for
        
    Returns:
        Dict[str, float]: Memory information in GB
    """
    return _global_device_manager.get_memory_info(device)


def clear_memory(device: Optional[torch.device] = None) -> None:
    """
    Clear memory caches for a device.
    
    Args:
        device: Device to clear memory for
    """
    _global_device_manager.clear_memory(device)


def estimate_model_memory(
    num_parameters: int,
    batch_size: int = 1,
    sequence_length: int = 1024,
    dtype: torch.dtype = torch.float32,
    training: bool = True
) -> Dict[str, float]:
    """
    Estimate memory requirements for a model.
    
    Args:
        num_parameters: Number of model parameters
        batch_size: Batch size
        sequence_length: Sequence length
        dtype: Data type
        training: Whether estimating for training
        
    Returns:
        Dict[str, float]: Memory estimates in GB
    """
    return _global_device_manager.estimate_model_memory(
        num_parameters, batch_size, sequence_length, dtype, training
    )


def check_memory_requirements(
    required_memory_gb: float,
    device: Optional[torch.device] = None,
    safety_margin: float = 0.1
) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if device has sufficient memory.
    
    Args:
        required_memory_gb: Required memory in GB
        device: Device to check
        safety_margin: Safety margin as fraction
        
    Returns:
        Tuple[bool, Dict[str, Any]]: (has_sufficient_memory, memory_info)
    """
    return _global_device_manager.check_memory_requirements(
        required_memory_gb, device, safety_margin
    )


def get_optimization_recommendations(device: Optional[torch.device] = None) -> List[str]:
    """
    Get optimization recommendations for a device.
    
    Args:
        device: Device to get recommendations for
        
    Returns:
        List[str]: Optimization recommendations
    """
    return _global_device_manager.get_optimization_recommendations(device)


def validate_device_compatibility(device: torch.device) -> bool:
    """
    Validate device compatibility.
    
    Args:
        device: Device to validate
        
    Returns:
        bool: True if compatible
    """
    return _global_device_manager.validate_device_compatibility(device)