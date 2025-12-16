"""Enhanced async executor utility for non-blocking operations with progress tracking."""

import threading
import time
from typing import Callable, Optional, Any, Dict
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime, timedelta
import logging
import psutil
import gc
import weakref
from utils.cache_manager import get_cache_manager


class ProgressTracker:
    """Tracks progress and estimates completion time for operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = time.time()
        self.progress = 0.0
        self.last_update = self.start_time
        self.progress_history = [(0.0, self.start_time)]
        self.is_cancelled = False
        self.estimated_total_time = None
        self.estimated_completion_time = None
    
    def update_progress(self, progress: float):
        """Update progress and calculate estimates."""
        if self.is_cancelled:
            return
        
        current_time = time.time()
        self.progress = max(0.0, min(1.0, progress))
        self.last_update = current_time
        
        # Store progress history for better estimation
        self.progress_history.append((self.progress, current_time))
        
        # Keep only recent history (last 10 updates)
        if len(self.progress_history) > 10:
            self.progress_history = self.progress_history[-10:]
        
        # Calculate estimates
        self._calculate_estimates()
    
    def _calculate_estimates(self):
        """Calculate estimated completion time based on progress history."""
        if self.progress <= 0.0:
            return
        
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # Simple linear estimation
        if self.progress > 0:
            self.estimated_total_time = elapsed_time / self.progress
            remaining_time = self.estimated_total_time - elapsed_time
            self.estimated_completion_time = current_time + remaining_time
        
        # More sophisticated estimation using recent progress rate
        if len(self.progress_history) >= 2:
            recent_progress = self.progress_history[-1][0] - self.progress_history[-2][0]
            recent_time = self.progress_history[-1][1] - self.progress_history[-2][1]
            
            if recent_progress > 0 and recent_time > 0:
                recent_rate = recent_progress / recent_time
                remaining_progress = 1.0 - self.progress
                estimated_remaining_time = remaining_progress / recent_rate
                self.estimated_completion_time = current_time + estimated_remaining_time
    
    def get_eta_seconds(self) -> Optional[float]:
        """Get estimated time to completion in seconds."""
        if self.estimated_completion_time:
            return max(0, self.estimated_completion_time - time.time())
        return None
    
    def get_eta_string(self) -> str:
        """Get estimated time to completion as formatted string."""
        eta_seconds = self.get_eta_seconds()
        if eta_seconds is None:
            return "Unknown"
        
        if eta_seconds < 60:
            return f"{int(eta_seconds)}s"
        elif eta_seconds < 3600:
            minutes = int(eta_seconds // 60)
            seconds = int(eta_seconds % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(eta_seconds // 3600)
            minutes = int((eta_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def cancel(self):
        """Mark operation as cancelled."""
        self.is_cancelled = True


class ResourceMonitor:
    """Monitors system resources during operations."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        self.peak_memory = self.initial_memory
        self.initial_cpu_percent = self.process.cpu_percent()
    
    def update(self):
        """Update resource usage statistics."""
        current_memory = self.process.memory_info().rss
        self.peak_memory = max(self.peak_memory, current_memory)
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def get_peak_memory_mb(self) -> float:
        """Get peak memory usage in MB."""
        return self.peak_memory / (1024 * 1024)
    
    def get_memory_increase_mb(self) -> float:
        """Get memory increase since start in MB."""
        current_memory = self.process.memory_info().rss
        return (current_memory - self.initial_memory) / (1024 * 1024)
    
    def get_cpu_percent(self) -> float:
        """Get current CPU usage percentage."""
        return self.process.cpu_percent()
    
    def should_warn_memory(self, threshold_mb: float = 1000) -> bool:
        """Check if memory usage exceeds threshold."""
        return self.get_memory_usage_mb() > threshold_mb
    
    def should_warn_cpu(self, threshold_percent: float = 80) -> bool:
        """Check if CPU usage exceeds threshold."""
        return self.get_cpu_percent() > threshold_percent


class AsyncExecutor:
    """Enhanced async executor with progress tracking and resource monitoring."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for async executor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize async executor."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="AsyncExecutor")
        self.logger = logging.getLogger(__name__)
        self._active_tasks = {}
        self._task_counter = 0
        self._tasks_lock = threading.Lock()
        self._progress_trackers = {}
        self._resource_monitors = {}
        self._cancellation_tokens = {}
    
    @staticmethod
    def run_async(task: Callable[[], Any], 
                  on_complete: Optional[Callable[[Any], None]] = None,
                  on_error: Optional[Callable[[Exception], None]] = None,
                  task_name: str = "unnamed_task") -> threading.Thread:
        """
        Run a task asynchronously using a thread.
        
        Args:
            task: Function to execute
            on_complete: Callback for successful completion
            on_error: Callback for error handling
            task_name: Name for the task (for monitoring)
            
        Returns:
            Thread object
        """
        def worker():
            resource_monitor = ResourceMonitor()
            
            try:
                result = task()
                if on_complete:
                    # Simple direct call - let the ViewModel handle thread safety
                    on_complete(result)
            except Exception as e:
                if on_error:
                    on_error(e)
                else:
                    logging.getLogger(__name__).error(f"Async task '{task_name}' failed: {e}", exc_info=True)
            finally:
                # Log resource usage
                logging.getLogger(__name__).info(
                    f"Task '{task_name}' completed. "
                    f"Peak memory: {resource_monitor.get_peak_memory_mb():.1f}MB, "
                    f"Memory increase: {resource_monitor.get_memory_increase_mb():.1f}MB"
                )
        
        thread = threading.Thread(target=worker, daemon=True, name=f"AsyncTask-{task_name}")
        thread.start()
        return thread
    
    @staticmethod
    def run_with_progress(task: Callable[[Callable[[float], None]], Any],
                         progress_callback: Callable[[float], None],
                         on_complete: Optional[Callable[[Any], None]] = None,
                         on_error: Optional[Callable[[Exception], None]] = None,
                         task_name: str = "unnamed_task",
                         enable_cancellation: bool = False) -> Dict[str, Any]:
        """
        Run a task asynchronously with enhanced progress reporting.
        
        Args:
            task: Function that accepts a progress callback
            progress_callback: Callback for progress updates (0.0 to 1.0)
            on_complete: Callback for successful completion
            on_error: Callback for error handling
            task_name: Name for the task (for monitoring)
            enable_cancellation: Whether to enable cancellation support
            
        Returns:
            Dictionary with thread and control functions
        """
        progress_tracker = ProgressTracker(task_name)
        resource_monitor = ResourceMonitor()
        cancellation_token = {'cancelled': False} if enable_cancellation else None
        
        def enhanced_progress_callback(progress: float):
            if cancellation_token and cancellation_token['cancelled']:
                progress_tracker.cancel()
                return
            
            progress_tracker.update_progress(progress)
            resource_monitor.update()
            
            # Call original progress callback with enhanced info
            progress_info = {
                'progress': progress,
                'eta_string': progress_tracker.get_eta_string(),
                'eta_seconds': progress_tracker.get_eta_seconds(),
                'memory_mb': resource_monitor.get_memory_usage_mb(),
                'cpu_percent': resource_monitor.get_cpu_percent(),
                'is_cancelled': progress_tracker.is_cancelled
            }
            
            # Check for resource warnings
            if resource_monitor.should_warn_memory():
                logging.getLogger(__name__).warning(
                    f"High memory usage in task '{task_name}': {resource_monitor.get_memory_usage_mb():.1f}MB"
                )
            
            if resource_monitor.should_warn_cpu():
                logging.getLogger(__name__).warning(
                    f"High CPU usage in task '{task_name}': {resource_monitor.get_cpu_percent():.1f}%"
                )
            
            progress_callback(progress_info)
        
        def worker():
            try:
                # Check for cancellation before starting
                if cancellation_token and cancellation_token['cancelled']:
                    return
                
                result = task(enhanced_progress_callback)
                
                # Check for cancellation before completion
                if cancellation_token and cancellation_token['cancelled']:
                    logging.getLogger(__name__).info(f"Task '{task_name}' was cancelled")
                    return
                
                if on_complete:
                    on_complete(result)
                    
            except Exception as e:
                if on_error:
                    on_error(e)
                else:
                    logging.getLogger(__name__).error(f"Async task '{task_name}' failed: {e}", exc_info=True)
            finally:
                # Log final resource usage
                logging.getLogger(__name__).info(
                    f"Task '{task_name}' finished. "
                    f"Peak memory: {resource_monitor.get_peak_memory_mb():.1f}MB, "
                    f"Memory increase: {resource_monitor.get_memory_increase_mb():.1f}MB, "
                    f"Final progress: {progress_tracker.progress:.1%}"
                )
                
                # Trigger garbage collection for large operations
                if resource_monitor.get_memory_increase_mb() > 100:
                    gc.collect()
        
        thread = threading.Thread(target=worker, daemon=True, name=f"AsyncProgressTask-{task_name}")
        thread.start()
        
        result = {
            'thread': thread,
            'progress_tracker': progress_tracker,
            'resource_monitor': resource_monitor
        }
        
        if enable_cancellation:
            result['cancel'] = lambda: cancellation_token.update({'cancelled': True})
            result['is_cancelled'] = lambda: cancellation_token['cancelled']
        
        return result
    
    def submit_task(self, task: Callable[[], Any], 
                   task_name: str = "unnamed_task") -> int:
        """
        Submit a task to the thread pool executor.
        
        Args:
            task: Function to execute
            task_name: Name for the task (for tracking)
            
        Returns:
            Task ID for tracking
        """
        with self._tasks_lock:
            self._task_counter += 1
            task_id = self._task_counter
        
        future = self.executor.submit(task)
        
        with self._tasks_lock:
            self._active_tasks[task_id] = {
                'future': future,
                'name': task_name,
                'start_time': time.time()
            }
        
        # Add completion callback to clean up
        def cleanup_task(fut):
            with self._tasks_lock:
                self._active_tasks.pop(task_id, None)
        
        future.add_done_callback(cleanup_task)
        
        self.logger.info(f"Submitted task {task_id}: {task_name}")
        return task_id
    
    def get_task_result(self, task_id: int, timeout: Optional[float] = None) -> Any:
        """
        Get the result of a submitted task.
        
        Args:
            task_id: Task ID returned by submit_task
            timeout: Maximum time to wait for result
            
        Returns:
            Task result
            
        Raises:
            KeyError: If task ID not found
            TimeoutError: If timeout exceeded
            Exception: Any exception raised by the task
        """
        with self._tasks_lock:
            if task_id not in self._active_tasks:
                raise KeyError(f"Task {task_id} not found")
            
            future = self._active_tasks[task_id]['future']
        
        return future.result(timeout=timeout)
    
    def cancel_task(self, task_id: int) -> bool:
        """
        Cancel a submitted task.
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            True if task was cancelled, False otherwise
        """
        with self._tasks_lock:
            if task_id not in self._active_tasks:
                return False
            
            future = self._active_tasks[task_id]['future']
            cancelled = future.cancel()
            
            if cancelled:
                self._active_tasks.pop(task_id, None)
                self.logger.info(f"Cancelled task {task_id}")
            
            return cancelled
    
    def get_active_tasks(self) -> dict:
        """Get information about active tasks."""
        with self._tasks_lock:
            active_info = {}
            for task_id, task_info in self._active_tasks.items():
                active_info[task_id] = {
                    'name': task_info['name'],
                    'start_time': task_info['start_time'],
                    'running_time': time.time() - task_info['start_time'],
                    'done': task_info['future'].done(),
                    'cancelled': task_info['future'].cancelled()
                }
            return active_info
    
    def wait_for_all_tasks(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all active tasks to complete.
        
        Args:
            timeout: Maximum time to wait
            
        Returns:
            True if all tasks completed, False if timeout
        """
        start_time = time.time()
        
        while True:
            with self._tasks_lock:
                if not self._active_tasks:
                    return True
                
                # Check if any tasks are still running
                running_tasks = [
                    task_info for task_info in self._active_tasks.values()
                    if not task_info['future'].done()
                ]
                
                if not running_tasks:
                    return True
            
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            time.sleep(0.1)
    
    def shutdown(self, wait: bool = True):
        """Shutdown the executor."""
        self.logger.info("Shutting down AsyncExecutor")
        self.executor.shutdown(wait=wait)
    
    def __del__(self):
        """Cleanup on destruction."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# Convenience functions for backward compatibility
def run_async(task: Callable[[], Any], 
              on_complete: Optional[Callable[[Any], None]] = None,
              on_error: Optional[Callable[[Exception], None]] = None) -> threading.Thread:
    """Run a task asynchronously."""
    return AsyncExecutor.run_async(task, on_complete, on_error)


def run_with_progress(task: Callable[[Callable[[float], None]], Any],
                     progress_callback: Callable[[float], None],
                     on_complete: Optional[Callable[[Any], None]] = None,
                     on_error: Optional[Callable[[Exception], None]] = None) -> threading.Thread:
    """Run a task asynchronously with progress reporting."""
    return AsyncExecutor.run_with_progress(task, progress_callback, on_complete, on_error)


# Global instance for convenience
_global_executor = None


def get_executor() -> AsyncExecutor:
    """Get the global AsyncExecutor instance."""
    global _global_executor
    if _global_executor is None:
        _global_executor = AsyncExecutor()
    return _global_executor