"""Logging utilities for SmartChunkLLM."""

import os
import sys
import json
import logging
import logging.handlers
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from datetime import datetime
from contextlib import contextmanager
import traceback
import functools
import time

try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.traceback import install as install_rich_traceback
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from ..core.types import ProcessingStatus


class SmartChunkLogger:
    """Enhanced logger for SmartChunkLLM."""
    
    def __init__(self, name: str = 'smartchunkllm',
                 level: str = 'INFO',
                 log_dir: Optional[Union[str, Path]] = None,
                 use_rich: bool = True,
                 use_loguru: bool = False,
                 structured: bool = True):
        self.name = name
        self.level = level.upper()
        self.log_dir = Path(log_dir) if log_dir else None
        self.use_rich = use_rich and RICH_AVAILABLE
        self.use_loguru = use_loguru and LOGURU_AVAILABLE
        self.structured = structured
        
        self._setup_logger()
        self._setup_context()
    
    def _setup_logger(self):
        """Setup logger configuration."""
        if self.use_loguru:
            self._setup_loguru()
        else:
            self._setup_standard()
    
    def _setup_loguru(self):
        """Setup Loguru logger."""
        # Remove default handler
        loguru_logger.remove()
        
        # Console handler
        if self.use_rich:
            console_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        else:
            console_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        
        loguru_logger.add(
            sys.stderr,
            format=console_format,
            level=self.level,
            colorize=True
        )
        
        # File handlers
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Main log file
            loguru_logger.add(
                self.log_dir / f"{self.name}.log",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {extra} | {message}",
                level=self.level,
                rotation="10 MB",
                retention="30 days",
                compression="gz"
            )
            
            # Error log file
            loguru_logger.add(
                self.log_dir / f"{self.name}_errors.log",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {extra} | {message}",
                level="ERROR",
                rotation="10 MB",
                retention="90 days",
                compression="gz"
            )
            
            # JSON log file for structured logging
            if self.structured:
                loguru_logger.add(
                    self.log_dir / f"{self.name}_structured.jsonl",
                    format="{message}",
                    level=self.level,
                    rotation="10 MB",
                    retention="30 days",
                    compression="gz",
                    serialize=True
                )
        
        self.logger = loguru_logger
    
    def _setup_standard(self):
        """Setup standard Python logger."""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, self.level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        if self.use_rich:
            console_handler = RichHandler(
                rich_tracebacks=True,
                show_path=True,
                show_time=True
            )
            install_rich_traceback()
        else:
            console_handler = logging.StreamHandler(sys.stderr)
        
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(getattr(logging, self.level))
        self.logger.addHandler(console_handler)
        
        # File handlers
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Main log file with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / f"{self.name}.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(getattr(logging, self.level))
            self.logger.addHandler(file_handler)
            
            # Error log file
            error_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / f"{self.name}_errors.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=10
            )
            error_handler.setFormatter(file_formatter)
            error_handler.setLevel(logging.ERROR)
            self.logger.addHandler(error_handler)
            
            # JSON handler for structured logging
            if self.structured:
                json_handler = logging.handlers.RotatingFileHandler(
                    self.log_dir / f"{self.name}_structured.jsonl",
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5
                )
                json_handler.setFormatter(JSONFormatter())
                json_handler.setLevel(getattr(logging, self.level))
                self.logger.addHandler(json_handler)
    
    def _setup_context(self):
        """Setup logging context."""
        self.context = {
            'session_id': None,
            'request_id': None,
            'user_id': None,
            'component': None,
            'operation': None
        }
    
    def set_context(self, **kwargs):
        """Set logging context.
        
        Args:
            **kwargs: Context key-value pairs
        """
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear logging context."""
        self.context = {
            'session_id': None,
            'request_id': None,
            'user_id': None,
            'component': None,
            'operation': None
        }
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format message with context.
        
        Args:
            message: Log message
            extra: Extra context
        
        Returns:
            Formatted message
        """
        if not self.structured:
            return message
        
        context = {k: v for k, v in self.context.items() if v is not None}
        if extra:
            context.update(extra)
        
        if context:
            context_str = ' | '.join(f"{k}={v}" for k, v in context.items())
            return f"{message} | {context_str}"
        
        return message
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        if self.use_loguru:
            self.logger.debug(message, extra=extra or {})
        else:
            self.logger.debug(self._format_message(message, extra))
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        if self.use_loguru:
            self.logger.info(message, extra=extra or {})
        else:
            self.logger.info(self._format_message(message, extra))
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        if self.use_loguru:
            self.logger.warning(message, extra=extra or {})
        else:
            self.logger.warning(self._format_message(message, extra))
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log error message."""
        if self.use_loguru:
            self.logger.error(message, extra=extra or {})
        else:
            self.logger.error(self._format_message(message, extra), exc_info=exc_info)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        if self.use_loguru:
            self.logger.critical(message, extra=extra or {})
        else:
            self.logger.critical(self._format_message(message, extra))
    
    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log exception with traceback."""
        if self.use_loguru:
            self.logger.exception(message, extra=extra or {})
        else:
            self.logger.exception(self._format_message(message, extra))
    
    def log_processing_status(self, status: ProcessingStatus, 
                            component: str,
                            operation: str,
                            details: Optional[Dict[str, Any]] = None):
        """Log processing status.
        
        Args:
            status: Processing status
            component: Component name
            operation: Operation name
            details: Additional details
        """
        extra = {
            'component': component,
            'operation': operation,
            'status': status.value,
            **(details or {})
        }
        
        message = f"{component}.{operation}: {status.value}"
        
        if status == ProcessingStatus.COMPLETED:
            self.info(message, extra)
        elif status == ProcessingStatus.FAILED:
            self.error(message, extra)
        elif status == ProcessingStatus.IN_PROGRESS:
            self.debug(message, extra)
        else:
            self.info(message, extra)
    
    def log_performance(self, operation: str, 
                       duration: float,
                       component: str,
                       details: Optional[Dict[str, Any]] = None):
        """Log performance metrics.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            component: Component name
            details: Additional details
        """
        extra = {
            'component': component,
            'operation': operation,
            'duration_seconds': duration,
            'performance': True,
            **(details or {})
        }
        
        message = f"Performance: {component}.{operation} completed in {duration:.3f}s"
        
        if duration > 10:  # Slow operation
            self.warning(message, extra)
        else:
            self.info(message, extra)
    
    @contextmanager
    def operation_context(self, component: str, operation: str):
        """Context manager for operation logging.
        
        Args:
            component: Component name
            operation: Operation name
        """
        start_time = time.time()
        old_context = self.context.copy()
        
        try:
            self.set_context(component=component, operation=operation)
            self.log_processing_status(ProcessingStatus.IN_PROGRESS, component, operation)
            yield
            
            duration = time.time() - start_time
            self.log_processing_status(ProcessingStatus.COMPLETED, component, operation)
            self.log_performance(operation, duration, component)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_processing_status(
                ProcessingStatus.FAILED, 
                component, 
                operation, 
                {'error': str(e), 'duration_seconds': duration}
            )
            self.exception(f"Operation failed: {component}.{operation}")
            raise
        
        finally:
            self.context = old_context


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON.
        
        Args:
            record: Log record
        
        Returns:
            JSON formatted string
        """
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(name: str = 'smartchunkllm',
                 level: str = 'INFO',
                 log_dir: Optional[Union[str, Path]] = None,
                 use_rich: bool = True,
                 use_loguru: bool = False,
                 structured: bool = True) -> SmartChunkLogger:
    """Setup logging configuration.
    
    Args:
        name: Logger name
        level: Log level
        log_dir: Log directory
        use_rich: Use Rich for console output
        use_loguru: Use Loguru instead of standard logging
        structured: Enable structured logging
    
    Returns:
        Configured logger
    """
    return SmartChunkLogger(
        name=name,
        level=level,
        log_dir=log_dir,
        use_rich=use_rich,
        use_loguru=use_loguru,
        structured=structured
    )


def get_logger(name: str = 'smartchunkllm') -> SmartChunkLogger:
    """Get logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    # Simple singleton pattern
    if not hasattr(get_logger, '_loggers'):
        get_logger._loggers = {}
    
    if name not in get_logger._loggers:
        get_logger._loggers[name] = setup_logging(name)
    
    return get_logger._loggers[name]


def log_function_call(logger: Optional[SmartChunkLogger] = None,
                     level: str = 'DEBUG',
                     include_args: bool = False,
                     include_result: bool = False):
    """Decorator to log function calls.
    
    Args:
        logger: Logger instance
        level: Log level
        include_args: Include function arguments
        include_result: Include function result
    
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger()
            
            func_name = f"{func.__module__}.{func.__qualname__}"
            
            # Log function entry
            extra = {'function': func_name}
            if include_args:
                extra['args'] = args
                extra['kwargs'] = kwargs
            
            getattr(logger, level.lower())(f"Entering {func_name}", extra)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log function exit
                extra = {
                    'function': func_name,
                    'duration_seconds': duration
                }
                if include_result:
                    extra['result'] = result
                
                getattr(logger, level.lower())(f"Exiting {func_name}", extra)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                extra = {
                    'function': func_name,
                    'duration_seconds': duration,
                    'error': str(e)
                }
                
                logger.error(f"Exception in {func_name}", extra)
                raise
        
        return wrapper
    return decorator


class LogCapture:
    """Context manager to capture log messages."""
    
    def __init__(self, logger_name: str = 'smartchunkllm', level: str = 'DEBUG'):
        self.logger_name = logger_name
        self.level = getattr(logging, level.upper())
        self.records = []
        self.handler = None
    
    def __enter__(self):
        self.handler = logging.Handler()
        self.handler.setLevel(self.level)
        self.handler.emit = self._capture_record
        
        logger = logging.getLogger(self.logger_name)
        logger.addHandler(self.handler)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.handler:
            logger = logging.getLogger(self.logger_name)
            logger.removeHandler(self.handler)
    
    def _capture_record(self, record):
        """Capture log record.
        
        Args:
            record: Log record
        """
        self.records.append(record)
    
    def get_messages(self, level: Optional[str] = None) -> List[str]:
        """Get captured messages.
        
        Args:
            level: Filter by log level
        
        Returns:
            List of log messages
        """
        if level:
            level_num = getattr(logging, level.upper())
            return [record.getMessage() for record in self.records if record.levelno >= level_num]
        
        return [record.getMessage() for record in self.records]
    
    def get_records(self, level: Optional[str] = None) -> List[logging.LogRecord]:
        """Get captured log records.
        
        Args:
            level: Filter by log level
        
        Returns:
            List of log records
        """
        if level:
            level_num = getattr(logging, level.upper())
            return [record for record in self.records if record.levelno >= level_num]
        
        return self.records.copy()
    
    def clear(self):
        """Clear captured records."""
        self.records.clear()


# Global logger instance
_default_logger = None


def get_default_logger() -> SmartChunkLogger:
    """Get default logger instance.
    
    Returns:
        Default logger
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_logging()
    return _default_logger


# Convenience functions using default logger
def debug(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log debug message using default logger."""
    get_default_logger().debug(message, extra)


def info(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log info message using default logger."""
    get_default_logger().info(message, extra)


def warning(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log warning message using default logger."""
    get_default_logger().warning(message, extra)


def error(message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
    """Log error message using default logger."""
    get_default_logger().error(message, extra, exc_info)


def critical(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log critical message using default logger."""
    get_default_logger().critical(message, extra)


def exception(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log exception using default logger."""
    get_default_logger().exception(message, extra)


def log_performance(operation: str, 
                   duration: float,
                   component: str,
                   details: Optional[Dict[str, Any]] = None):
    """Log performance metrics using default logger.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        component: Component name
        details: Additional details
    """
    get_default_logger().log_performance(operation, duration, component, details)


def log_error(message: str, 
              component: str,
              operation: str = None,
              error: Exception = None,
              details: Optional[Dict[str, Any]] = None):
    """Log error message using default logger.
    
    Args:
        message: Error message
        component: Component name
        operation: Operation name (optional)
        error: Exception object (optional)
        details: Additional details
    """
    extra = {
        'component': component,
        'error': True,
        **(details or {})
    }
    
    if operation:
        extra['operation'] = operation
    
    if error:
        extra['exception'] = str(error)
        extra['exception_type'] = type(error).__name__
    
    get_default_logger().error(message, extra, exc_info=bool(error))


class LogManager:
    """Log manager for centralized logging control."""
    
    def __init__(self):
        self._loggers = {}
        self._default_config = {
            'level': 'INFO',
            'log_dir': None,
            'use_rich': True,
            'use_loguru': False,
            'structured': True
        }
    
    def get_logger(self, name: str = 'smartchunkllm', **config) -> SmartChunkLogger:
        """Get or create logger instance.
        
        Args:
            name: Logger name
            **config: Logger configuration overrides
        
        Returns:
            Logger instance
        """
        if name not in self._loggers:
            logger_config = {**self._default_config, **config}
            self._loggers[name] = SmartChunkLogger(name=name, **logger_config)
        
        return self._loggers[name]
    
    def configure_default(self, **config):
        """Configure default logger settings.
        
        Args:
            **config: Default configuration
        """
        self._default_config.update(config)
    
    def set_level(self, level: str, logger_name: str = None):
        """Set log level for logger(s).
        
        Args:
            level: Log level
            logger_name: Specific logger name, or None for all
        """
        if logger_name:
            if logger_name in self._loggers:
                self._loggers[logger_name].set_level(level)
        else:
            for logger in self._loggers.values():
                logger.set_level(level)
    
    def clear_loggers(self):
        """Clear all logger instances."""
        self._loggers.clear()
    
    def get_all_loggers(self) -> Dict[str, SmartChunkLogger]:
        """Get all logger instances.
        
        Returns:
            Dictionary of logger instances
        """
        return self._loggers.copy()


# Global log manager instance
_log_manager = LogManager()