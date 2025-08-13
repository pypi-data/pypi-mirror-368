"""
Exception converters for built-in Python exceptions.

This module provides utilities for converting built-in Python exceptions
like ValueError and KeyError to appropriate HTTP exceptions.
"""

from typing import Dict, Type, Callable
from .http import BadRequest, NotFound, InternalServerError

# Default mapping of built-in exceptions to HTTP exceptions
DEFAULT_EXCEPTION_MAPPING = {
    ValueError: BadRequest,
    KeyError: BadRequest,
    AttributeError: BadRequest,
    TypeError: BadRequest,
    IndexError: NotFound,
    FileNotFoundError: NotFound,
}

class ExceptionConverter:
    """Converter for built-in Python exceptions to HTTP exceptions."""
    
    def __init__(self, exception_mapping: Dict[Type[Exception], Type[Exception]] = None):
        """
        Initialize the exception converter.
        
        Args:
            exception_mapping: Custom mapping of exceptions to HTTP exceptions
        """
        self.exception_mapping = exception_mapping or DEFAULT_EXCEPTION_MAPPING
    
    def convert(self, exc: Exception) -> Exception:
        """
        Convert a built-in exception to an HTTP exception.
        
        Args:
            exc: The exception to convert
            
        Returns:
            An HTTP exception
        """
        # Try direct match
        if type(exc) in self.exception_mapping:
            http_exception_class = self.exception_mapping[type(exc)]
            return http_exception_class(str(exc))
        
        # Try subclass matching
        for exc_class, http_exception_class in self.exception_mapping.items():
            if isinstance(exc, exc_class):
                return http_exception_class(str(exc))
        
        # If no mapping found, return the original exception
        return exc
    
    def add_mapping(self, py_exception: Type[Exception], http_exception: Type[Exception]) -> None:
        """
        Add a custom exception mapping.
        
        Args:
            py_exception: The built-in Python exception class
            http_exception: The HTTP exception class to map to
        """
        self.exception_mapping[py_exception] = http_exception

# Global exception converter instance
_converter = ExceptionConverter()

def convert_exception(exc: Exception) -> Exception:
    """
    Convert a built-in exception to an HTTP exception using the global converter.
    
    Args:
        exc: The exception to convert
        
    Returns:
        An HTTP exception
    """
    return _converter.convert(exc)

def add_exception_mapping(py_exception: Type[Exception], http_exception: Type[Exception]) -> None:
    """
    Add a custom exception mapping to the global converter.
    
    Args:
        py_exception: The built-in Python exception class
        http_exception: The HTTP exception class to map to
    """
    _converter.add_mapping(py_exception, http_exception)