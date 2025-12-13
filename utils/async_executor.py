"""Async executor utility for non-blocking operations."""

import threading
import time
from typing import Callable, Optional, Any
from concurrent.futures import ThreadPoolExecutor, Future
import logging


class AsyncExecutor:
    """Executes long-running operations asynchronously."""
    
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
    
    @staticmethod
    def run_async(task: Callable[[], Any], 
                  on_complete: Optional[Callable[[Any], None]] = None,
                  on_error: Optional[Callable[[Exception], None]] = None) -> threading.Thread:
        """
        Run a task asynchronously using a thread.
        
        Args:
            task: Function to execute
            on_complete: Callback for successful completion
            on_error: Callback for error handling
            
        Returns:
            Thread object
        """
        def worker():
            try:
                result = task()
                if on_complete:
                    # Simple direct call - let the ViewModel handle thread safety
                    on_complete(result)
            except Exception as e:
                if on_error:
                    on_error(e)
                else:
                    logging.getLogger(__name__).error(f"Async task failed: {e}", exc_info=True)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
    
    @staticmethod
    def run_with_progress(task: Callable[[Callable[[float], None]], Any],
                         progress_callback: Callable[[float], None],
                         on_complete: Optional[Callable[[Any], None]] = None,
                         on_error: Optional[Callable[[Exception], None]] = None) -> threading.Thread:
        """
        Run a task asynchronously with progress reporting.
        
        Args:
            task: Function that accepts a progress callback
            progress_callback: Callback for progress updates (0.0 to 1.0)
            on_complete: Callback for successful completion
            on_error: Callback for error handling
            
        Returns:
            Thread object
        """
        def worker():
            try:
                def progress_wrapper(progress: float):
                    # Direct call - let the ViewModel handle thread safety
                    progress_callback(progress)
                
                result = task(progress_wrapper)
                if on_complete:
                    on_complete(result)
            except Exception as e:
                if on_error:
                    on_error(e)
                else:
                    logging.getLogger(__name__).error(f"Async task with progress failed: {e}", exc_info=True)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
    
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