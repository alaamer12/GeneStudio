"""Async executor utility for non-blocking operations."""

import threading
import time
from typing import Callable, Any, Optional
import logging


class AsyncExecutor:
    """Executes long-running operations asynchronously."""
    
    @staticmethod
    def run_async(
        task: Callable[[], Any], 
        on_complete: Callable[[Any], None], 
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> threading.Thread:
        """
        Execute a task asynchronously and call callbacks on completion.
        
        Args:
            task: Function to execute asynchronously
            on_complete: Callback for successful completion
            on_error: Optional callback for error handling
            
        Returns:
            Thread object for the async operation
        """
        def worker():
            try:
                result = task()
                # Schedule callback on main thread using timer
                threading.Timer(0, lambda: on_complete(result)).start()
            except Exception as e:
                logging.error(f"Async task failed: {e}")
                if on_error:
                    threading.Timer(0, lambda: on_error(e)).start()
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
    
    @staticmethod
    def run_with_progress(
        task: Callable[[Callable[[float], None]], Any],
        progress_callback: Callable[[float], None],
        on_complete: Callable[[Any], None],
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> threading.Thread:
        """
        Execute a task with progress reporting.
        
        Args:
            task: Function that accepts a progress callback (0.0 to 1.0)
            progress_callback: Callback for progress updates
            on_complete: Callback for successful completion
            on_error: Optional callback for error handling
            
        Returns:
            Thread object for the async operation
        """
        def worker():
            try:
                def update_progress(progress: float):
                    threading.Timer(0, lambda: progress_callback(progress)).start()
                
                result = task(update_progress)
                threading.Timer(0, lambda: on_complete(result)).start()
            except Exception as e:
                logging.error(f"Async task with progress failed: {e}")
                if on_error:
                    threading.Timer(0, lambda: on_error(e)).start()
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
    
    @staticmethod
    def run_with_timeout(
        task: Callable[[], Any],
        timeout_seconds: float,
        on_complete: Callable[[Any], None],
        on_timeout: Callable[[], None],
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> threading.Thread:
        """
        Execute a task with a timeout.
        
        Args:
            task: Function to execute
            timeout_seconds: Maximum execution time
            on_complete: Callback for successful completion
            on_timeout: Callback for timeout
            on_error: Optional callback for error handling
            
        Returns:
            Thread object for the async operation
        """
        result_container = {'result': None, 'completed': False, 'error': None}
        
        def worker():
            try:
                result_container['result'] = task()
                result_container['completed'] = True
            except Exception as e:
                result_container['error'] = e
        
        def monitor():
            thread = threading.Thread(target=worker, daemon=True)
            thread.start()
            thread.join(timeout_seconds)
            
            if result_container['completed']:
                threading.Timer(0, lambda: on_complete(result_container['result'])).start()
            elif result_container['error']:
                if on_error:
                    threading.Timer(0, lambda: on_error(result_container['error'])).start()
            else:
                # Timeout occurred
                threading.Timer(0, on_timeout).start()
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        return monitor_thread


class CancellableTask:
    """A task that can be cancelled during execution."""
    
    def __init__(self):
        self._cancelled = False
        self._thread = None
    
    def cancel(self):
        """Cancel the task."""
        self._cancelled = True
    
    @property
    def is_cancelled(self) -> bool:
        """Check if task is cancelled."""
        return self._cancelled
    
    def run_async(
        self,
        task: Callable[['CancellableTask'], Any],
        on_complete: Callable[[Any], None],
        on_cancelled: Callable[[], None],
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> threading.Thread:
        """
        Run a cancellable task asynchronously.
        
        Args:
            task: Function that accepts this CancellableTask instance
            on_complete: Callback for successful completion
            on_cancelled: Callback for cancellation
            on_error: Optional callback for error handling
            
        Returns:
            Thread object for the async operation
        """
        def worker():
            try:
                if self._cancelled:
                    threading.Timer(0, on_cancelled).start()
                    return
                
                result = task(self)
                
                if self._cancelled:
                    threading.Timer(0, on_cancelled).start()
                else:
                    threading.Timer(0, lambda: on_complete(result)).start()
                    
            except Exception as e:
                if not self._cancelled:
                    logging.error(f"Cancellable task failed: {e}")
                    if on_error:
                        threading.Timer(0, lambda: on_error(e)).start()
        
        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()
        return self._thread