"""
Template context processors for PacificPy.

This module provides an API for registering context processors
that add global variables to template contexts.
"""

from typing import Callable, Dict, Any, List
from starlette.requests import Request

# Global context processors registry
_context_processors: List[Callable[[Request], Dict[str, Any]]] = []

def register_context_processor(processor: Callable[[Request], Dict[str, Any]]) -> None:
    """
    Register a context processor.
    
    Args:
        processor: A function that takes a request and returns a dict of context variables
    """
    _context_processors.append(processor)

def get_context_processors() -> List[Callable[[Request], Dict[str, Any]]]:
    """
    Get all registered context processors.
    
    Returns:
        A list of context processor functions
    """
    return _context_processors

def clear_context_processors() -> None:
    """Clear all registered context processors."""
    _context_processors.clear()

# Built-in context processors
def request_context_processor(request: Request) -> Dict[str, Any]:
    """
    Context processor that adds request information to the template context.
    
    Args:
        request: The request object
        
    Returns:
        A dictionary with request context
    """
    return {
        "request": request,
        "url": str(request.url),
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params),
    }

def user_context_processor(request: Request) -> Dict[str, Any]:
    """
    Context processor that adds user information to the template context.
    
    Args:
        request: The request object
        
    Returns:
        A dictionary with user context
    """
    user = getattr(request.state, "user", None)
    return {
        "user": user,
        "is_authenticated": user is not None,
    }

def session_context_processor(request: Request) -> Dict[str, Any]:
    """
    Context processor that adds session information to the template context.
    
    Args:
        request: The request object
        
    Returns:
        A dictionary with session context
    """
    session = getattr(request.state, "session", None)
    return {
        "session": session.data if session else {},
    }

def security_context_processor(request: Request) -> Dict[str, Any]:
    """
    Context processor that adds security-related information to the template context.
    
    Args:
        request: The request object
        
    Returns:
        A dictionary with security context
    """
    csp_nonce = getattr(request.state, "csp_nonce", None)
    return {
        "csp_nonce": csp_nonce,
    }

# Default context processors
DEFAULT_CONTEXT_PROCESSORS = [
    request_context_processor,
    user_context_processor,
    session_context_processor,
    security_context_processor,
]

def register_default_context_processors() -> None:
    """Register the default context processors."""
    for processor in DEFAULT_CONTEXT_PROCESSORS:
        register_context_processor(processor)

# Context processor for template engine integration
def run_context_processors(request: Request) -> Dict[str, Any]:
    """
    Run all registered context processors and combine their results.
    
    Args:
        request: The request object
        
    Returns:
        A dictionary with combined context from all processors
    """
    context = {}
    
    for processor in _context_processors:
        try:
            processor_context = processor(request)
            if processor_context:
                context.update(processor_context)
        except Exception:
            # Don't let one processor error break the whole context
            pass
    
    return context

# Decorator for creating context processors
def context_processor(func: Callable[[Request], Dict[str, Any]]) -> Callable[[Request], Dict[str, Any]]:
    """
    Decorator for creating context processors.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    register_context_processor(func)
    return func