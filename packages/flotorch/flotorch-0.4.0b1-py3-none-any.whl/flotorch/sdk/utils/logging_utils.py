import logging
import sys
import inspect
from typing import Optional

# Global flag to track if logging is configured
_logging_configured = False

def _configure_logging_once():
    """Configure logging once globally."""
    global _logging_configured
    if not _logging_configured:
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        
        # Suppress specific loggers completely
        logging.getLogger('httpx').setLevel(logging.ERROR)
        logging.getLogger('google_adk').setLevel(logging.ERROR)
        logging.getLogger('google_adk.google.adk.tools.base_authenticated_tool').setLevel(logging.ERROR)
        # Suppress LiteLLM noisy logs used by CrewAI integrations
        for _name in ('litellm', 'LiteLLM'):
            _logger = logging.getLogger(_name)
            _logger.setLevel(logging.ERROR)
            _logger.propagate = False
        
        _logging_configured = True

def _get_caller_logger() -> logging.Logger:
    """
    Automatically get the logger for the calling module.
    
    Returns:
        Logger instance for the calling module
    """
    # Configure logging once
    _configure_logging_once()
    
    # Get the calling frame (the module that called the logging function)
    # We need to go back 2 frames: 1 for the logging function, 1 for the actual caller
    caller_frame = inspect.currentframe().f_back.f_back
    
    # Get the module name from the calling frame
    if caller_frame and hasattr(caller_frame, 'f_globals'):
        module_name = caller_frame.f_globals.get('__name__', 'unknown')
    else:
        module_name = 'unknown'
    
    # Get logger for this module
    return logging.getLogger(module_name)

def log_object_creation(class_name: str, **kwargs) -> None:
    """
    Log object creation with key parameters.
    
    Args:
        class_name: Name of the class being created
        **kwargs: Key parameters to include in log
    """
    logger = _get_caller_logger()
    params = []
    for key, value in kwargs.items():
        # Mask sensitive information
        if any(sensitive in key.lower() for sensitive in ['key', 'token', 'password', 'secret']):
            value = '***'
        params.append(f"{key}={value}")
    
    param_str = ', '.join(params) if params else 'no parameters'
    logger.info(f"{class_name} initialized ({param_str})")

def log_info(message: str) -> None:
    """
    Log informational messages in a consistent format.
    
    Args:
        message: Information message to log
    """
    logger = _get_caller_logger()
    logger.info(message)

def log_error(operation: str, error: Exception) -> None:
    """
    Log errors in a consistent format.
    
    Args:
        operation: Description of the operation that failed
        error: The exception that occurred
    """
    logger = _get_caller_logger()
    logger.error(f"{operation} failed: {type(error).__name__}: {str(error)}")

def log_warning(message: str) -> None:
    """
    Log warnings in a consistent format.
    
    Args:
        message: Warning message
    """
    logger = _get_caller_logger()
    logger.warning(message) 