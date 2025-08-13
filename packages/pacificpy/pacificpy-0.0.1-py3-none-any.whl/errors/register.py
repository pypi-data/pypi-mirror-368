"""
Custom HTTP exception registration API.

This module provides an API for registering custom exception handlers,
similar to Starlette/FastAPI.
"""

from typing import Callable, Dict, Type, Union
from starlette.requests import Request
from starlette.responses import Response
from .http import HTTPException

class ExceptionHandlerRegistry:
    """Registry for custom exception handlers."""
    
    def __init__(self):
        """Initialize the exception handler registry."""
        self._handlers: Dict[Type[Exception], Callable] = {}
    
    def add_exception_handler(
        self,
        exc_class: Type[Exception],
        handler: Callable[[Request, Exception], Union[Response, HTTPException]]
    ) -> None:
        """
        Register a custom exception handler.
        
        Args:
            exc_class: The exception class to handle
            handler: The handler function
        """
        self._handlers[exc_class] = handler
    
    def get_handler(self, exc: Exception) -> Callable:
        """
        Get the handler for an exception.
        
        Args:
            exc: The exception instance
            
        Returns:
            The handler function, or None if no handler is registered
        """
        # Try direct match first
        if type(exc) in self._handlers:
            return self._handlers[type(exc)]
        
        # Try subclass matching
        for exc_class, handler in self._handlers.items():
            if isinstance(exc, exc_class):
                return handler
        
        return None

# Global exception handler registry
_exception_handler_registry = ExceptionHandlerRegistry()

def add_exception_handler(
    exc_class: Type[Exception],
    handler: Callable[[Request, Exception], Union[Response, HTTPException]]
) -> None:
    """
    Register a custom exception handler globally.
    
    Args:
        exc_class: The exception class to handle
        handler: The handler function
    """
    _exception_handler_registry.add_exception_handler(exc_class, handler)

def get_exception_handler(exc: Exception) -> Callable:
    """
    Get the registered handler for an exception.
    
    Args:
        exc: The exception instance
        
    Returns:
        The handler function, or None if no handler is registered
    """
    return _exception_handler_registry.get_handler(exc)