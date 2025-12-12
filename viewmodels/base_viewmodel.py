"""Base ViewModel class with observer pattern and state management."""

from typing import Any, Dict, List, Callable, Optional
from utils.logger import get_logger


class BaseViewModel:
    """Abstract base class for all ViewModels with observer pattern."""
    
    def __init__(self):
        """Initialize base ViewModel."""
        self.logger = get_logger(self.__class__.__name__)
        self._observers: List[Callable] = []
        self._state: Dict[str, Any] = {}
        self._loading_states: Dict[str, bool] = {}
        
        # Initialize default state
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize default state. Override in subclasses."""
        self._state = {
            'initialized': True,
            'error': None,
            'loading': False
        }
    
    def add_observer(self, callback: Callable[[str, Any], None]) -> None:
        """Add an observer callback for state changes."""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remove_observer(self, callback: Callable[[str, Any], None]) -> None:
        """Remove an observer callback."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def notify_observers(self, key: Optional[str] = None, value: Any = None) -> None:
        """Notify all observers of state changes."""
        for callback in self._observers:
            try:
                callback(key, value)
            except Exception as e:
                self.logger.error(f"Error notifying observer: {e}")
    
    def update_state(self, key: str, value: Any, notify: bool = True) -> None:
        """Update state and optionally notify observers."""
        old_value = self._state.get(key)
        self._state[key] = value
        
        if notify and old_value != value:
            self.notify_observers(key, value)
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value by key."""
        return self._state.get(key, default)
    
    def get_all_state(self) -> Dict[str, Any]:
        """Get all state data."""
        return self._state.copy()
    
    def clear_state(self) -> None:
        """Clear all state data."""
        self._state.clear()
        self._initialize_state()
        self.notify_observers()
    
    def set_loading(self, operation: str, loading: bool = True) -> None:
        """Set loading state for a specific operation."""
        self._loading_states[operation] = loading
        self.update_state('loading', any(self._loading_states.values()))
        self.update_state(f'loading_{operation}', loading)
    
    def is_loading(self, operation: Optional[str] = None) -> bool:
        """Check if currently loading (specific operation or any)."""
        if operation:
            return self._loading_states.get(operation, False)
        return any(self._loading_states.values())
    
    def set_error(self, error: Optional[str], operation: Optional[str] = None) -> None:
        """Set error state."""
        self.update_state('error', error)
        if operation:
            self.update_state(f'error_{operation}', error)
    
    def clear_error(self, operation: Optional[str] = None) -> None:
        """Clear error state."""
        self.set_error(None, operation)
    
    def has_error(self, operation: Optional[str] = None) -> bool:
        """Check if there's an error."""
        if operation:
            return bool(self.get_state(f'error_{operation}'))
        return bool(self.get_state('error'))
    
    def execute_async_operation(self, operation_name: str, operation_func: Callable,
                               on_success: Optional[Callable] = None,
                               on_error: Optional[Callable] = None) -> None:
        """Execute an async operation with loading and error handling."""
        from utils.async_executor import AsyncExecutor
        
        # Set loading state
        self.set_loading(operation_name, True)
        self.clear_error(operation_name)
        
        def success_handler(result):
            self.set_loading(operation_name, False)
            if on_success:
                on_success(result)
        
        def error_handler(error):
            self.set_loading(operation_name, False)
            error_message = str(error)
            self.set_error(error_message, operation_name)
            self.logger.error(f"Error in {operation_name}: {error_message}")
            if on_error:
                on_error(error)
        
        AsyncExecutor.run_async(operation_func, success_handler, error_handler)
    
    def validate_input(self, data: Dict[str, Any], rules: Dict[str, Callable]) -> tuple[bool, Dict[str, str]]:
        """Validate input data against rules."""
        errors = {}
        
        for field, validator in rules.items():
            if field in data:
                try:
                    is_valid, error_message = validator(data[field])
                    if not is_valid:
                        errors[field] = error_message
                except Exception as e:
                    errors[field] = f"Validation error: {e}"
        
        return len(errors) == 0, errors
    
    def log_action(self, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log user action for debugging and analytics."""
        log_message = f"User action: {action}"
        if details:
            log_message += f" - {details}"
        self.logger.info(log_message)
    
    def cleanup(self) -> None:
        """Cleanup resources when ViewModel is destroyed."""
        self._observers.clear()
        self._state.clear()
        self._loading_states.clear()
        self.logger.debug("ViewModel cleaned up")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore errors during cleanup