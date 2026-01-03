"""Base service abstract class with logging and error handling."""

from abc import ABC
from typing import Any, Tuple, Callable, Optional, TypeVar, Generic
from repositories.base_repository import BaseRepository, RepositoryError
import logging
import time

from utils.error_handling import (
    GeneStudioError, ValidationError, ErrorContext, 
    get_error_handler, with_error_handling
)
from utils.resource_manager import get_resource_manager, with_resource_management
from utils.validators import get_validation_manager

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """Abstract base class for all services."""
    
    def __init__(self, repository: BaseRepository[T]):
        """Initialize service with repository."""
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @with_resource_management("service_operation")
    def execute_with_logging(self, operation: Callable[[], Any], operation_name: str = "operation") -> Tuple[bool, Any]:
        """
        Execute an operation with logging and error handling.
        
        Args:
            operation: Function to execute
            operation_name: Name of the operation for logging
            
        Returns:
            Tuple of (success, result_or_error_message)
        """
        start_time = time.time()
        
        context = ErrorContext(
            operation=operation_name,
            component=self.__class__.__name__
        )
        
        try:
            self.logger.info(f"Starting {operation_name}")
            
            # Check resource limits before operation
            resource_manager = get_resource_manager()
            violations = resource_manager.check_resource_limits()
            if violations:
                self.logger.warning(f"Resource limit violations detected: {violations}")
            
            result = operation()
            
            execution_time = time.time() - start_time
            self.logger.info(f"Completed {operation_name} in {execution_time:.3f}s")
            
            return True, result
            
        except ValidationError as e:
            execution_time = time.time() - start_time
            self.logger.warning(f"Validation error in {operation_name} after {execution_time:.3f}s: {e}")
            get_error_handler().handle_error(e, context, suppress=True)
            return False, e.user_message
            
        except RepositoryError as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Repository error in {operation_name} after {execution_time:.3f}s: {e}")
            get_error_handler().handle_error(e, context, suppress=True)
            return False, f"Data access error: {e}"
            
        except ServiceError as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Service error in {operation_name} after {execution_time:.3f}s: {e}")
            get_error_handler().handle_error(e, context, suppress=True)
            return False, str(e)
            
        except GeneStudioError as e:
            execution_time = time.time() - start_time
            self.logger.error(f"GeneStudio error in {operation_name} after {execution_time:.3f}s: {e}")
            get_error_handler().handle_error(e, context, suppress=True)
            return False, e.user_message
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Unexpected error in {operation_name} after {execution_time:.3f}s: {e}", exc_info=True)
            
            # Convert to GeneStudio error
            gs_error = GeneStudioError(
                message=f"Unexpected error in {operation_name}: {e}",
                context=context,
                cause=e
            )
            get_error_handler().handle_error(gs_error, context, suppress=True)
            return False, gs_error.user_message
    
    def validate_input(self, data: Any, validation_rules: Optional[Callable[[Any], None]] = None) -> Tuple[bool, str]:
        """
        Validate input data using the validation manager.
        
        Args:
            data: Data to validate
            validation_rules: Optional custom validation function
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        context = ErrorContext(
            operation="input_validation",
            component=self.__class__.__name__
        )
        
        try:
            # Basic validation
            if data is None:
                raise ValidationError("Data cannot be None", context=context)
            
            # Custom validation if provided
            if validation_rules:
                validation_rules(data)
            
            # Model validation if data has validate method
            if hasattr(data, 'validate'):
                data.validate()
            
            # Use validation manager for structured validation
            validation_manager = get_validation_manager()
            if hasattr(data, '__dict__'):
                # Convert object to dict for validation
                data_dict = data.__dict__ if hasattr(data, '__dict__') else {}
                
                # Determine validation type based on class name
                class_name = data.__class__.__name__.lower()
                if 'project' in class_name:
                    result = validation_manager.validate_project(data_dict, context)
                elif 'sequence' in class_name:
                    result = validation_manager.validate_sequence(data_dict, context)
                else:
                    # Generic validation passed
                    return True, ""
                
                if not result.is_valid:
                    error_messages = result.get_error_messages()
                    return False, "; ".join(error_messages)
            
            return True, ""
            
        except ValidationError as e:
            self.logger.warning(f"Validation failed: {e}")
            get_error_handler().handle_error(e, context, suppress=True)
            return False, e.user_message
        except ValueError as e:
            validation_error = ValidationError(f"Value validation failed: {e}", context=context, cause=e)
            get_error_handler().handle_error(validation_error, context, suppress=True)
            return False, validation_error.user_message
        except Exception as e:
            validation_error = ValidationError(f"Unexpected validation error: {e}", context=context, cause=e)
            get_error_handler().handle_error(validation_error, context, suppress=True)
            return False, validation_error.user_message
    
    def log_operation(self, operation: str, entity_id: Optional[int] = None, **kwargs):
        """Log an operation for audit purposes."""
        extra_info = {
            'operation': operation,
            'entity_id': entity_id,
            **kwargs
        }
        self.logger.info(f"Operation: {operation}", extra=extra_info)
    
    def handle_not_found(self, entity_type: str, entity_id: int) -> Tuple[bool, str]:
        """Handle not found scenarios consistently."""
        message = f"{entity_type} with ID {entity_id} not found"
        self.logger.warning(message)
        return False, message
    
    def handle_validation_error(self, error: Exception, operation: str) -> Tuple[bool, str]:
        """Handle validation errors consistently."""
        message = f"Validation failed for {operation}: {error}"
        self.logger.warning(message)
        return False, str(error)
    
    def handle_repository_error(self, error: Exception, operation: str) -> Tuple[bool, str]:
        """Handle repository errors consistently."""
        message = f"Data access failed for {operation}: {error}"
        self.logger.error(message)
        return False, "A database error occurred. Please try again."
    
    def handle_unexpected_error(self, error: Exception, operation: str) -> Tuple[bool, str]:
        """Handle unexpected errors consistently."""
        message = f"Unexpected error in {operation}: {error}"
        self.logger.error(message, exc_info=True)
        return False, "An unexpected error occurred. Please contact support."
    
    def create_entity(self, entity: T) -> Tuple[bool, T]:
        """Create an entity with validation and error handling."""
        def operation():
            # Validate input
            is_valid, error_msg = self.validate_input(entity)
            if not is_valid:
                raise ValidationError(error_msg)
            
            # Create entity
            created_entity = self.repository.create(entity)
            self.log_operation("create", getattr(created_entity, 'id', None))
            
            return created_entity
        
        return self.execute_with_logging(operation, f"create {self.__class__.__name__.replace('Service', '').lower()}")
    
    def get_entity(self, entity_id: int) -> Tuple[bool, Optional[T]]:
        """Get an entity by ID with error handling."""
        def operation():
            entity = self.repository.get_by_id(entity_id)
            if entity is None:
                raise EntityNotFoundError(f"Entity with ID {entity_id} not found")
            
            self.log_operation("get", entity_id)
            return entity
        
        return self.execute_with_logging(operation, f"get {self.__class__.__name__.replace('Service', '').lower()}")
    
    def update_entity(self, entity: T) -> Tuple[bool, bool]:
        """Update an entity with validation and error handling."""
        def operation():
            # Validate input
            is_valid, error_msg = self.validate_input(entity)
            if not is_valid:
                raise ValidationError(error_msg)
            
            # Update entity
            success = self.repository.update(entity)
            if not success:
                raise ServiceError("Failed to update entity")
            
            self.log_operation("update", getattr(entity, 'id', None))
            return success
        
        return self.execute_with_logging(operation, f"update {self.__class__.__name__.replace('Service', '').lower()}")
    
    def delete_entity(self, entity_id: int) -> Tuple[bool, bool]:
        """Delete an entity with error handling."""
        def operation():
            # Check if entity exists
            if not self.repository.exists(entity_id):
                raise EntityNotFoundError(f"Entity with ID {entity_id} not found")
            
            # Delete entity
            success = self.repository.delete(entity_id)
            if not success:
                raise ServiceError("Failed to delete entity")
            
            self.log_operation("delete", entity_id)
            return success
        
        return self.execute_with_logging(operation, f"delete {self.__class__.__name__.replace('Service', '').lower()}")


class ServiceError(Exception):
    """Custom exception for service operations."""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class EntityNotFoundError(Exception):
    """Custom exception for entity not found errors."""
    pass