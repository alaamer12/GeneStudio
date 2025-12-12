"""Base service abstract class with logging and error handling."""

from abc import ABC
from typing import Any, Tuple, Callable, Optional, TypeVar, Generic
from repositories.base_repository import BaseRepository, RepositoryError
import logging
import time

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """Abstract base class for all services."""
    
    def __init__(self, repository: BaseRepository[T]):
        """Initialize service with repository."""
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)
    
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
        
        try:
            self.logger.info(f"Starting {operation_name}")
            result = operation()
            
            execution_time = time.time() - start_time
            self.logger.info(f"Completed {operation_name} in {execution_time:.3f}s")
            
            return True, result
            
        except ValidationError as e:
            execution_time = time.time() - start_time
            self.logger.warning(f"Validation error in {operation_name} after {execution_time:.3f}s: {e}")
            return False, f"Validation error: {e}"
            
        except RepositoryError as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Repository error in {operation_name} after {execution_time:.3f}s: {e}")
            return False, f"Data access error: {e}"
            
        except ServiceError as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Service error in {operation_name} after {execution_time:.3f}s: {e}")
            return False, str(e)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Unexpected error in {operation_name} after {execution_time:.3f}s: {e}", exc_info=True)
            return False, f"An unexpected error occurred: {e}"
    
    def validate_input(self, data: Any, validation_rules: Optional[Callable[[Any], None]] = None) -> Tuple[bool, str]:
        """
        Validate input data.
        
        Args:
            data: Data to validate
            validation_rules: Optional custom validation function
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic validation
            if data is None:
                return False, "Data cannot be None"
            
            # Custom validation if provided
            if validation_rules:
                validation_rules(data)
            
            # Model validation if data has validate method
            if hasattr(data, 'validate'):
                data.validate()
            
            return True, ""
            
        except ValidationError as e:
            self.logger.warning(f"Validation failed: {e}")
            return False, str(e)
        except ValueError as e:
            self.logger.warning(f"Value validation failed: {e}")
            return False, str(e)
        except Exception as e:
            self.logger.error(f"Unexpected validation error: {e}")
            return False, f"Validation error: {e}"
    
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