"""Logging utility with file rotation and structured logging."""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record):
        """Format log record with structured data."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'operation'):
            log_data['operation'] = record.operation
        if hasattr(record, 'duration'):
            log_data['duration'] = record.duration
            
        return json.dumps(log_data)


class LoggerManager:
    """Manages application logging configuration."""
    
    _configured = False
    
    @classmethod
    def setup_logging(
        cls,
        log_level: str = "INFO",
        log_dir: str = "logs",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True,
        structured_format: bool = False
    ):
        """
        Set up application logging.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files
            max_file_size: Maximum size of each log file in bytes
            backup_count: Number of backup files to keep
            console_output: Whether to output logs to console
            structured_format: Whether to use structured JSON format
        """
        if cls._configured:
            return
        
        # Create log directory
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / "genestudio.log",
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
        
        # Set formatters
        if structured_format:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        if console_output:
            console_formatter = logging.Formatter(
                '%(levelname)s - %(name)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # Create separate error log
        error_handler = logging.handlers.RotatingFileHandler(
            log_path / "genestudio_errors.log",
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
        
        cls._configured = True
        
        # Log startup message
        logger = logging.getLogger(__name__)
        logger.info("Logging system initialized")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance."""
        return logging.getLogger(name)
    
    @staticmethod
    def log_operation(
        logger: logging.Logger,
        operation: str,
        duration: Optional[float] = None,
        **kwargs
    ):
        """Log an operation with structured data."""
        extra = {'operation': operation}
        if duration is not None:
            extra['duration'] = duration
        extra.update(kwargs)
        
        logger.info(f"Operation: {operation}", extra=extra)
    
    @staticmethod
    def log_error(
        logger: logging.Logger,
        error: Exception,
        operation: Optional[str] = None,
        **kwargs
    ):
        """Log an error with structured data."""
        extra = {}
        if operation:
            extra['operation'] = operation
        extra.update(kwargs)
        
        logger.error(f"Error in {operation or 'unknown operation'}: {error}", 
                    exc_info=True, extra=extra)


# Convenience functions
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return LoggerManager.get_logger(name)


def setup_logging(**kwargs):
    """Set up logging with default configuration."""
    LoggerManager.setup_logging(**kwargs)


def log_operation(operation: str, duration: Optional[float] = None, **kwargs):
    """Log an operation."""
    logger = logging.getLogger('genestudio.operations')
    LoggerManager.log_operation(logger, operation, duration, **kwargs)


def log_error(error: Exception, operation: Optional[str] = None, **kwargs):
    """Log an error."""
    logger = logging.getLogger('genestudio.errors')
    LoggerManager.log_error(logger, error, operation, **kwargs)