"""Database manager for GeneStudio Pro using DuckDB."""

import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
import duckdb
import logging


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
        self.db_path = Path("data/genestudio.db")
        self.db_path.parent.mkdir(exist_ok=True)
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
        try:
            conn = self.get_connection()
            result = conn.execute(query, params).fetchall()
            
            # Get column names
            columns = [desc[0] for desc in conn.description] if conn.description else []
            
            # Convert to list of dictionaries
            return [dict(zip(columns, row)) for row in result]
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {query}, params: {params}, error: {e}")
            raise DatabaseError(f"Query execution failed: {e}")
    
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
                    metadata JSON
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
                    parameters JSON,
                    results JSON,
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


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass