"""
Device Manager Module for Jal-Drishti ML Engine
================================================
Cross-Vendor GPU Compatibility Layer

This module provides a single source of truth for device selection,
implementing runtime detection with graceful fallback.

Design Principles:
1. Single Codebase, Multiple Devices (No vendor-specific forks)
2. Runtime Detection, Not Assumptions
3. Performance Is Conditional, Correctness Is Mandatory
4. Fail Gracefully, Never Hard-Fail

Priority Order:
1. CUDA (NVIDIA + AMD ROCm)
2. MPS (Apple Silicon)
3. XPU (Intel Arc)
4. CPU (Fallback - always works)
"""

import logging
from typing import Tuple, Optional
from dataclasses import dataclass

import torch

logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """Container for device configuration and capabilities."""
    device: torch.device
    device_type: str  # 'cuda', 'mps', 'xpu', 'cpu'
    device_name: str  # Human-readable name
    fp16_supported: bool
    memory_gb: Optional[float]  # GPU memory in GB, None for CPU


class DeviceManager:
    """
    Centralized device resolution and management.
    
    This class should be the ONLY place where device selection logic exists.
    All model loading and tensor transfers should reference this manager.
    
    Usage:
        manager = DeviceManager()
        device_info = manager.get_device_info()
        model.to(device_info.device)
    """
    
    _instance: Optional['DeviceManager'] = None
    _device_info: Optional[DeviceInfo] = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern - one device manager per process."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, force_cpu: bool = False):
        """
        Initialize device manager with optional CPU-only mode.
        
        Args:
            force_cpu: If True, skip all GPU detection and use CPU.
                       Useful for testing fallback behavior.
        """
        if self._device_info is None:
            self._device_info = self._detect_best_device(force_cpu)
            self._log_device_info()
    
    def _detect_best_device(self, force_cpu: bool = False) -> DeviceInfo:
        """
        Detect and return the best available compute device.
        
        Priority order (per implementation plan):
        1. CUDA (covers NVIDIA + AMD ROCm transparently)
        2. Apple MPS
        3. Intel XPU
        4. CPU (fallback)
        
        Returns:
            DeviceInfo with selected device and capabilities
        """
        if force_cpu:
            logger.info("[DeviceManager] Force CPU mode enabled")
            return self._create_cpu_device_info()
        
        # Priority 1: CUDA (NVIDIA or AMD ROCm)
        if torch.cuda.is_available():
            return self._create_cuda_device_info()
        
        # Priority 2: Apple MPS (Metal Performance Shaders)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return self._create_mps_device_info()
        
        # Priority 3: Intel XPU
        try:
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
                return self._create_xpu_device_info()
        except AttributeError:
            pass  # XPU not available in this PyTorch build
        
        # Priority 4: CPU Fallback
        logger.warning("[DeviceManager] No GPU detected. Falling back to CPU.")
        logger.warning("[DeviceManager] Performance will be significantly reduced.")
        return self._create_cpu_device_info()
    
    def _create_cuda_device_info(self) -> DeviceInfo:
        """Create DeviceInfo for CUDA device."""
        device = torch.device("cuda")
        device_name = torch.cuda.get_device_name(0)
        memory_bytes = torch.cuda.get_device_properties(0).total_memory
        memory_gb = memory_bytes / (1024 ** 3)
        
        return DeviceInfo(
            device=device,
            device_type="cuda",
            device_name=device_name,
            fp16_supported=True,  # CUDA fully supports FP16
            memory_gb=round(memory_gb, 2)
        )
    
    def _create_mps_device_info(self) -> DeviceInfo:
        """Create DeviceInfo for Apple MPS device."""
        device = torch.device("mps")
        
        return DeviceInfo(
            device=device,
            device_type="mps",
            device_name="Apple Silicon (MPS)",
            fp16_supported=False,  # MPS FP16 is unstable per plan
            memory_gb=None  # Unified memory, not easily queryable
        )
    
    def _create_xpu_device_info(self) -> DeviceInfo:
        """Create DeviceInfo for Intel XPU device."""
        device = torch.device("xpu")
        
        # Intel XPU device name detection
        try:
            device_name = torch.xpu.get_device_name(0)
        except Exception:
            device_name = "Intel XPU"
        
        return DeviceInfo(
            device=device,
            device_type="xpu",
            device_name=device_name,
            fp16_supported=False,  # XPU FP16 is inconsistent per plan
            memory_gb=None
        )
    
    def _create_cpu_device_info(self) -> DeviceInfo:
        """Create DeviceInfo for CPU fallback."""
        import platform
        cpu_name = platform.processor() or "Unknown CPU"
        
        return DeviceInfo(
            device=torch.device("cpu"),
            device_type="cpu",
            device_name=cpu_name,
            fp16_supported=False,  # CPU should use FP32
            memory_gb=None
        )
    
    def _log_device_info(self):
        """Log comprehensive device information at startup."""
        info = self._device_info
        
        logger.info("=" * 60)
        logger.info("[DeviceManager] Device Configuration")
        logger.info("=" * 60)
        logger.info(f"  Device Type:    {info.device_type.upper()}")
        logger.info(f"  Device Name:    {info.device_name}")
        logger.info(f"  FP16 Enabled:   {info.fp16_supported}")
        
        if info.memory_gb is not None:
            logger.info(f"  GPU Memory:     {info.memory_gb:.2f} GB")
        
        if info.device_type == "cpu":
            logger.warning("  [!] CPU Mode: Expect significant latency increase")
        elif not info.fp16_supported:
            logger.info("  [!] FP32 Mode: Using full precision for stability")
        else:
            logger.info("  [✓] GPU Acceleration with FP16 enabled")
        
        logger.info("=" * 60)
    
    def get_device_info(self) -> DeviceInfo:
        """
        Get the current device configuration.
        
        Returns:
            DeviceInfo containing device and capabilities
        """
        return self._device_info
    
    def get_device(self) -> torch.device:
        """
        Get the torch.device object directly.
        
        Convenience method for common use case.
        
        Returns:
            torch.device for the selected compute backend
        """
        return self._device_info.device
    
    def is_fp16_enabled(self) -> bool:
        """
        Check if FP16 inference is safe for current device.
        
        Returns:
            True only if device fully supports FP16
        """
        return self._device_info.fp16_supported
    
    def get_device_type(self) -> str:
        """
        Get the device type string.
        
        Returns:
            One of: 'cuda', 'mps', 'xpu', 'cpu'
        """
        return self._device_info.device_type
    
    @classmethod
    def reset(cls):
        """
        Reset the singleton instance.
        
        Useful for testing or reinitializing with different settings.
        """
        cls._instance = None
        cls._device_info = None


# Convenience functions for simpler API
def get_device_manager(force_cpu: bool = False) -> DeviceManager:
    """Get or create the device manager singleton."""
    manager = DeviceManager()
    if force_cpu and manager._device_info.device_type != "cpu":
        DeviceManager.reset()
        return DeviceManager(force_cpu=True)
    return manager


def get_best_device() -> torch.device:
    """Get the best available device directly."""
    return get_device_manager().get_device()


def is_fp16_supported() -> bool:
    """Check if FP16 is safe for the current device."""
    return get_device_manager().is_fp16_enabled()
