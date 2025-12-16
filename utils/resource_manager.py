"""Resource management and monitoring utilities."""

import psutil
import gc
import threading
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import weakref
from utils.logger import get_logger


@dataclass
class ResourceSnapshot:
    """Snapshot of system resource usage."""
    timestamp: datetime
    memory_mb: float
    memory_percent: float
    cpu_percent: float
    disk_usage_percent: float
    thread_count: int
    file_descriptors: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'memory_mb': self.memory_mb,
            'memory_percent': self.memory_percent,
            'cpu_percent': self.cpu_percent,
            'disk_usage_percent': self.disk_usage_percent,
            'thread_count': self.thread_count,
            'file_descriptors': self.file_descriptors
        }


@dataclass
class ResourceThresholds:
    """Resource usage thresholds for warnings."""
    memory_mb: float = 1000.0  # 1GB
    memory_percent: float = 80.0  # 80%
    cpu_percent: float = 80.0  # 80%
    disk_usage_percent: float = 90.0  # 90%
    thread_count: int = 100
    file_descriptors: int = 1000


class ResourceMonitor:
    """Monitors system resource usage and provides warnings."""
    
    def __init__(self, 
                 thresholds: Optional[ResourceThresholds] = None,
                 monitoring_interval: float = 5.0):
        """
        Initialize resource monitor.
        
        Args:
            thresholds: Resource thresholds for warnings
            monitoring_interval: Monitoring interval in seconds
        """
        self.thresholds = thresholds or ResourceThresholds()
        self.monitoring_interval = monitoring_interval
        self.logger = get_logger(self.__class__.__name__)
        
        self.process = psutil.Process()
        self.snapshots: List[ResourceSnapshot] = []
        self.max_snapshots = 100  # Keep last 100 snapshots
        
        self._monitoring = False
        self._monitor_thread = None
        self._lock = threading.Lock()
        
        # Callbacks for resource warnings
        self._warning_callbacks: List[Callable[[str, ResourceSnapshot], None]] = []
        
        # Track resource peaks
        self.peak_memory_mb = 0.0
        self.peak_cpu_percent = 0.0
        self.peak_thread_count = 0
    
    def start_monitoring(self):
        """Start continuous resource monitoring."""
        with self._lock:
            if self._monitoring:
                return
            
            self._monitoring = True
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="ResourceMonitor"
            )
            self._monitor_thread.start()
            
            self.logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring."""
        with self._lock:
            if not self._monitoring:
                return
            
            self._monitoring = False
            
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=1.0)
            
            self.logger.info("Resource monitoring stopped")
    
    def get_current_snapshot(self) -> ResourceSnapshot:
        """Get current resource usage snapshot."""
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            memory_percent = self.process.memory_percent()
            cpu_percent = self.process.cpu_percent()
            
            # System-wide disk usage
            disk_usage = psutil.disk_usage('/')
            disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            thread_count = self.process.num_threads()
            
            # File descriptors (Unix-like systems)
            try:
                file_descriptors = self.process.num_fds()
            except (AttributeError, psutil.AccessDenied):
                file_descriptors = 0
            
            snapshot = ResourceSnapshot(
                timestamp=datetime.now(),
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                cpu_percent=cpu_percent,
                disk_usage_percent=disk_usage_percent,
                thread_count=thread_count,
                file_descriptors=file_descriptors
            )
            
            # Update peaks
            self.peak_memory_mb = max(self.peak_memory_mb, memory_mb)
            self.peak_cpu_percent = max(self.peak_cpu_percent, cpu_percent)
            self.peak_thread_count = max(self.peak_thread_count, thread_count)
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Failed to get resource snapshot: {e}")
            return ResourceSnapshot(
                timestamp=datetime.now(),
                memory_mb=0, memory_percent=0, cpu_percent=0,
                disk_usage_percent=0, thread_count=0, file_descriptors=0
            )
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                snapshot = self.get_current_snapshot()
                
                # Store snapshot
                with self._lock:
                    self.snapshots.append(snapshot)
                    if len(self.snapshots) > self.max_snapshots:
                        self.snapshots = self.snapshots[-self.max_snapshots:]
                
                # Check thresholds and trigger warnings
                self._check_thresholds(snapshot)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _check_thresholds(self, snapshot: ResourceSnapshot):
        """Check if any thresholds are exceeded."""
        warnings = []
        
        if snapshot.memory_mb > self.thresholds.memory_mb:
            warnings.append(f"High memory usage: {snapshot.memory_mb:.1f}MB")
        
        if snapshot.memory_percent > self.thresholds.memory_percent:
            warnings.append(f"High memory percentage: {snapshot.memory_percent:.1f}%")
        
        if snapshot.cpu_percent > self.thresholds.cpu_percent:
            warnings.append(f"High CPU usage: {snapshot.cpu_percent:.1f}%")
        
        if snapshot.disk_usage_percent > self.thresholds.disk_usage_percent:
            warnings.append(f"High disk usage: {snapshot.disk_usage_percent:.1f}%")
        
        if snapshot.thread_count > self.thresholds.thread_count:
            warnings.append(f"High thread count: {snapshot.thread_count}")
        
        if snapshot.file_descriptors > self.thresholds.file_descriptors:
            warnings.append(f"High file descriptor count: {snapshot.file_descriptors}")
        
        # Trigger warning callbacks
        for warning in warnings:
            self.logger.warning(warning)
            for callback in self._warning_callbacks:
                try:
                    callback(warning, snapshot)
                except Exception as e:
                    self.logger.error(f"Error in warning callback: {e}")
    
    def add_warning_callback(self, callback: Callable[[str, ResourceSnapshot], None]):
        """Add callback for resource warnings."""
        self._warning_callbacks.append(callback)
    
    def remove_warning_callback(self, callback: Callable[[str, ResourceSnapshot], None]):
        """Remove warning callback."""
        if callback in self._warning_callbacks:
            self._warning_callbacks.remove(callback)
    
    def get_recent_snapshots(self, minutes: int = 10) -> List[ResourceSnapshot]:
        """Get snapshots from the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self._lock:
            return [s for s in self.snapshots if s.timestamp >= cutoff_time]
    
    def get_average_usage(self, minutes: int = 10) -> Dict[str, float]:
        """Get average resource usage over the last N minutes."""
        snapshots = self.get_recent_snapshots(minutes)
        
        if not snapshots:
            return {}
        
        return {
            'memory_mb': sum(s.memory_mb for s in snapshots) / len(snapshots),
            'memory_percent': sum(s.memory_percent for s in snapshots) / len(snapshots),
            'cpu_percent': sum(s.cpu_percent for s in snapshots) / len(snapshots),
            'disk_usage_percent': sum(s.disk_usage_percent for s in snapshots) / len(snapshots),
            'thread_count': sum(s.thread_count for s in snapshots) / len(snapshots),
            'file_descriptors': sum(s.file_descriptors for s in snapshots) / len(snapshots)
        }
    
    def get_peak_usage(self) -> Dict[str, float]:
        """Get peak resource usage since monitoring started."""
        return {
            'memory_mb': self.peak_memory_mb,
            'cpu_percent': self.peak_cpu_percent,
            'thread_count': self.peak_thread_count
        }
    
    def should_trigger_gc(self) -> bool:
        """Check if garbage collection should be triggered."""
        current = self.get_current_snapshot()
        
        # Trigger GC if memory usage is high
        if current.memory_mb > self.thresholds.memory_mb * 0.8:
            return True
        
        # Trigger GC if memory growth is rapid
        recent_snapshots = self.get_recent_snapshots(5)  # Last 5 minutes
        if len(recent_snapshots) >= 2:
            memory_growth = recent_snapshots[-1].memory_mb - recent_snapshots[0].memory_mb
            if memory_growth > 100:  # 100MB growth in 5 minutes
                return True
        
        return False
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop_monitoring()
        self._warning_callbacks.clear()
        self.snapshots.clear()


class MemoryManager:
    """Manages memory usage and garbage collection."""
    
    def __init__(self, resource_monitor: Optional[ResourceMonitor] = None):
        self.resource_monitor = resource_monitor
        self.logger = get_logger(self.__class__.__name__)
        
        # Track large objects
        self._large_objects = weakref.WeakSet()
        self._gc_stats = {
            'manual_collections': 0,
            'auto_collections': 0,
            'objects_collected': 0
        }
    
    def register_large_object(self, obj: Any):
        """Register a large object for tracking."""
        self._large_objects.add(obj)
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """Force garbage collection and return statistics."""
        self.logger.info("Forcing garbage collection")
        
        # Get initial object counts
        initial_counts = [len(gc.get_objects(generation)) for generation in range(3)]
        
        # Force collection
        collected = gc.collect()
        
        # Get final object counts
        final_counts = [len(gc.get_objects(generation)) for generation in range(3)]
        
        # Update statistics
        self._gc_stats['manual_collections'] += 1
        self._gc_stats['objects_collected'] += collected
        
        stats = {
            'objects_collected': collected,
            'generation_0_freed': initial_counts[0] - final_counts[0],
            'generation_1_freed': initial_counts[1] - final_counts[1],
            'generation_2_freed': initial_counts[2] - final_counts[2],
            'large_objects_tracked': len(self._large_objects)
        }
        
        self.logger.info(f"Garbage collection completed: {stats}")
        return stats
    
    def auto_manage_memory(self):
        """Automatically manage memory based on usage."""
        if self.resource_monitor and self.resource_monitor.should_trigger_gc():
            self.force_garbage_collection()
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            info = {
                'rss_mb': memory_info.rss / (1024 * 1024),
                'vms_mb': memory_info.vms / (1024 * 1024),
                'memory_percent': process.memory_percent(),
                'gc_stats': self._gc_stats.copy(),
                'gc_thresholds': gc.get_threshold(),
                'gc_counts': gc.get_count(),
                'large_objects_tracked': len(self._large_objects)
            }
            
            # Add platform-specific info
            if hasattr(memory_info, 'pss'):
                info['pss_mb'] = memory_info.pss / (1024 * 1024)
            if hasattr(memory_info, 'uss'):
                info['uss_mb'] = memory_info.uss / (1024 * 1024)
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get memory info: {e}")
            return {}
    
    def optimize_gc_thresholds(self):
        """Optimize garbage collection thresholds based on usage patterns."""
        current_thresholds = gc.get_threshold()
        
        # If we have high memory usage, make GC more aggressive
        if self.resource_monitor:
            current_snapshot = self.resource_monitor.get_current_snapshot()
            
            if current_snapshot.memory_percent > 70:
                # More aggressive GC
                new_thresholds = (
                    current_thresholds[0] // 2,
                    current_thresholds[1] // 2,
                    current_thresholds[2] // 2
                )
                gc.set_threshold(*new_thresholds)
                self.logger.info(f"Set aggressive GC thresholds: {new_thresholds}")
            
            elif current_snapshot.memory_percent < 30:
                # Less aggressive GC
                new_thresholds = (
                    current_thresholds[0] * 2,
                    current_thresholds[1] * 2,
                    current_thresholds[2] * 2
                )
                gc.set_threshold(*new_thresholds)
                self.logger.info(f"Set relaxed GC thresholds: {new_thresholds}")


class StreamingProcessor:
    """Processes large datasets using streaming to avoid memory issues."""
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 memory_manager: Optional[MemoryManager] = None):
        self.chunk_size = chunk_size
        self.memory_manager = memory_manager
        self.logger = get_logger(self.__class__.__name__)
    
    def process_file_stream(self, 
                           file_path: str,
                           processor: Callable[[str], Any],
                           progress_callback: Optional[Callable[[float], None]] = None):
        """Process a large file line by line."""
        try:
            import os
            file_size = os.path.getsize(file_path)
            processed_bytes = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        # Process line
                        result = processor(line.strip())
                        
                        # Update progress
                        processed_bytes += len(line.encode('utf-8'))
                        if progress_callback and line_num % 100 == 0:
                            progress = processed_bytes / file_size
                            progress_callback(progress)
                        
                        # Memory management
                        if self.memory_manager and line_num % 1000 == 0:
                            self.memory_manager.auto_manage_memory()
                        
                        yield result
                        
                    except Exception as e:
                        self.logger.warning(f"Error processing line {line_num}: {e}")
                        continue
            
            if progress_callback:
                progress_callback(1.0)
                
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def process_data_chunks(self,
                           data_source: Callable[[int, int], List[Any]],
                           processor: Callable[[List[Any]], Any],
                           total_count: int,
                           progress_callback: Optional[Callable[[float], None]] = None):
        """Process data in chunks to manage memory usage."""
        processed_count = 0
        
        while processed_count < total_count:
            try:
                # Calculate chunk size for this iteration
                current_chunk_size = min(self.chunk_size, total_count - processed_count)
                
                # Get chunk data
                chunk_data = data_source(processed_count, current_chunk_size)
                
                if not chunk_data:
                    break
                
                # Process chunk
                result = processor(chunk_data)
                yield result
                
                processed_count += len(chunk_data)
                
                # Update progress
                if progress_callback:
                    progress = processed_count / total_count
                    progress_callback(progress)
                
                # Memory management
                if self.memory_manager:
                    self.memory_manager.auto_manage_memory()
                
                # Log progress periodically
                if processed_count % (self.chunk_size * 10) == 0:
                    self.logger.info(f"Processed {processed_count}/{total_count} items")
                
            except Exception as e:
                self.logger.error(f"Error processing chunk at offset {processed_count}: {e}")
                processed_count += current_chunk_size
                continue


# Global instances
_global_resource_monitor = None
_global_memory_manager = None
_monitor_lock = threading.Lock()


def get_resource_monitor() -> ResourceMonitor:
    """Get the global resource monitor instance."""
    global _global_resource_monitor
    
    if _global_resource_monitor is None:
        with _monitor_lock:
            if _global_resource_monitor is None:
                _global_resource_monitor = ResourceMonitor()
                _global_resource_monitor.start_monitoring()
    
    return _global_resource_monitor


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    global _global_memory_manager
    
    if _global_memory_manager is None:
        with _monitor_lock:
            if _global_memory_manager is None:
                resource_monitor = get_resource_monitor()
                _global_memory_manager = MemoryManager(resource_monitor)
    
    return _global_memory_manager


def get_resource_manager():
    """Get the global memory manager instance (alias for compatibility)."""
    return get_memory_manager()


def managed_operation(operation_name: str, description: str = ""):
    """Context manager for resource-managed operations."""
    class ManagedOperationContext:
        def __init__(self, name: str, desc: str):
            self.name = name
            self.description = desc
            self.memory_manager = get_memory_manager()
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            # Auto manage memory after operation
            self.memory_manager.auto_manage_memory()
            
            # Log operation completion
            duration = time.time() - self.start_time if self.start_time else 0
            logger = get_logger("ManagedOperation")
            logger.info(f"Operation '{self.name}' completed in {duration:.2f}s")
    
    return ManagedOperationContext(operation_name, description)


def with_resource_management(operation_name: str):
    """Decorator for resource-managed operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with managed_operation(operation_name, f"Function: {func.__name__}"):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def cleanup_global_resources():
    """Cleanup global resource managers."""
    global _global_resource_monitor, _global_memory_manager
    
    with _monitor_lock:
        if _global_resource_monitor:
            _global_resource_monitor.cleanup()
            _global_resource_monitor = None
        
        _global_memory_manager = None