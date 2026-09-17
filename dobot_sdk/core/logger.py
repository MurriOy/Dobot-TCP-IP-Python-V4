# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""
Logging module
Provides unified logging functionality for the SDK, supports cross-platform operation (Windows/Ubuntu)
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime


class DobotLogger:
    """
    Dobot SDK logger
    
    Features:
        - Supports multiple log levels: DEBUG, INFO, WARNING, ERROR
        - Simultaneous output to console and log file
        - Automatic log file rotation (max 5 files, 10MB each)
        - Cross-platform compatible (Windows/Ubuntu)
        - Structured log format
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_level: str = "INFO", log_dir: Optional[str] = None):
        """
        Initialize logger
        
        Args:
            log_level: Log level, options: "DEBUG", "INFO", "WARNING", "ERROR"
            log_dir: Log file directory, defaults to logs folder under SDK installation directory
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        
        # Get log directory
        if log_dir is None:
            # Default log directory: SDK installation directory/logs
            sdk_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.log_dir = os.path.join(sdk_dir, 'logs')
        else:
            self.log_dir = log_dir
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Log file name format: dobot_sdk_20260615.log
        today = datetime.now().strftime("%Y%m%d")
        self.log_file = os.path.join(self.log_dir, f"dobot_sdk_{today}.log")
        
        # Create logger
        self.logger = logging.getLogger("dobot_sdk")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self.logger.propagate = False
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # File handler (with rotation)
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,              # Max 5 backups
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Log format
        log_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
        )
        console_handler.setFormatter(log_format)
        file_handler.setFormatter(log_format)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get logger instance"""
        return self.logger
    
    @property
    def log_directory(self) -> str:
        """Get log file directory"""
        return self.log_dir


# Global logging decorator
def log_api_call(func):
    """
    Decorator: Log API call
    
    Automatically logs:
        - Function name called
        - Input parameters
        - Return value
        - Execution time
        - Exception information (if occurred)
    """
    import time
    
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("dobot_sdk")
        start_time = time.time()
        
        # Get call info
        class_name = ""
        if len(args) > 0 and hasattr(args[0], '__class__'):
            class_name = args[0].__class__.__name__ + "."
        
        func_name = class_name + func.__name__
        
        # Format arguments
        args_str = []
        for i, arg in enumerate(args[1:], 1):  # Skip self
            args_str.append(f"arg{i}={arg!r}")
        for k, v in kwargs.items():
            args_str.append(f"{k}={v!r}")
        
        args_str = ", ".join(args_str)
        
        # Log call info
        logger.info(f"API call: {func_name}({args_str})")
        
        try:
            result = func(*args, **kwargs)
            elapsed = (time.time() - start_time) * 1000
            
            # Log return value (limited length)
            result_str = str(result)
            if len(result_str) > 500:
                result_str = result_str[:500] + "..."
            
            logger.debug(f"API return: {func_name} -> {result_str} (elapsed: {elapsed:.2f}ms)")
            
            return result
        
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"API exception: {func_name} -> {type(e).__name__}: {str(e)} (elapsed: {elapsed:.2f}ms)", exc_info=True)
            raise
    
    return wrapper


def get_logger() -> logging.Logger:
    """Convenience function: Get global logger"""
    return DobotLogger().get_logger()


def set_log_level(log_level: str):
    """
    Set global log level
    
    Args:
        log_level: "DEBUG", "INFO", "WARNING", "ERROR"
    """
    logger = DobotLogger(log_level=log_level).get_logger()
    logger.setLevel(getattr(logging, log_level.upper()))
    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)


def get_log_directory() -> str:
    """Get log file storage directory"""
    return DobotLogger().log_directory
