"""Resource management strategies for large datasets and memory usage."""

import os
import psutil
import threading
import time
import gc
import weakref
from typing import Any, Dict, List, Optional, Callable, Iterator, Tuple
from dataclasses import dataclass
from pathlib import Path
from contextlib import contextmanager
from functools import lru_cache
import logging

from utils.error_handling import MemoryError, ErrorContext, handle_error


@dataclass
class ResourceLimits:
    """Resource limits configuration."""
    max_memory_mb: int = 1024  # 1GB default
    max_file_size_mb: int = 100  # 100MB default
    max_concurrent_operations: int = 4
    cache_size_mb: int = 256  # 256MB default
    temp_cleanup_age_hours: int = 24


@dataclass
class ResourceUsage:
    """Current resource usage information."""
    memory_mb: float
    cpu_percent: float
    disk_usage_mb: float
    active_operations: int
    cache_size_mb: float
    temp_files_count: int


class MemoryMonitor:
    """Monitor and manage memory usage."""
    
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.logger = logging.getLogger(__name__)
        self._monitoring = False
        self._monitor_thread = None
        self._callbacks = []
        self._tracked_objects = weakref.WeakSet()
    
    def start_monitoring(self, interval: float = 5.0):
        """Start memory monitoring."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        self.logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop memory monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        self.logger.info("Memory monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Memory monitoring loop."""
        while self._monitoring:
            try:
                usage = self.get_memory_usage()
                
                # Check if memory usage exceeds limits
                if usage > self.limits.max_memory_mb:
                    self._handle_memory_pressure(usage)
                
                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(usage)
                    except Exception as e:
                        self.logger.error(f"Memory monitor callback failed: {e}")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                time.sleep(interval)
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss / (1024 * 1024)  # Convert to MB
    
    def get_system_memory_info(self) -> Dict[str, float]:
        """Get system memory information."""
        memory = psutil.virtual_memory()
        return {
            'total_mb': memory.total / (1024 * 1024),
            'available_mb': memory.available / (1024 * 1024),
            'used_mb': memory.used / (1024 * 1024),
            'percent': memory.percent
        }
    
    def _handle_memory_pressure(self, current_usage: float):
        """Handle memory pressure situation."""
        self.logger.warning(f"Memory usage ({current_usage:.1f}MB) exceeds limit ({self.limits.max_memory_mb}MB)")
        
        # Try garbage collection first
        collected = gc.collect()
        self.logger.info(f"Garbage collection freed {collected} objects")
        
        # Check usage after GC
        new_usage = self.get_memory_usage()
        if new_usage < self.limits.max_memory_mb:
            self.logger.info(f"Memory usage reduced to {new_usage:.1f}MB after GC")
            return
        
        # Clear caches if still over limit
        self._clear_caches()
        
        # Final check
        final_usage = self.get_memory_usage()
        if final_usage >= self.limits.max_memory_mb:
            # Raise memory error
            context = ErrorContext(
                operation="memory_monitoring",
                component="resource_manager"
            )
            error = MemoryError(
                f"Memory usage ({final_usage:.1f}MB) exceeds limit ({self.limits.max_memory_mb}MB)",
                memory_usage=int(final_usage * 1024 * 1024),
                context=context
            )
            handle_error(error, suppress=True)
    
    def _clear_caches(self):
        """Clear application caches to free memory."""
        # Clear function caches
        for obj in gc.get_objects():
            if hasattr(obj, 'cache_clear') and callable(obj.cache_clear):
                try:
                    obj.cache_clear()
                except Exception:
                    pass
        
        self.logger.info("Cleared application caches")
    
    def add_callback(self, callback: Callable[[float], None]):
        """Add memory usage callback."""
        self._callbacks.append(callback)
    
    def track_object(self, obj: Any):
        """Track an object for memory monitoring."""
        self._tracked_objects.add(obj)
    
    def get_tracked_objects_count(self) -> int:
        """Get count of tracked objects."""
        return len(self._tracked_objects)


class FileManager:
    """Manage file operations and large file handling."""
    
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.logger = logging.getLogger(__name__)
        self._temp_files = set()
        self._file_locks = {}
        self._lock = threading.Lock()
    
    def validate_file_size(self, filepath: str) -> bool:
        """Validate file size against limits."""
        try:
            file_size = Path(filepath).stat().st_size
            size_mb = file_size / (1024 * 1024)
            
            if size_mb > self.limits.max_file_size_mb:
                context = ErrorContext(
                    operation="file_validation",
                    component="file_manager",
                    additional_data={'filepath': filepath, 'size_mb': size_mb}
                )
                from utils.error_handling import FileSystemError
                raise FileSystemError(
                    f"File size ({size_mb:.1f}MB) exceeds limit ({self.limits.max_file_size_mb}MB)",
                    filepath=filepath,
                    operation="size_check",
                    context=context
                )
            
            return True
            
        except OSError as e:
            context = ErrorContext(
                operation="file_validation",
                component="file_manager"
            )
            from utils.error_handling import FileSystemError
            raise FileSystemError(
                f"Cannot access file: {e}",
                filepath=filepath,
                operation="access_check",
                context=context
            )
    
    def stream_large_file(self, filepath: str, chunk_size: int = 8192) -> Iterator[bytes]:
        """Stream large file in chunks to avoid memory issues."""
        self.validate_file_size(filepath)
        
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
                    
        except IOError as e:
            context = ErrorContext(
                operation="file_streaming",
                component="file_manager"
            )
            from utils.error_handling import FileSystemError
            raise FileSystemError(
                f"Error streaming file: {e}",
                filepath=filepath,
                operation="stream",
                context=context
            )
    
    def read_file_lines(self, filepath: str, max_lines: Optional[int] = None) -> Iterator[str]:
        """Read file lines with optional limit."""
        self.validate_file_size(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if max_lines and i >= max_lines:
                        break
                    yield line.rstrip('\n\r')
                    
        except IOError as e:
            context = ErrorContext(
                operation="file_reading",
                component="file_manager"
            )
            from utils.error_handling import FileSystemError
            raise FileSystemError(
                f"Error reading file: {e}",
                filepath=filepath,
                operation="read",
                context=context
            )
    
    def create_temp_file(self, suffix: str = '.tmp', prefix: str = 'genestudio_') -> str:
        """Create a temporary file and track it for cleanup."""
        import tempfile
        
        fd, filepath = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(fd)  # Close file descriptor, keep file
        
        with self._lock:
            self._temp_files.add(filepath)
        
        self.logger.debug(f"Created temporary file: {filepath}")
        return filepath
    
    def cleanup_temp_files(self, max_age_hours: Optional[int] = None):
        """Clean up temporary files."""
        if max_age_hours is None:
            max_age_hours = self.limits.temp_cleanup_age_hours
        
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        cleaned_count = 0
        
        with self._lock:
            files_to_remove = set()
            
            for filepath in self._temp_files:
                try:
                    if Path(filepath).exists():
                        file_age = current_time - Path(filepath).stat().st_mtime
                        if file_age > max_age_seconds:
                            os.unlink(filepath)
                            files_to_remove.add(filepath)
                            cleaned_count += 1
                    else:
                        # File already deleted
                        files_to_remove.add(filepath)
                        
                except Exception as e:
                    self.logger.warning(f"Error cleaning temp file {filepath}: {e}")
            
            # Remove from tracking
            self._temp_files -= files_to_remove
        
        self.logger.info(f"Cleaned up {cleaned_count} temporary files")
        return cleaned_count
    
    def get_temp_files_info(self) -> Dict[str, Any]:
        """Get information about temporary files."""
        with self._lock:
            total_size = 0
            existing_count = 0
            
            for filepath in self._temp_files:
                try:
                    if Path(filepath).exists():
                        total_size += Path(filepath).stat().st_size
                        existing_count += 1
                except Exception:
                    pass
            
            return {
                'total_tracked': len(self._temp_files),
                'existing_count': existing_count,
                'total_size_mb': total_size / (1024 * 1024)
            }


class OperationManager:
    """Manage concurrent operations and resource allocation."""
    
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.logger = logging.getLogger(__name__)
        self._active_operations = {}
        self._operation_counter = 0
        self._lock = threading.Lock()
        self._semaphore = threading.Semaphore(limits.max_concurrent_operations)
    
    @contextmanager
    def operation(self, name: str, description: str = ""):
        """Context manager for tracking operations."""
        operation_id = None
        
        try:
            # Acquire semaphore (blocks if at limit)
            self._semaphore.acquire()
            
            # Register operation
            with self._lock:
                self._operation_counter += 1
                operation_id = self._operation_counter
                
                self._active_operations[operation_id] = {
                    'name': name,
                    'description': description,
                    'start_time': time.time(),
                    'thread_id': threading.get_ident()
                }
            
            self.logger.info(f"Started operation {operation_id}: {name}")
            yield operation_id
            
        finally:
            # Clean up operation
            if operation_id:
                with self._lock:
                    if operation_id in self._active_operations:
                        operation = self._active_operations.pop(operation_id)
                        duration = time.time() - operation['start_time']
                        self.logger.info(f"Completed operation {operation_id}: {name} in {duration:.2f}s")
            
            # Release semaphore
            self._semaphore.release()
    
    def get_active_operations(self) -> Dict[int, Dict[str, Any]]:
        """Get information about active operations."""
        with self._lock:
            current_time = time.time()
            operations = {}
            
            for op_id, op_info in self._active_operations.items():
                operations[op_id] = {
                    **op_info,
                    'duration': current_time - op_info['start_time']
                }
            
            return operations
    
    def get_operation_count(self) -> int:
        """Get count of active operations."""
        with self._lock:
            return len(self._active_operations)
    
    def wait_for_operations(self, timeout: Optional[float] = None) -> bool:
        """Wait for all operations to complete."""
        start_time = time.time()
        
        while self.get_operation_count() > 0:
            if timeout and (time.time() - start_time) > timeout:
                return False
            time.sleep(0.1)
        
        return True


class CacheManager:
    """Manage application caches with size limits."""
    
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.logger = logging.getLogger(__name__)
        self._caches = {}
        self._cache_sizes = {}
        self._lock = threading.Lock()
    
    def register_cache(self, name: str, cache_obj: Any, size_estimator: Callable[[Any], int]):
        """Register a cache for management."""
        with self._lock:
            self._caches[name] = {
                'cache': cache_obj,
                'size_estimator': size_estimator
            }
            self._update_cache_size(name)
    
    def _update_cache_size(self, name: str):
        """Update cache size estimate."""
        if name in self._caches:
            cache_info = self._caches[name]
            try:
                size = cache_info['size_estimator'](cache_info['cache'])
                self._cache_sizes[name] = size
            except Exception as e:
                self.logger.warning(f"Error estimating cache size for {name}: {e}")
                self._cache_sizes[name] = 0
    
    def get_total_cache_size(self) -> int:
        """Get total cache size in bytes."""
        with self._lock:
            # Update all cache sizes
            for name in self._caches:
                self._update_cache_size(name)
            
            return sum(self._cache_sizes.values())
    
    def clear_cache(self, name: str) -> bool:
        """Clear a specific cache."""
        with self._lock:
            if name in self._caches:
                cache_obj = self._caches[name]['cache']
                try:
                    if hasattr(cache_obj, 'clear'):
                        cache_obj.clear()
                    elif hasattr(cache_obj, 'cache_clear'):
                        cache_obj.cache_clear()
                    
                    self._cache_sizes[name] = 0
                    self.logger.info(f"Cleared cache: {name}")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Error clearing cache {name}: {e}")
        
        return False
    
    def clear_all_caches(self):
        """Clear all registered caches."""
        with self._lock:
            cleared_count = 0
            for name in list(self._caches.keys()):
                if self.clear_cache(name):
                    cleared_count += 1
            
            self.logger.info(f"Cleared {cleared_count} caches")
    
    def enforce_cache_limits(self):
        """Enforce cache size limits."""
        total_size_mb = self.get_total_cache_size() / (1024 * 1024)
        
        if total_size_mb > self.limits.cache_size_mb:
            self.logger.warning(f"Cache size ({total_size_mb:.1f}MB) exceeds limit ({self.limits.cache_size_mb}MB)")
            
            # Clear caches starting with largest
            with self._lock:
                sorted_caches = sorted(
                    self._cache_sizes.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for name, size in sorted_caches:
                    if self.get_total_cache_size() / (1024 * 1024) <= self.limits.cache_size_mb:
                        break
                    
                    self.clear_cache(name)
                    self.logger.info(f"Cleared cache {name} ({size / (1024 * 1024):.1f}MB)")


class ResourceManager:
    """Main resource manager coordinating all resource management."""
    
    def __init__(self, limits: Optional[ResourceLimits] = None):
        self.limits = limits or ResourceLimits()
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.memory_monitor = MemoryMonitor(self.limits)
        self.file_manager = FileManager(self.limits)
        self.operation_manager = OperationManager(self.limits)
        self.cache_manager = CacheManager(self.limits)
        
        # Start monitoring
        self.memory_monitor.start_monitoring()
        
        # Setup cleanup timer
        self._cleanup_timer = None
        self._start_cleanup_timer()
    
    def _start_cleanup_timer(self):
        """Start periodic cleanup timer."""
        def cleanup_task():
            try:
                self.cleanup_resources()
            except Exception as e:
                self.logger.error(f"Resource cleanup error: {e}")
            finally:
                # Schedule next cleanup
                self._cleanup_timer = threading.Timer(3600, cleanup_task)  # Every hour
                self._cleanup_timer.daemon = True
                self._cleanup_timer.start()
        
        self._cleanup_timer = threading.Timer(3600, cleanup_task)  # First cleanup in 1 hour
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def cleanup_resources(self):
        """Perform resource cleanup."""
        self.logger.info("Starting resource cleanup")
        
        # Clean temporary files
        temp_cleaned = self.file_manager.cleanup_temp_files()
        
        # Enforce cache limits
        self.cache_manager.enforce_cache_limits()
        
        # Force garbage collection
        collected = gc.collect()
        
        self.logger.info(f"Resource cleanup completed: {temp_cleaned} temp files, {collected} objects collected")
    
    def get_resource_usage(self) -> ResourceUsage:
        """Get current resource usage."""
        memory_mb = self.memory_monitor.get_memory_usage()
        
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Get disk usage for temp files
        temp_info = self.file_manager.get_temp_files_info()
        
        # Get cache size
        cache_size_mb = self.cache_manager.get_total_cache_size() / (1024 * 1024)
        
        return ResourceUsage(
            memory_mb=memory_mb,
            cpu_percent=cpu_percent,
            disk_usage_mb=temp_info['total_size_mb'],
            active_operations=self.operation_manager.get_operation_count(),
            cache_size_mb=cache_size_mb,
            temp_files_count=temp_info['existing_count']
        )
    
    def check_resource_limits(self) -> List[str]:
        """Check if any resource limits are exceeded."""
        usage = self.get_resource_usage()
        violations = []
        
        if usage.memory_mb > self.limits.max_memory_mb:
            violations.append(f"Memory usage ({usage.memory_mb:.1f}MB) exceeds limit ({self.limits.max_memory_mb}MB)")
        
        if usage.cache_size_mb > self.limits.cache_size_mb:
            violations.append(f"Cache size ({usage.cache_size_mb:.1f}MB) exceeds limit ({self.limits.cache_size_mb}MB)")
        
        if usage.active_operations >= self.limits.max_concurrent_operations:
            violations.append(f"Active operations ({usage.active_operations}) at limit ({self.limits.max_concurrent_operations})")
        
        return violations
    
    def shutdown(self):
        """Shutdown resource manager."""
        self.logger.info("Shutting down resource manager")
        
        # Stop monitoring
        self.memory_monitor.stop_monitoring()
        
        # Cancel cleanup timer
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        
        # Wait for operations to complete
        self.operation_manager.wait_for_operations(timeout=30.0)
        
        # Final cleanup
        self.cleanup_resources()


# Global resource manager instance
_resource_manager = None


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


def with_resource_management(operation_name: str, description: str = ""):
    """Decorator for resource-managed operations."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            manager = get_resource_manager()
            with manager.operation_manager.operation(operation_name, description):
                return func(*args, **kwargs)
        return wrapper
    return decorator


@contextmanager
def managed_operation(name: str, description: str = ""):
    """Context manager for resource-managed operations."""
    manager = get_resource_manager()
    with manager.operation_manager.operation(name, description) as op_id:
        yield op_id