"""Database manager for GeneStudio Pro using DuckDB."""

import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
import duckdb
import logging

from utils.error_handling import (
    DatabaseError, ErrorContext, get_error_handler, 
    with_error_handling
)
from utils.resource_manager import get_resource_manager


class DatabaseManager:
    """Manages DuckDB connections and schema operations."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for database manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database manager."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # Use platform-specific directory
        from utils.platform_dirs import get_database_dir
        db_dir = get_database_dir()
        self.db_path = db_dir / "genestudio.db"
        
        self._connection_pool = {}
        self._pool_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Initialize schema on first run
        self.initialize_schema()    

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get a database connection from the pool."""
        thread_id = threading.get_ident()
        
        with self._pool_lock:
            if thread_id not in self._connection_pool:
                try:
                    conn = duckdb.connect(str(self.db_path))
                    self._connection_pool[thread_id] = conn
                    self.logger.debug(f"Created new connection for thread {thread_id}")
                except Exception as e:
                    self.logger.error(f"Failed to create database connection: {e}")
                    raise DatabaseError(f"Failed to connect to database: {e}")
            
            return self._connection_pool[thread_id]
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries."""
        context = ErrorContext(
            operation="database_query",
            component="DatabaseManager",
            additional_data={'query': query[:100]}  # Truncate long queries
        )
        
        try:
            conn = self.get_connection()
            
            # Monitor resource usage
            resource_manager = get_resource_manager()
            resource_manager.memory_monitor.track_object(conn)
            
            result = conn.execute(query, params).fetchall()
            
            # Get column names
            columns = [desc[0] for desc in conn.description] if conn.description else []
            
            # Convert to list of dictionaries
            return [dict(zip(columns, row)) for row in result]
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {query}, params: {params}, error: {e}")
            
            db_error = DatabaseError(
                f"Query execution failed: {e}",
                query=query[:100],  # Truncate for logging
                context=context,
                cause=e
            )
            
            get_error_handler().handle_error(db_error, context, suppress=False)
            raise db_error
    
    def execute_transaction(self, operations: List[Callable]) -> bool:
        """Execute multiple operations in a transaction."""
        conn = self.get_connection()
        try:
            conn.begin()
            
            for operation in operations:
                operation(conn)
            
            conn.commit()
            self.logger.debug(f"Transaction completed successfully with {len(operations)} operations")
            return True
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Transaction failed, rolled back: {e}")
            raise DatabaseError(f"Transaction failed: {e}")    

    def initialize_schema(self) -> None:
        """Initialize database schema."""
        try:
            conn = self.get_connection()
            
            # Create projects table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL DEFAULT 'sequence_analysis',
                    description TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    sequence_count INTEGER DEFAULT 0,
                    analysis_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # Create sequences table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sequences (
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER REFERENCES projects(id),
                    header TEXT NOT NULL,
                    sequence TEXT,
                    sequence_type TEXT DEFAULT 'dna',
                    length INTEGER,
                    gc_percentage REAL,
                    notes TEXT,
                    tags TEXT,
                    file_path TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create analyses table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER REFERENCES projects(id),
                    sequence_id INTEGER REFERENCES sequences(id),
                    analysis_type TEXT NOT NULL,
                    parameters TEXT,
                    results TEXT,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    execution_time REAL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create settings table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    value_type TEXT DEFAULT 'string',
                    category TEXT DEFAULT 'general'
                )
            """)
            
            # Create activity log table for dashboard
            conn.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY,
                    action TEXT NOT NULL,
                    entity_type TEXT,
                    entity_id INTEGER,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sequences_project_id ON sequences(project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_project_id ON analyses(project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_sequence_id ON analyses(sequence_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON activity_log(timestamp)")
            
            self.logger.info("Database schema initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database schema: {e}")
            raise DatabaseError(f"Schema initialization failed: {e}")    

    def backup_database(self, filepath: str) -> bool:
        """Create a backup of the database."""
        try:
            conn = self.get_connection()
            backup_path = Path(filepath)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn.execute(f"EXPORT DATABASE '{backup_path.parent}' (FORMAT PARQUET)")
            self.logger.info(f"Database backup created at {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
    
    def close_all_connections(self):
        """Close all connections in the pool."""
        with self._pool_lock:
            for thread_id, conn in self._connection_pool.items():
                try:
                    conn.close()
                    self.logger.debug(f"Closed connection for thread {thread_id}")
                except Exception as e:
                    self.logger.warning(f"Error closing connection for thread {thread_id}: {e}")
            
            self._connection_pool.clear()


# DatabaseError is imported from utils.error_handling - no need to redefine