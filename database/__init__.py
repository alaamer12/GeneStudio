"""Database package for GeneStudio Pro."""

from .db_manager import DatabaseManager, DatabaseError

__all__ = ['DatabaseManager', 'DatabaseError']