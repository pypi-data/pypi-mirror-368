"""
ETag support for PacificPy.

This module provides ETag generation and validation middleware,
along with a decorator for manual ETag control.
"""

import hashlib
from typing import Any, Callable, Optional
from functools import wraps
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
from starlette.responses import Response
from starlette.datastructures import Headers

class ETagMiddleware:
    """ASGI middleware for ETag generation and validation."""
    
    def __init__(
        self,
        app: ASGIApp,
        enabled: bool = True,
        weak_etags: bool = False,
        auto_etag: bool = True,
    ):
        """
        Initialize the ETag middleware.
        
        Args:
            app: The ASGI application
            enabled: Whether ETag support is enabled
            weak_etags: Whether to generate weak ETags
            auto_etag: Whether to automatically generate ETags for responses
        """
        self.app = app
        self.enabled = enabled
        self.weak_etags = weak_etags
        self.auto_etag = auto_etag
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and handle ETag generation/validation.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http" or not self.enabled:
            await self.app(scope, receive, send)
            return
        
        request = Request(scope)
        
        # Create a wrapper for the send function to add ETags
        async def send_with_etag(message):
            if message["type"] == "http.response.start" and self.auto_etag:
                # Add ETag to response
                message = await self._add_etag(message, scope)
            await send(message)
        
        # Check If-None-Match header for conditional requests
        headers = Headers(scope=scope)
        if_none_match = headers.get("if-none-match")
        
        if if_none_match:
            # Store the If-None-Match header for later use
            scope["if_none_match"] = if_none_match
        
        # Call the next middleware/app
        await self.app(scope, receive, send_with_etag)
    
    async def _add_etag(self, message: dict, scope: Scope) -> dict:
        """
        Add ETag header to a response message.
        
        Args:
            message: The response message
            scope: The ASGI scope
            
        Returns:
            The modified response message
        """
        # Get response body from scope (this is a simplification)
        # In a real implementation, you'd need to capture the body differently
        body = scope.get("response_body", b"")
        
        # Generate ETag
        etag = self._generate_etag(body)
        
        # Check If-None-Match header
        if_none_match = scope.get("if_none_match")
        if if_none_match and self._matches_etag(if_none_match, etag):
            # Return 304 Not Modified
            return {
                "type": "http.response.start",
                "status": 304,
                "headers": [(b"etag", etag.encode())],
            }
        
        # Add ETag header
        headers = message.get("headers", [])
        headers.append((b"etag", etag.encode()))
        message["headers"] = headers
        
        return message
    
    def _generate_etag(self, body: bytes) -> str:
        """
        Generate an ETag for a response body.
        
        Args:
            body: The response body
            
        Returns:
            The ETag
        """
        # Create hash of body
        hash_digest = hashlib.md5(body).hexdigest()
        
        # Add weak prefix if needed
        if self.weak_etags:
            return f"W/\"{hash_digest}\""
        else:
            return f"\"{hash_digest}\""
    
    def _matches_etag(self, if_none_match: str, etag: str) -> bool:
        """
        Check if an ETag matches the If-None-Match header.
        
        Args:
            if_none_match: The If-None-Match header value
            etag: The ETag to check
            
        Returns:
            True if the ETag matches, False otherwise
        """
        # Handle wildcard
        if if_none_match == "*":
            return True
        
        # Parse ETags from header
        etags = [tag.strip() for tag in if_none_match.split(",")]
        
        # Check if any ETag matches
        return etag in etags

# ETag decorator
def etag(key_func: Callable[[Request], str] = None):
    """
    Decorator to add ETag support to an endpoint.
    
    Args:
        key_func: Function to generate ETag key from request
        
    Returns:
        The decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Response:
            # Generate ETag key if function provided
            etag_key = None
            if key_func:
                etag_key = key_func(request)
            
            # Check If-None-Match header
            if_none_match = request.headers.get("if-none-match")
            
            # If we have an ETag key, check if content matches
            if etag_key and if_none_match:
                # In a real implementation, you'd check if the content
                # associated with the ETag key matches the If-None-Match header
                # For this example, we'll skip that logic
                
                # Generate ETag from key
                etag_value = f"\"{hashlib.md5(etag_key.encode()).hexdigest()}\""
                
                # Check if ETag matches
                if etag_value == if_none_match:
                    # Return 304 Not Modified
                    return Response("", status_code=304, headers={"ETag": etag_value})
            
            # Execute the original function
            response = await func(request, *args, **kwargs)
            
            # Add ETag header if not already present
            if etag_key and "etag" not in response.headers:
                etag_value = f"\"{hashlib.md5(etag_key.encode()).hexdigest()}\""
                response.headers["ETag"] = etag_value
            
            return response
        
        return wrapper
    
    return decorator

# Manual ETag functions
def generate_etag(content: Any) -> str:
    """
    Generate an ETag for content.
    
    Args:
        content: The content to generate an ETag for
        
    Returns:
        The ETag
    """
    # Convert content to bytes
    if isinstance(content, str):
        content_bytes = content.encode("utf-8")
    elif isinstance(content, bytes):
        content_bytes = content
    else:
        content_bytes = str(content).encode("utf-8")
    
    # Generate hash
    hash_digest = hashlib.md5(content_bytes).hexdigest()
    return f"\"{hash_digest}\""

def check_etag(request: Request, content: Any) -> Optional[Response]:
    """
    Check if a request has a matching ETag and return 304 if so.
    
    Args:
        request: The request object
        content: The content to check ETag for
        
    Returns:
        A 304 response if ETag matches, None otherwise
    """
    # Get If-None-Match header
    if_none_match = request.headers.get("if-none-match")
    if not if_none_match:
        return None
    
    # Generate ETag for content
    etag = generate_etag(content)
    
    # Check if ETag matches
    if etag == if_none_match:
        return Response("", status_code=304, headers={"ETag": etag})
    
    return None

# ETag validation function
def validate_etag(if_none_match: str, etag: str) -> bool:
    """
    Validate an ETag against an If-None-Match header.
    
    Args:
        if_none_match: The If-None-Match header value
        etag: The ETag to validate
        
    Returns:
        True if the ETag matches, False otherwise
    """
    # Handle wildcard
    if if_none_match == "*":
        return True
    
    # Parse ETags from header
    etags = [tag.strip() for tag in if_none_match.split(",")]
    
    # Check if any ETag matches
    return etag in etags

# Example usage:
"""
# Add ETag middleware to app
app.add_middleware(ETagMiddleware)

# Use ETag decorator
@app.get("/users")
@etag(key_func=lambda request: f"users:{request.query_params.get('page', 1)}")
async def get_users(request):
    users = await fetch_users()
    return users

# Manual ETag checking
@app.get("/resource/{id}")
async def get_resource(request):
    resource = await fetch_resource(request.path_params["id"])
    
    # Check if ETag matches
    etag_response = check_etag(request, resource)
    if etag_response:
        return etag_response
    
    return resource
"""