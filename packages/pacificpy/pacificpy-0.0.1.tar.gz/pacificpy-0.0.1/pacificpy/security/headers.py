"""
Header sanitizer for PacificPy.

This module provides utilities for sanitizing HTTP headers
to remove sensitive information that could be leaked by the server.
"""

from typing import List, Set
from starlette.types import ASGIApp, Receive, Scope, Send

# Default headers to remove
DEFAULT_SENSITIVE_HEADERS = {
    "server",
    "x-powered-by",
    "x-aspnet-version",
    "x-aspnetmvc-version",
}

class HeaderSanitizerMiddleware:
    """ASGI middleware for sanitizing HTTP headers."""
    
    def __init__(
        self,
        app: ASGIApp,
        sensitive_headers: Set[str] = None,
        remove_via: bool = False,
    ):
        """
        Initialize the header sanitizer middleware.
        
        Args:
            app: The ASGI application
            sensitive_headers: Set of headers to remove
            remove_via: Whether to remove the Via header
        """
        self.app = app
        self.sensitive_headers = sensitive_headers or DEFAULT_SENSITIVE_HEADERS.copy()
        if remove_via:
            self.sensitive_headers.add("via")
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and sanitize headers.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Create a wrapper for the send function to sanitize headers
        async def send_with_sanitized_headers(message):
            if message["type"] == "http.response.start":
                # Sanitize headers
                message = self._sanitize_headers(message)
            await send(message)
        
        # Call the next middleware/app
        await self.app(scope, receive, send_with_sanitized_headers)
    
    def _sanitize_headers(self, message: dict) -> dict:
        """
        Remove sensitive headers from a response message.
        
        Args:
            message: The response message
            
        Returns:
            The sanitized response message
        """
        headers = message.get("headers", [])
        
        # Filter out sensitive headers
        sanitized_headers = [
            (name, value)
            for name, value in headers
            if name.decode().lower() not in self.sensitive_headers
        ]
        
        message["headers"] = sanitized_headers
        return message

# Default header sanitizer middleware
def default_header_sanitizer_middleware(app: ASGIApp) -> HeaderSanitizerMiddleware:
    """
    Create a header sanitizer middleware with default settings.
    
    Args:
        app: The ASGI application
        
    Returns:
        A HeaderSanitizerMiddleware instance
    """
    return HeaderSanitizerMiddleware(app)