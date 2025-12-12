"""Base repository abstract class with CRUD interface."""

from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, TypeVar, Generic
from database.db_manager import DatabaseManager
from utils.error_handling import DatabaseError
import logging

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base class for all repositories."""
    
    def __init__(self):
        """Initialize repository with database manager."""
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete an entity by ID."""
        pass
    
    @abstractmethod
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List entities with optional filters."""
        pass
    
    def exists(self, entity_id: int) -> bool:
        """Check if entity exists."""
        try:
            entity = self.get_by_id(entity_id)
            return entity is not None
        except Exception as e:
            self.logger.error(f"Error checking entity existence: {e}")
            return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters."""
        try:
            entities = self.list(filters)
            return len(entities)
        except Exception as e:
            self.logger.error(f"Error counting entities: {e}")
            return 0
    
    def _execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a database query safely."""
        try:
            return self.db_manager.execute_query(query, params)
        except DatabaseError as e:
            self.logger.error(f"Database query failed: {query}, params: {params}, error: {e}")
            raise RepositoryError(f"Database operation failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in query: {query}, params: {params}, error: {e}")
            raise RepositoryError(f"Unexpected database error: {e}")
    
    def _execute_transaction(self, operations: List[callable]) -> bool:
        """Execute multiple operations in a transaction."""
        try:
            return self.db_manager.execute_transaction(operations)
        except DatabaseError as e:
            self.logger.error(f"Transaction failed: {e}")
            raise RepositoryError(f"Transaction failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in transaction: {e}")
            raise RepositoryError(f"Unexpected transaction error: {e}")
    
    def _build_where_clause(self, filters: Optional[Dict[str, Any]]) -> tuple[str, tuple]:
        """Build WHERE clause from filters."""
        if not filters:
            return "", ()
        
        conditions = []
        params = []
        
        for key, value in filters.items():
            if value is not None:
                conditions.append(f"{key} = ?")
                params.append(value)
        
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            return where_clause, tuple(params)
        
        return "", ()
    
    def _build_order_clause(self, order_by: Optional[str] = None, order_desc: bool = False) -> str:
        """Build ORDER BY clause."""
        if not order_by:
            return ""
        
        direction = "DESC" if order_desc else "ASC"
        return f" ORDER BY {order_by} {direction}"
    
    def _build_limit_clause(self, limit: Optional[int] = None, offset: Optional[int] = None) -> str:
        """Build LIMIT clause."""
        if limit is None:
            return ""
        
        clause = f" LIMIT {limit}"
        if offset is not None:
            clause += f" OFFSET {offset}"
        
        return clause


class RepositoryError(Exception):
    """Custom exception for repository operations."""
    pass