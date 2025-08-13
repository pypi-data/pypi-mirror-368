"""
Global exception handler for PacificPy.

This module provides a unified exception handler that catches all exceptions,
converts them to JSON responses with trace IDs, and conditionally includes
stack traces based on DEBUG settings.
"""

import traceback
import uuid
from typing import Any, Dict, Optional
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send
from .http import HTTPException
from ..validation.errors import format_validation_error

async def global_exception_handler(request: Request, exc: Exception) -> Response:
    """
    Global exception handler that converts exceptions to JSON responses.
    
    Args:
        request: The incoming request
        exc: The exception that was raised
        
    Returns:
        A JSON response with error details
    """
    # Generate a trace ID for this error
    trace_id = str(uuid.uuid4())
    
    # Check if debug mode is enabled
    debug = getattr(request.app, "debug", False)
    
    # Handle different types of exceptions
    if isinstance(exc, HTTPException):
        return _handle_http_exception(exc, trace_id, debug)
    elif isinstance(exc, ValidationError):
        return _handle_validation_error(exc, trace_id, debug)
    else:
        return _handle_generic_exception(exc, trace_id, debug)

def _handle_http_exception(
    exc: HTTPException,
    trace_id: str,
    debug: bool
) -> JSONResponse:
    """Handle HTTPException instances."""
    content = {
        "detail": exc.detail,
        "trace_id": trace_id
    }
    
    # Add stack trace in debug mode
    if debug and exc.status_code >= 500:
        content["stacktrace"] = traceback.format_exc()
    
    return JSONResponse(
        content=content,
        status_code=exc.status_code,
        headers=exc.headers
    )

def _handle_validation_error(
    exc: ValidationError,
    trace_id: str,
    debug: bool
) -> JSONResponse:
    """Handle Pydantic ValidationError instances."""
    content = {
        "detail": format_validation_error(exc)["detail"],
        "trace_id": trace_id
    }
    
    # Add stack trace in debug mode
    if debug:
        content["stacktrace"] = traceback.format_exc()
    
    return JSONResponse(
        content=content,
        status_code=400
    )

def _handle_generic_exception(
    exc: Exception,
    trace_id: str,
    debug: bool
) -> JSONResponse:
    """Handle generic exceptions."""
    content = {
        "detail": "Internal server error",
        "trace_id": trace_id
    }
    
    # Add stack trace in debug mode
    if debug:
        content["stacktrace"] = traceback.format_exc()
    
    return JSONResponse(
        content=content,
        status_code=500
    )

def handle_validation_error(error: ValidationError) -> HTTPException:
    """Convert a Pydantic ValidationError to an HTTPException."""
    formatted_error = format_validation_error(error)
    return HTTPException(400, formatted_error)

class ExceptionMiddleware:
    """ASGI middleware for handling exceptions."""
    
    def __init__(self, app: ASGIApp):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
        """
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and handle exceptions.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            # Create a request object to get app settings
            request = Request(scope)
            
            # Handle the exception
            response = await global_exception_handler(request, exc)
            
            # Send the response
            await response(scope, receive, send)