"""
SGLBO Performance Optimization Utilities
========================================

This module provides performance optimization utilities specifically designed
for SGLBO operations, including GPU acceleration, memory management, parallel
processing, and computational efficiency enhancements.

Key Features:
- GPU acceleration for gradient computations
- Memory-efficient tensor operations
- Parallel gradient evaluation
- Caching strategies for repeated computations
- Batch processing optimizations
- Profiling and benchmarking tools
- Adaptive resource management

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0 - SGLBO Performance Optimization
"""

import logging
import time
import functools
import threading
from typing import Any, Dict, List, Optional, Tuple, Callable, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import warnings
import gc

import numpy as np
import torch
from torch import Tensor
import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceConfig:
    """Configuration for SGLBO performance optimizations."""
    # GPU settings
    use_gpu: bool = True
    gpu_memory_fraction: float = 0.8
    gpu_batch_size: int = 32
    
    # CPU settings
    max_cpu_threads: int = 4
    cpu_batch_size: int = 16
    
    # Memory management
    enable_memory_optimization: bool = True
    max_memory_usage_gb: float = 8.0
    garbage_collection_frequency: int = 100
    
    # Caching
    enable_caching: bool = True
    cache_size_limit: int = 10000
    cache_cleanup_frequency: int = 500
    
    # Profiling
    enable_profiling: bool = False
    profile_memory: bool = False
    profile_timing: bool = True


class GPUAccelerator:
    """GPU acceleration utilities for SGLBO computations."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.device = torch.device("cpu")
        self.gpu_available = False
        self.memory_pool = {}
        
        self._initialize_gpu()
        
    def _initialize_gpu(self):
        """Initialize GPU if available and configured."""
        try:
            if self.config.use_gpu and torch.cuda.is_available():
                self.device = torch.device("cuda")
                self.gpu_available = True
                
                # Set memory fraction
                if hasattr(torch.cuda, 'set_memory_fraction'):
                    torch.cuda.set_memory_fraction(self.config.gpu_memory_fraction)
                
                # Get GPU info
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
                
                logger.info(f"GPU acceleration enabled: {gpu_name}")
                logger.info(f"GPU memory: {gpu_memory:.1f} GB")
                
            else:
                logger.info("GPU acceleration disabled or not available")
                
        except Exception as e:
            logger.warning(f"Failed to initialize GPU: {e}")
            self.device = torch.device("cpu")
            self.gpu_available = False
    
    def to_device(self, tensor: Tensor, non_blocking: bool = True) -> Tensor:
        """Move tensor to optimal device."""
        try:
            if isinstance(tensor, torch.Tensor):
                return tensor.to(self.device, non_blocking=non_blocking)
            else:
                # Convert numpy array to tensor first
                if isinstance(tensor, np.ndarray):
                    tensor = torch.from_numpy(tensor)
                return tensor.to(self.device, non_blocking=non_blocking)
        except Exception as e:
            logger.warning(f"Failed to move tensor to device: {e}")
            return tensor
    
    def batch_process(self, data: List[Tensor], 
                     processing_func: Callable, 
                     batch_size: Optional[int] = None) -> List[Any]:
        """Process data in GPU-optimized batches."""
        try:
            if batch_size is None:
                batch_size = self.config.gpu_batch_size if self.gpu_available else self.config.cpu_batch_size
            
            results = []
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                
                # Move batch to device
                batch_gpu = [self.to_device(item) for item in batch]
                
                # Process batch
                with torch.no_grad():  # Disable gradient computation for efficiency
                    batch_results = processing_func(batch_gpu)
                    
                # Move results back to CPU if needed
                if isinstance(batch_results, list):
                    batch_results = [result.cpu() if isinstance(result, torch.Tensor) else result 
                                   for result in batch_results]
                elif isinstance(batch_results, torch.Tensor):
                    batch_results = batch_results.cpu()
                
                results.extend(batch_results if isinstance(batch_results, list) else [batch_results])
                
                # Clear GPU memory
                if self.gpu_available:
                    torch.cuda.empty_cache()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            # Fallback to CPU processing
            return [processing_func([item]) for item in data]
    
    def parallel_gradient_computation(self, points: List[np.ndarray],
                                    gradient_func: Callable) -> List[np.ndarray]:
        """Compute gradients in parallel with GPU acceleration."""
        try:
            # Convert to tensors and move to GPU
            points_tensors = [self.to_device(torch.from_numpy(point.astype(np.float32))) 
                            for point in points]
            
            # Define batch processing function
            def process_batch(batch_tensors):
                batch_gradients = []
                for tensor_point in batch_tensors:
                    try:
                        point_np = tensor_point.cpu().numpy()
                        gradient = gradient_func(point_np)
                        gradient_tensor = torch.from_numpy(gradient.astype(np.float32))
                        batch_gradients.append(self.to_device(gradient_tensor))
                    except Exception as e:
                        logger.warning(f"Error computing gradient: {e}")
                        batch_gradients.append(torch.zeros_like(tensor_point))
                return batch_gradients
            
            # Process in batches
            gradient_tensors = self.batch_process(points_tensors, process_batch)
            
            # Convert back to numpy arrays
            gradients = [tensor.cpu().numpy() if isinstance(tensor, torch.Tensor) else tensor 
                        for tensor in gradient_tensors]
            
            return gradients
            
        except Exception as e:
            logger.error(f"Error in parallel gradient computation: {e}")
            # Fallback to sequential computation
            return [gradient_func(point) for point in points]
    
    def cleanup(self):
        """Clean up GPU resources."""
        try:
            self.memory_pool.clear()
            if self.gpu_available:
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except Exception as e:
            logger.warning(f"Error during GPU cleanup: {e}")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get GPU memory information."""
        if not self.gpu_available:
            return {"gpu_available": False}
        
        try:
            allocated = torch.cuda.memory_allocated() / 1e9
            cached = torch.cuda.memory_reserved() / 1e9
            total = torch.cuda.get_device_properties(0).total_memory / 1e9
            
            return {
                "gpu_available": True,
                "allocated_gb": allocated,
                "cached_gb": cached,
                "total_gb": total,
                "utilization": (allocated / total) * 100
            }
        except Exception as e:
            logger.warning(f"Error getting GPU memory info: {e}")
            return {"gpu_available": True, "error": str(e)}


class MemoryManager:
    """Memory management utilities for SGLBO operations."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.operation_count = 0
        self.memory_usage_history = []
        
    def monitor_memory(self) -> Dict[str, float]:
        """Monitor current memory usage."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            usage = {
                "rss_gb": memory_info.rss / 1e9,  # Resident Set Size
                "vms_gb": memory_info.vms / 1e9,  # Virtual Memory Size
                "percent": process.memory_percent(),
                "available_gb": psutil.virtual_memory().available / 1e9
            }
            
            self.memory_usage_history.append(usage)
            
            # Keep limited history
            if len(self.memory_usage_history) > 1000:
                self.memory_usage_history = self.memory_usage_history[-500:]
            
            return usage
            
        except Exception as e:
            logger.warning(f"Error monitoring memory: {e}")
            return {}
    
    def check_memory_threshold(self) -> bool:
        """Check if memory usage exceeds threshold."""
        try:
            current_usage = self.monitor_memory()
            return current_usage.get("rss_gb", 0) > self.config.max_memory_usage_gb
        except Exception:
            return False
    
    def optimize_memory(self):
        """Perform memory optimization."""
        try:
            self.operation_count += 1
            
            # Periodic garbage collection
            if (self.config.enable_memory_optimization and 
                self.operation_count % self.config.garbage_collection_frequency == 0):
                
                logger.debug("Performing garbage collection")
                collected = gc.collect()
                
                if collected > 0:
                    logger.debug(f"Garbage collection freed {collected} objects")
            
            # Check memory threshold
            if self.check_memory_threshold():
                logger.warning("Memory usage high - performing intensive cleanup")
                self._intensive_cleanup()
                
        except Exception as e:
            logger.warning(f"Error in memory optimization: {e}")
    
    def _intensive_cleanup(self):
        """Perform intensive memory cleanup."""
        try:
            # Force garbage collection
            for i in range(3):
                gc.collect()
            
            # Clear unnecessary caches
            if hasattr(torch, 'cuda') and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("Intensive memory cleanup completed")
            
        except Exception as e:
            logger.warning(f"Error in intensive cleanup: {e}")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory usage summary."""
        try:
            current = self.monitor_memory()
            
            if self.memory_usage_history:
                peak_rss = max(usage["rss_gb"] for usage in self.memory_usage_history)
                avg_rss = np.mean([usage["rss_gb"] for usage in self.memory_usage_history])
            else:
                peak_rss = avg_rss = 0
            
            return {
                "current": current,
                "peak_rss_gb": peak_rss,
                "average_rss_gb": avg_rss,
                "threshold_gb": self.config.max_memory_usage_gb,
                "operations_monitored": self.operation_count
            }
            
        except Exception as e:
            logger.warning(f"Error getting memory summary: {e}")
            return {}


class ComputationCache:
    """Caching system for SGLBO computations."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.cache = {}
        self.access_counts = {}
        self.access_order = []
        self.operation_count = 0
        
    def _get_cache_key(self, x: np.ndarray, func_name: str = "") -> str:
        """Generate cache key for input."""
        try:
            # Round to avoid floating point precision issues
            x_rounded = np.round(x, decimals=8)
            key = f"{func_name}_{hash(x_rounded.tobytes())}"
            return key
        except Exception:
            return f"{func_name}_{id(x)}"
    
    def get_cached_result(self, x: np.ndarray, func_name: str = "") -> Optional[Any]:
        """Get cached result if available."""
        if not self.config.enable_caching:
            return None
        
        try:
            key = self._get_cache_key(x, func_name)
            
            if key in self.cache:
                # Update access tracking
                self.access_counts[key] = self.access_counts.get(key, 0) + 1
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                return self.cache[key]
            
        except Exception as e:
            logger.debug(f"Error accessing cache: {e}")
        
        return None
    
    def cache_result(self, x: np.ndarray, result: Any, func_name: str = ""):
        """Cache computation result."""
        if not self.config.enable_caching:
            return
        
        try:
            key = self._get_cache_key(x, func_name)
            
            # Check cache size limit
            if len(self.cache) >= self.config.cache_size_limit:
                self._evict_cache_entries()
            
            self.cache[key] = result
            self.access_counts[key] = 1
            self.access_order.append(key)
            
            # Periodic cleanup
            self.operation_count += 1
            if self.operation_count % self.config.cache_cleanup_frequency == 0:
                self._cleanup_cache()
                
        except Exception as e:
            logger.debug(f"Error caching result: {e}")
    
    def _evict_cache_entries(self):
        """Evict least recently used cache entries."""
        try:
            # Remove oldest 25% of entries
            num_to_remove = len(self.cache) // 4
            
            for _ in range(num_to_remove):
                if self.access_order:
                    key_to_remove = self.access_order.pop(0)
                    self.cache.pop(key_to_remove, None)
                    self.access_counts.pop(key_to_remove, None)
                    
        except Exception as e:
            logger.warning(f"Error evicting cache entries: {e}")
    
    def _cleanup_cache(self):
        """Clean up cache inconsistencies."""
        try:
            # Remove keys that exist in access tracking but not in cache
            cache_keys = set(self.cache.keys())
            access_keys = set(self.access_counts.keys())
            
            orphaned_keys = access_keys - cache_keys
            for key in orphaned_keys:
                self.access_counts.pop(key, None)
                if key in self.access_order:
                    self.access_order.remove(key)
                    
        except Exception as e:
            logger.warning(f"Error cleaning up cache: {e}")
    
    def clear_cache(self):
        """Clear all cache data."""
        self.cache.clear()
        self.access_counts.clear()
        self.access_order.clear()
        self.operation_count = 0
        
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.config.cache_size_limit,
            "total_accesses": sum(self.access_counts.values()),
            "unique_keys": len(self.access_counts),
            "operations": self.operation_count
        }


class ParallelProcessor:
    """Parallel processing utilities for SGLBO."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.thread_pool = None
        self.process_pool = None
        
    def _ensure_thread_pool(self):
        """Ensure thread pool is initialized."""
        if self.thread_pool is None:
            self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_cpu_threads)
    
    def parallel_function_evaluation(self, points: List[np.ndarray],
                                   func: Callable, use_processes: bool = False) -> List[Any]:
        """Evaluate function at multiple points in parallel."""
        try:
            if use_processes and len(points) > 10:
                # Use process pool for CPU-intensive tasks
                if self.process_pool is None:
                    self.process_pool = ProcessPoolExecutor(max_workers=self.config.max_cpu_threads)
                
                futures = [self.process_pool.submit(func, point) for point in points]
                results = [future.result() for future in futures]
                
            else:
                # Use thread pool for I/O or GPU tasks
                self._ensure_thread_pool()
                
                futures = [self.thread_pool.submit(func, point) for point in points]
                results = [future.result() for future in futures]
            
            return results
            
        except Exception as e:
            logger.error(f"Error in parallel function evaluation: {e}")
            # Fallback to sequential processing
            return [func(point) for point in points]
    
    def parallel_gradient_computation(self, points: List[np.ndarray], 
                                    gradient_func: Callable) -> List[np.ndarray]:
        """Compute gradients in parallel."""
        return self.parallel_function_evaluation(points, gradient_func, use_processes=True)
    
    def cleanup(self):
        """Clean up parallel processing resources."""
        try:
            if self.thread_pool is not None:
                self.thread_pool.shutdown(wait=True)
                self.thread_pool = None
                
            if self.process_pool is not None:
                self.process_pool.shutdown(wait=True)
                self.process_pool = None
                
        except Exception as e:
            logger.warning(f"Error during parallel processor cleanup: {e}")


class PerformanceProfiler:
    """Performance profiling utilities for SGLBO."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.timing_data = {}
        self.memory_data = {}
        self.enabled = config.enable_profiling
        
    def time_operation(self, operation_name: str):
        """Decorator for timing operations."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                start_time = time.time()
                start_memory = None
                
                if self.config.profile_memory:
                    start_memory = psutil.Process().memory_info().rss
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Record timing
                    if self.config.profile_timing:
                        execution_time = time.time() - start_time
                        if operation_name not in self.timing_data:
                            self.timing_data[operation_name] = []
                        self.timing_data[operation_name].append(execution_time)
                    
                    # Record memory
                    if self.config.profile_memory and start_memory is not None:
                        end_memory = psutil.Process().memory_info().rss
                        memory_delta = end_memory - start_memory
                        if operation_name not in self.memory_data:
                            self.memory_data[operation_name] = []
                        self.memory_data[operation_name].append(memory_delta)
                    
                    return result
                    
                except Exception as e:
                    # Still record timing even on failure
                    if self.config.profile_timing:
                        execution_time = time.time() - start_time
                        if operation_name not in self.timing_data:
                            self.timing_data[operation_name] = []
                        self.timing_data[operation_name].append(execution_time)
                    raise
                    
            return wrapper
        return decorator
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance profiling summary."""
        summary = {
            "timing_stats": {},
            "memory_stats": {},
            "enabled": self.enabled
        }
        
        # Timing statistics
        for operation, times in self.timing_data.items():
            if times:
                summary["timing_stats"][operation] = {
                    "calls": len(times),
                    "total_time": sum(times),
                    "average_time": np.mean(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "std_time": np.std(times)
                }
        
        # Memory statistics
        for operation, memory_deltas in self.memory_data.items():
            if memory_deltas:
                summary["memory_stats"][operation] = {
                    "calls": len(memory_deltas),
                    "total_memory_delta": sum(memory_deltas),
                    "average_memory_delta": np.mean(memory_deltas),
                    "max_memory_delta": max(memory_deltas)
                }
        
        return summary
    
    def reset_profiling_data(self):
        """Reset all profiling data."""
        self.timing_data.clear()
        self.memory_data.clear()


class SGLBOPerformanceManager:
    """Main performance manager for SGLBO operations."""
    
    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or PerformanceConfig()
        
        # Initialize components
        self.gpu_accelerator = GPUAccelerator(self.config)
        self.memory_manager = MemoryManager(self.config)
        self.cache = ComputationCache(self.config)
        self.parallel_processor = ParallelProcessor(self.config)
        self.profiler = PerformanceProfiler(self.config)
        
        logger.info("SGLBO Performance Manager initialized")
        logger.info(f"  GPU available: {self.gpu_accelerator.gpu_available}")
        logger.info(f"  CPU threads: {self.config.max_cpu_threads}")
        logger.info(f"  Caching enabled: {self.config.enable_caching}")
        
    def optimize_gradient_computation(self, points: List[np.ndarray],
                                    gradient_func: Callable) -> List[np.ndarray]:
        """Optimized gradient computation with caching and acceleration."""
        
        @self.profiler.time_operation("gradient_computation")
        def compute_gradients():
            results = []
            uncached_points = []
            uncached_indices = []
            
            # Check cache for each point
            for i, point in enumerate(points):
                cached_result = self.cache.get_cached_result(point, "gradient")
                if cached_result is not None:
                    results.append((i, cached_result))
                else:
                    uncached_points.append(point)
                    uncached_indices.append(i)
            
            # Compute uncached gradients
            if uncached_points:
                if self.gpu_accelerator.gpu_available and len(uncached_points) > 5:
                    # Use GPU acceleration for large batches
                    uncached_gradients = self.gpu_accelerator.parallel_gradient_computation(
                        uncached_points, gradient_func
                    )
                elif len(uncached_points) > 2:
                    # Use parallel CPU processing
                    uncached_gradients = self.parallel_processor.parallel_gradient_computation(
                        uncached_points, gradient_func
                    )
                else:
                    # Sequential processing for small batches
                    uncached_gradients = [gradient_func(point) for point in uncached_points]
                
                # Cache results and add to results list
                for point, gradient, idx in zip(uncached_points, uncached_gradients, uncached_indices):
                    self.cache.cache_result(point, gradient, "gradient")
                    results.append((idx, gradient))
            
            # Sort results by original index
            results.sort(key=lambda x: x[0])
            final_results = [result[1] for result in results]
            
            # Memory optimization
            self.memory_manager.optimize_memory()
            
            return final_results
        
        return compute_gradients()
    
    def optimize_function_evaluation(self, points: List[np.ndarray],
                                   func: Callable, use_cache: bool = True) -> List[Any]:
        """Optimized function evaluation with performance enhancements."""
        
        @self.profiler.time_operation("function_evaluation")
        def evaluate_functions():
            results = []
            uncached_points = []
            uncached_indices = []
            
            if use_cache:
                # Check cache
                for i, point in enumerate(points):
                    cached_result = self.cache.get_cached_result(point, "function")
                    if cached_result is not None:
                        results.append((i, cached_result))
                    else:
                        uncached_points.append(point)
                        uncached_indices.append(i)
            else:
                uncached_points = points
                uncached_indices = list(range(len(points)))
            
            # Evaluate uncached points
            if uncached_points:
                if len(uncached_points) > 3:
                    # Use parallel processing
                    uncached_results = self.parallel_processor.parallel_function_evaluation(
                        uncached_points, func, use_processes=False
                    )
                else:
                    # Sequential processing
                    uncached_results = [func(point) for point in uncached_points]
                
                # Cache and collect results
                for point, result, idx in zip(uncached_points, uncached_results, uncached_indices):
                    if use_cache:
                        self.cache.cache_result(point, result, "function")
                    results.append((idx, result))
            
            # Sort and extract final results
            results.sort(key=lambda x: x[0])
            final_results = [result[1] for result in results]
            
            return final_results
        
        return evaluate_functions()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        try:
            return {
                "gpu_info": self.gpu_accelerator.get_memory_info(),
                "memory_summary": self.memory_manager.get_memory_summary(),
                "cache_stats": self.cache.get_cache_stats(),
                "profiling_data": self.profiler.get_performance_summary(),
                "configuration": {
                    "gpu_enabled": self.config.use_gpu,
                    "max_cpu_threads": self.config.max_cpu_threads,
                    "caching_enabled": self.config.enable_caching,
                    "memory_optimization": self.config.enable_memory_optimization
                }
            }
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}
    
    def cleanup(self):
        """Clean up all performance manager resources."""
        try:
            logger.info("Cleaning up SGLBO Performance Manager")
            
            self.gpu_accelerator.cleanup()
            self.cache.clear_cache()
            self.parallel_processor.cleanup()
            
            # Final memory cleanup
            self.memory_manager._intensive_cleanup()
            
            logger.info("Performance Manager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during performance manager cleanup: {e}")
    
    def reset_performance_data(self):
        """Reset all performance tracking data."""
        self.cache.clear_cache()
        self.profiler.reset_profiling_data()
        self.memory_manager.memory_usage_history.clear()
        self.memory_manager.operation_count = 0