"""Comprehensive error handling utilities with specific error types."""

import logging
import traceback
import functools
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    ALGORITHM = "algorithm"
    MEMORY = "memory"
    PERMISSION = "permission"
    CONFIGURATION = "configuration"
    USER_INPUT = "user_input"
    SYSTEM = "system"


@dataclass
class ErrorContext:
    """Context information for errors."""
    operation: str
    component: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = None
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.additional_data is None:
            self.additional_data = {}


class GeneStudioError(Exception):
    """Base exception for all GeneStudio errors."""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.SYSTEM,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 context: Optional[ErrorContext] = None,
                 cause: Optional[Exception] = None,
                 user_message: Optional[str] = None,
                 recovery_suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context
        self.cause = cause
        self.user_message = user_message or self._generate_user_message()
        self.recovery_suggestions = recovery_suggestions or []
        self.timestamp = datetime.now()
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly message based on category."""
        category_messages = {
            ErrorCategory.VALIDATION: "Please check your input and try again.",
            ErrorCategory.DATABASE: "A database error occurred. Please try again later.",
            ErrorCategory.FILE_SYSTEM: "File operation failed. Please check file permissions and path.",
            ErrorCategory.NETWORK: "Network connection failed. Please check your internet connection.",
            ErrorCategory.ALGORITHM: "Analysis failed. Please check your input parameters.",
            ErrorCategory.MEMORY: "Insufficient memory. Please try with a smaller dataset.",
            ErrorCategory.PERMISSION: "Permission denied. Please check your access rights.",
            ErrorCategory.CONFIGURATION: "Configuration error. Please check application settings.",
            ErrorCategory.USER_INPUT: "Invalid input provided. Please correct and try again.",
            ErrorCategory.SYSTEM: "A system error occurred. Please contact support if this persists."
        }
        return category_messages.get(self.category, "An error occurred. Please try again.")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            'message': self.message,
            'user_message': self.user_message,
            'category': self.category.value,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'context': {
                'operation': self.context.operation if self.context else None,
                'component': self.context.component if self.context else None,
                'user_id': self.context.user_id if self.context else None,
                'session_id': self.context.session_id if self.context else None,
                'additional_data': self.context.additional_data if self.context else {}
            },
            'cause': str(self.cause) if self.cause else None,
            'recovery_suggestions': self.recovery_suggestions,
            'stack_trace': traceback.format_exc() if self.cause else None
        }


# Specific error types
class ValidationError(GeneStudioError):
    """Error for validation failures."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, **kwargs):
        self.field = field
        self.value = value
        
        context = kwargs.get('context')
        if context and field:
            context.additional_data['field'] = field
            context.additional_data['value'] = str(value) if value is not None else None
        
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )


class DatabaseError(GeneStudioError):
    """Error for database operations."""
    
    def __init__(self, message: str, query: Optional[str] = None, 
                 table: Optional[str] = None, **kwargs):
        self.query = query
        self.table = table
        
        context = kwargs.get('context')
        if context:
            if query:
                context.additional_data['query'] = query
            if table:
                context.additional_data['table'] = table
        
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            recovery_suggestions=[
                "Check database connection",
                "Verify data integrity",
                "Try again in a few moments"
            ],
            **kwargs
        )


class FileSystemError(GeneStudioError):
    """Error for file system operations."""
    
    def __init__(self, message: str, filepath: Optional[str] = None, 
                 operation: Optional[str] = None, **kwargs):
        self.filepath = filepath
        self.operation = operation
        
        context = kwargs.get('context')
        if context:
            if filepath:
                context.additional_data['filepath'] = filepath
            if operation:
                context.additional_data['file_operation'] = operation
        
        super().__init__(
            message,
            category=ErrorCategory.FILE_SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            recovery_suggestions=[
                "Check file path exists",
                "Verify file permissions",
                "Ensure sufficient disk space"
            ],
            **kwargs
        )


class NetworkError(GeneStudioError):
    """Error for network operations."""
    
    def __init__(self, message: str, url: Optional[str] = None, 
                 status_code: Optional[int] = None, **kwargs):
        self.url = url
        self.status_code = status_code
        
        context = kwargs.get('context')
        if context:
            if url:
                context.additional_data['url'] = url
            if status_code:
                context.additional_data['status_code'] = status_code
        
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.LOW,  # Often non-critical
            recovery_suggestions=[
                "Check internet connection",
                "Try again later",
                "Contact administrator if problem persists"
            ],
            **kwargs
        )


class AlgorithmError(GeneStudioError):
    """Error for algorithm execution."""
    
    def __init__(self, message: str, algorithm: Optional[str] = None, 
                 parameters: Optional[Dict[str, Any]] = None, **kwargs):
        self.algorithm = algorithm
        self.parameters = parameters
        
        context = kwargs.get('context')
        if context:
            if algorithm:
                context.additional_data['algorithm'] = algorithm
            if parameters:
                context.additional_data['parameters'] = parameters
        
        super().__init__(
            message,
            category=ErrorCategory.ALGORITHM,
            severity=ErrorSeverity.MEDIUM,
            recovery_suggestions=[
                "Check input parameters",
                "Verify sequence format",
                "Try with different parameters"
            ],
            **kwargs
        )


class MemoryError(GeneStudioError):
    """Error for memory-related issues."""
    
    def __init__(self, message: str, memory_usage: Optional[int] = None, 
                 dataset_size: Optional[int] = None, **kwargs):
        self.memory_usage = memory_usage
        self.dataset_size = dataset_size
        
        context = kwargs.get('context')
        if context:
            if memory_usage:
                context.additional_data['memory_usage'] = memory_usage
            if dataset_size:
                context.additional_data['dataset_size'] = dataset_size
        
        super().__init__(
            message,
            category=ErrorCategory.MEMORY,
            severity=ErrorSeverity.HIGH,
            recovery_suggestions=[
                "Try with a smaller dataset",
                "Close other applications",
                "Increase available memory"
            ],
            **kwargs
        )


class PermissionError(GeneStudioError):
    """Error for permission-related issues."""
    
    def __init__(self, message: str, resource: Optional[str] = None, 
                 required_permission: Optional[str] = None, **kwargs):
        self.resource = resource
        self.required_permission = required_permission
        
        context = kwargs.get('context')
        if context:
            if resource:
                context.additional_data['resource'] = resource
            if required_permission:
                context.additional_data['required_permission'] = required_permission
        
        super().__init__(
            message,
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.MEDIUM,
            recovery_suggestions=[
                "Check file/folder permissions",
                "Run as administrator if needed",
                "Contact system administrator"
            ],
            **kwargs
        )


class ConfigurationError(GeneStudioError):
    """Error for configuration issues."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, 
                 config_value: Optional[Any] = None, **kwargs):
        self.config_key = config_key
        self.config_value = config_value
        
        context = kwargs.get('context')
        if context:
            if config_key:
                context.additional_data['config_key'] = config_key
            if config_value:
                context.additional_data['config_value'] = str(config_value)
        
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.MEDIUM,
            recovery_suggestions=[
                "Check application settings",
                "Reset to default configuration",
                "Reinstall application if needed"
            ],
            **kwargs
        )


class ErrorHandler:
    """Centralized error handler with logging and recovery."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_counts = {}
        self.recovery_strategies = {}
        self.notification_callbacks = []
    
    def register_recovery_strategy(self, error_type: Type[GeneStudioError], 
                                 strategy: Callable[[GeneStudioError], bool]):
        """Register a recovery strategy for an error type."""
        self.recovery_strategies[error_type] = strategy
    
    def add_notification_callback(self, callback: Callable[[GeneStudioError], None]):
        """Add a callback for error notifications."""
        self.notification_callbacks.append(callback)
    
    def handle_error(self, error: Exception, context: Optional[ErrorContext] = None,
                    suppress: bool = False) -> GeneStudioError:
        """Handle an error with logging and recovery attempts."""
        # Convert to GeneStudioError if needed
        if isinstance(error, GeneStudioError):
            gs_error = error
        else:
            gs_error = GeneStudioError(
                message=str(error),
                context=context,
                cause=error
            )
        
        # Log the error
        self._log_error(gs_error)
        
        # Track error counts
        error_key = f"{gs_error.category.value}:{gs_error.__class__.__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Attempt recovery
        recovered = self._attempt_recovery(gs_error)
        
        # Notify callbacks
        for callback in self.notification_callbacks:
            try:
                callback(gs_error)
            except Exception as e:
                self.logger.error(f"Error in notification callback: {e}")
        
        # Re-raise if not suppressed and not recovered
        if not suppress and not recovered:
            raise gs_error
        
        return gs_error
    
    def _log_error(self, error: GeneStudioError):
        """Log error with appropriate level."""
        error_dict = error.to_dict()
        
        # Remove 'message' key to avoid conflict with LogRecord
        log_extra = {k: v for k, v in error_dict.items() if k != 'message'}
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error.message}", extra=log_extra)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"ERROR: {error.message}", extra=log_extra)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"WARNING: {error.message}", extra=log_extra)
        else:
            self.logger.info(f"INFO: {error.message}", extra=log_extra)
    
    def _attempt_recovery(self, error: GeneStudioError) -> bool:
        """Attempt to recover from error using registered strategies."""
        error_type = type(error)
        
        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](error)
            except Exception as e:
                self.logger.error(f"Recovery strategy failed: {e}")
        
        return False
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_counts': self.error_counts.copy(),
            'most_common': sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def clear_statistics(self):
        """Clear error statistics."""
        self.error_counts.clear()


# Global error handler instance
_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return _error_handler


def handle_error(error: Exception, context: Optional[ErrorContext] = None,
                suppress: bool = False) -> GeneStudioError:
    """Handle an error using the global error handler."""
    return _error_handler.handle_error(error, context, suppress)


def with_error_handling(operation: str = None, component: str = None,
                       suppress: bool = False, reraise: bool = True):
    """Decorator for automatic error handling."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context = ErrorContext(
                operation=operation or func.__name__,
                component=component or func.__module__
            )
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                gs_error = handle_error(e, context, suppress)
                if reraise and not suppress:
                    raise gs_error
                return None
        
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default=None, 
                context: Optional[ErrorContext] = None, **kwargs) -> Tuple[bool, Any]:
    """Safely execute a function with error handling."""
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        handle_error(e, context, suppress=True)
        return False, default


def create_error_context(operation: str, component: str, **kwargs) -> ErrorContext:
    """Create an error context with additional data."""
    return ErrorContext(
        operation=operation,
        component=component,
        additional_data=kwargs
    )


# Error handling utilities for common patterns
def validate_not_none(value: Any, field_name: str, context: Optional[ErrorContext] = None):
    """Validate that a value is not None."""
    if value is None:
        raise ValidationError(
            f"{field_name} cannot be None",
            field=field_name,
            value=value,
            context=context
        )


def validate_not_empty(value: str, field_name: str, context: Optional[ErrorContext] = None):
    """Validate that a string is not empty."""
    if not value or not value.strip():
        raise ValidationError(
            f"{field_name} cannot be empty",
            field=field_name,
            value=value,
            context=context
        )


def validate_file_exists(filepath: str, context: Optional[ErrorContext] = None):
    """Validate that a file exists."""
    from pathlib import Path
    
    if not Path(filepath).exists():
        raise FileSystemError(
            f"File not found: {filepath}",
            filepath=filepath,
            operation="file_check",
            context=context
        )


def validate_memory_usage(current_usage: int, max_usage: int, 
                         context: Optional[ErrorContext] = None):
    """Validate memory usage is within limits."""
    if current_usage > max_usage:
        raise MemoryError(
            f"Memory usage ({current_usage} bytes) exceeds limit ({max_usage} bytes)",
            memory_usage=current_usage,
            context=context
        )


def handle_network_error_silently(func: Callable, *args, **kwargs) -> Optional[Any]:
    """Handle network errors silently for non-critical operations."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # Create network error but suppress it
        network_error = NetworkError(
            f"Network operation failed: {e}",
            cause=e
        )
        handle_error(network_error, suppress=True)
        return None