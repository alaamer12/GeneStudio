"""Base ViewModel abstract class with observer pattern."""

from abc import ABC
from typing import Any, Callable, Dict, List, Optional
import logging
import threading


class BaseViewModel(ABC):
    """Abstract base class for all ViewModels implementing observer pattern."""
    
    def __init__(self):
        """Initialize ViewModel with observer pattern support."""
        self._state: Dict[str, Any] = {}
        self._observers: List[Callable[[], None]] = []
        self._property_observers: Dict[str, List[Callable[[Any], None]]] = {}
        self._lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_observer(self, callback: Callable[[], None]) -> None:
        """
        Add an observer that will be notified of any state changes.
        
        Args:
            callback: Function to call when state changes
        """
        with self._lock:
            if callback not in self._observers:
                self._observers.append(callback)
                self.logger.debug(f"Added observer: {callback.__name__}")
    
    def remove_observer(self, callback: Callable[[], None]) -> None:
        """
        Remove an observer.
        
        Args:
            callback: Function to remove from observers
        """
        with self._lock:
            if callback in self._observers:
                self._observers.remove(callback)
                self.logger.debug(f"Removed observer: {callback.__name__}")
    
    def add_property_observer(self, property_name: str, callback: Callable[[Any], None]) -> None:
        """
        Add an observer for a specific property.
        
        Args:
            property_name: Name of the property to observe
            callback: Function to call when property changes (receives new value)
        """
        with self._lock:
            if property_name not in self._property_observers:
                self._property_observers[property_name] = []
            
            if callback not in self._property_observers[property_name]:
                self._property_observers[property_name].append(callback)
                self.logger.debug(f"Added property observer for '{property_name}': {callback.__name__}")
    
    def remove_property_observer(self, property_name: str, callback: Callable[[Any], None]) -> None:
        """
        Remove a property observer.
        
        Args:
            property_name: Name of the property
            callback: Function to remove from property observers
        """
        with self._lock:
            if property_name in self._property_observers:
                if callback in self._property_observers[property_name]:
                    self._property_observers[property_name].remove(callback)
                    self.logger.debug(f"Removed property observer for '{property_name}': {callback.__name__}")
    
    def notify_observers(self) -> None:
        """Notify all observers of state changes."""
        with self._lock:
            observers_copy = self._observers.copy()
        
        for observer in observers_copy:
            try:
                observer()
            except Exception as e:
                self.logger.error(f"Error notifying observer {observer.__name__}: {e}")
    
    def notify_property_observers(self, property_name: str, new_value: Any) -> None:
        """
        Notify observers of a specific property change.
        
        Args:
            property_name: Name of the changed property
            new_value: New value of the property
        """
        with self._lock:
            if property_name in self._property_observers:
                observers_copy = self._property_observers[property_name].copy()
            else:
                observers_copy = []
        
        for observer in observers_copy:
            try:
                observer(new_value)
            except Exception as e:
                self.logger.error(f"Error notifying property observer for '{property_name}': {e}")
    
    def update_state(self, key: str, value: Any) -> None:
        """
        Update a state property and notify observers.
        
        Args:
            key: State property name
            value: New value
        """
        old_value = self._state.get(key)
        
        if old_value != value:
            self._state[key] = value
            self.logger.debug(f"State updated: {key} = {value}")
            
            # Notify property-specific observers
            self.notify_property_observers(key, value)
            
            # Notify general observers
            self.notify_observers()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a state property value.
        
        Args:
            key: State property name
            default: Default value if key doesn't exist
            
        Returns:
            State property value or default
        """
        return self._state.get(key, default)
    
    def has_state(self, key: str) -> bool:
        """
        Check if a state property exists.
        
        Args:
            key: State property name
            
        Returns:
            True if property exists
        """
        return key in self._state
    
    def clear_state(self) -> None:
        """Clear all state and notify observers."""
        self._state.clear()
        self.logger.debug("State cleared")
        self.notify_observers()
    
    def get_all_state(self) -> Dict[str, Any]:
        """
        Get a copy of all state data.
        
        Returns:
            Dictionary containing all state data
        """
        return self._state.copy()
    
    def set_loading(self, is_loading: bool) -> None:
        """
        Set loading state.
        
        Args:
            is_loading: Whether the ViewModel is in loading state
        """
        self.update_state("loading", is_loading)
    
    def is_loading(self) -> bool:
        """
        Check if ViewModel is in loading state.
        
        Returns:
            True if loading
        """
        return self.get_state("loading", False)
    
    def set_error(self, error_message: Optional[str]) -> None:
        """
        Set error state.
        
        Args:
            error_message: Error message or None to clear error
        """
        self.update_state("error", error_message)
        if error_message:
            self.logger.error(f"ViewModel error: {error_message}")
    
    def get_error(self) -> Optional[str]:
        """
        Get current error message.
        
        Returns:
            Error message or None
        """
        return self.get_state("error")
    
    def has_error(self) -> bool:
        """
        Check if ViewModel has an error.
        
        Returns:
            True if there's an error
        """
        return self.get_error() is not None
    
    def clear_error(self) -> None:
        """Clear error state."""
        self.set_error(None)
    
    def execute_async_operation(
        self,
        operation: Callable[[], Any],
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        loading_key: str = "loading"
    ) -> None:
        """
        Execute an async operation with loading state management.
        
        Args:
            operation: Function to execute
            on_success: Callback for successful completion
            on_error: Callback for error handling
            loading_key: State key for loading indicator
        """
        from utils.async_executor import AsyncExecutor
        
        def task():
            return operation()
        
        def on_complete(result):
            self.update_state(loading_key, False)
            if on_success:
                on_success(result)
        
        def on_operation_error(error):
            self.update_state(loading_key, False)
            self.set_error(str(error))
            if on_error:
                on_error(error)
        
        self.update_state(loading_key, True)
        self.clear_error()
        
        AsyncExecutor.run_async(task, on_complete, on_operation_error)
    
    def cleanup(self) -> None:
        """Clean up resources and observers."""
        with self._lock:
            self._observers.clear()
            self._property_observers.clear()
            self._state.clear()
        
        self.logger.debug("ViewModel cleaned up")