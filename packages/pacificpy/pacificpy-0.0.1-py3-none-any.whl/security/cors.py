"""
CORS middleware for PacificPy.

This module provides a CORS middleware with secure defaults and
support for preflight requests.
"""

import re
from typing import List, Optional, Set, Union
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import Response
from starlette.datastructures import Headers

class CORSMiddleware:
    """ASGI middleware for handling CORS headers."""
    
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: Union[List[str], Set[str]] = None,
        allow_methods: Union[List[str], Set[str]] = None,
        allow_headers: Union[List[str], Set[str]] = None,
        allow_credentials: bool = False,
        allow_origin_regex: Optional[str] = None,
        expose_headers: Optional[List[str]] = None,
        max_age: int = 600,
    ):
        """
        Initialize the CORS middleware.
        
        Args:
            app: The ASGI application
            allow_origins: List of allowed origins (default: empty list for security)
            allow_methods: List of allowed methods
            allow_headers: List of allowed headers
            allow_credentials: Whether to allow credentials
            allow_origin_regex: Regex pattern for allowed origins
            expose_headers: List of headers to expose
            max_age: Max age for preflight responses
        """
        self.app = app
        self.allow_origins = set(allow_origins or [])
        self.allow_methods = set(allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
        self.allow_headers = set(allow_headers or [])
        self.allow_credentials = allow_credentials
        self.allow_origin_regex = allow_origin_regex
        self.expose_headers = expose_headers or []
        self.max_age = max_age
        
        # Compile regex if provided
        if allow_origin_regex:
            self.origin_regex = re.compile(allow_origin_regex)
        else:
            self.origin_regex = None
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and handle CORS.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        headers = Headers(scope=scope)
        origin = headers.get("origin")
        
        # Handle preflight requests
        if scope["method"] == "OPTIONS" and "access-control-request-method" in headers:
            response = self._preflight_response(origin, headers)
            await response(scope, receive, send)
            return
        
        # For non-preflight requests, add CORS headers to response
        async def send_with_cors_headers(message):
            if message["type"] == "http.response.start":
                # Add CORS headers
                message = self._add_cors_headers(message, origin)
            
            await send(message)
        
        # Call the next middleware/app
        await self.app(scope, receive, send_with_cors_headers)
    
    def _preflight_response(self, origin: str, headers: Headers) -> Response:
        """
        Create a preflight response.
        
        Args:
            origin: The origin header
            headers: The request headers
            
        Returns:
            A Response instance
        """
        # Check if origin is allowed
        if not self._is_origin_allowed(origin):
            return Response("Forbidden", status_code=403)
        
        # Get requested method and headers
        requested_method = headers.get("access-control-request-method")
        requested_headers = headers.get("access-control-request-headers")
        
        # Check if method is allowed
        if requested_method and requested_method not in self.allow_methods:
            return Response("Forbidden", status_code=403)
        
        # Prepare response headers
        response_headers = {
            "access-control-allow-origin": origin,
            "access-control-allow-methods": ", ".join(self.allow_methods),
            "access-control-max-age": str(self.max_age),
        }
        
        # Add allowed headers
        if self.allow_headers:
            response_headers["access-control-allow-headers"] = ", ".join(self.allow_headers)
        elif requested_headers:
            response_headers["access-control-allow-headers"] = requested_headers
        
        # Add credentials header if allowed
        if self.allow_credentials:
            response_headers["access-control-allow-credentials"] = "true"
        
        return Response("", status_code=200, headers=response_headers)
    
    def _add_cors_headers(self, message: dict, origin: str) -> dict:
        """
        Add CORS headers to a response message.
        
        Args:
            message: The response message
            origin: The origin header
            
        Returns:
            The modified response message
        """
        if not origin or not self._is_origin_allowed(origin):
            return message
        
        # Add CORS headers
        headers = message.get("headers", [])
        header_dict = {k.decode(): v.decode() for k, v in headers}
        
        # Set allowed origin
        header_dict["access-control-allow-origin"] = origin
        
        # Set credentials header if allowed
        if self.allow_credentials:
            header_dict["access-control-allow-credentials"] = "true"
        
        # Set exposed headers
        if self.expose_headers:
            header_dict["access-control-expose-headers"] = ", ".join(self.expose_headers)
        
        # Convert back to list of tuples
        message["headers"] = [(k.encode(), v.encode()) for k, v in header_dict.items()]
        return message
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """
        Check if an origin is allowed.
        
        Args:
            origin: The origin to check
            
        Returns:
            True if the origin is allowed, False otherwise
        """
        if not origin:
            return False
        
        # Check exact matches
        if origin in self.allow_origins:
            return True
        
        # Check regex match
        if self.origin_regex and self.origin_regex.match(origin):
            return True
        
        # Special case for secure defaults
        # If no origins are configured, deny all
        if not self.allow_origins and not self.origin_regex:
            return False
        
        return False

# Default CORS middleware with secure settings
def default_cors_middleware(app: ASGIApp) -> CORSMiddleware:
    """
    Create a CORS middleware with secure default settings.
    
    Args:
        app: The ASGI application
        
    Returns:
        A CORSMiddleware instance
    """
    return CORSMiddleware(
        app,
        allow_origins=[],  # Secure default: no origins allowed
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=[],
        allow_credentials=False,
        max_age=600
    )