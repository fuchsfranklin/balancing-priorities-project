"""
Logging utilities for the Balancing Priorities Project.

This module provides centralized logging configuration and utilities
for consistent logging across the project.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration for the project.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        console_output: Whether to output logs to console
        format_string: Custom format string for log messages
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("balancing_priorities")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"balancing_priorities.{name}")

class LoggingContext:
    """Context manager for temporary logging configuration."""
    
    def __init__(self, level: str):
        """
        Initialize logging context.
        
        Args:
            level: Temporary logging level
        """
        self.level = level
        self.original_level = None
    
    def __enter__(self):
        """Enter the context."""
        logger = logging.getLogger("balancing_priorities")
        self.original_level = logger.level
        logger.setLevel(getattr(logging, self.level.upper()))
        return logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        if self.original_level is not None:
            logger = logging.getLogger("balancing_priorities")
            logger.setLevel(self.original_level)

def log_execution_time(func):
    """
    Decorator to log function execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {str(e)}")
            raise
    
    return wrapper

def log_dataframe_info(df, name: str = "DataFrame"):
    """
    Log information about a DataFrame.
    
    Args:
        df: Pandas DataFrame
        name: Name for the DataFrame in logs
    """
    logger = get_logger(__name__)
    
    logger.info(f"{name} shape: {df.shape}")
    logger.info(f"{name} columns: {list(df.columns)}")
    logger.info(f"{name} date range: {df.index[0]} to {df.index[-1]}" if hasattr(df.index, 'dtype') and 'datetime' in str(df.index.dtype) else "Non-datetime index")
    
    # Check for missing values
    missing_values = df.isnull().sum()
    if missing_values.sum() > 0:
        logger.warning(f"{name} missing values: {missing_values[missing_values > 0].to_dict()}")
    else:
        logger.info(f"{name} has no missing values")

class ProgressLogger:
    """Simple progress logger for long-running operations."""
    
    def __init__(self, total: int, name: str = "Operation", log_interval: int = 10):
        """
        Initialize progress logger.
        
        Args:
            total: Total number of items to process
            name: Name of the operation
            log_interval: Log progress every N percent
        """
        self.total = total
        self.name = name
        self.log_interval = log_interval
        self.current = 0
        self.last_logged_percent = 0
        self.start_time = datetime.now()
        self.logger = get_logger(__name__)
    
    def update(self, increment: int = 1):
        """
        Update progress.
        
        Args:
            increment: Number of items processed
        """
        self.current += increment
        percent = int((self.current / self.total) * 100)
        
        if percent >= self.last_logged_percent + self.log_interval or self.current == self.total:
            elapsed = datetime.now() - self.start_time
            if self.current < self.total:
                rate = self.current / elapsed.total_seconds()
                remaining_items = self.total - self.current
                eta = remaining_items / rate if rate > 0 else 0
                self.logger.info(f"{self.name}: {percent}% complete ({self.current}/{self.total}), ETA: {eta:.0f}s")
            else:
                self.logger.info(f"{self.name}: Complete! ({self.current}/{self.total}) in {elapsed.total_seconds():.1f}s")
            
            self.last_logged_percent = percent

# Initialize default logging
def init_project_logging():
    """Initialize default logging for the project."""
    from ..config.settings import LOG_LEVEL, LOG_FILE
    
    return setup_logging(
        log_level=LOG_LEVEL,
        log_file=LOG_FILE,
        console_output=True
    )
