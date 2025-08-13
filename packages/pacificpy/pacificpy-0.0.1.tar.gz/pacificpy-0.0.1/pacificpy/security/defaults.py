"""
Default security middleware for PacificPy.

This module provides a middleware that adds common security headers
to HTTP responses, including HSTS, X-Frame-Options, and X-Content-Type-Options.
"""

from typing import Optional
from starlette.types import ASGIApp, Receive, Scope, Send

class SecurityMiddleware:
    """ASGI middleware for adding default security headers."""
    
    def __init__(
        self,
        app: ASGIApp,
        hsts_max_age: int = 31536000,  # 1 year
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = False,
        frame_options: str = "DENY",
        content_type_options: str = "nosniff",
        referrer_policy: str = "strict-origin-when-cross-origin"
    ):
        """
        Initialize the security middleware.
        
        Args:
            app: The ASGI application
            hsts_max_age: Max age for HSTS header in seconds
            hsts_include_subdomains: Whether to include subdomains in HSTS
            hsts_preload: Whether to include preload directive in HSTS
            frame_options: Value for X-Frame-Options header
            content_type_options: Value for X-Content-Type-Options header
            referrer_policy: Value for Referrer-Policy header
        """
        self.app = app
        self.hsts_max_age = hsts_max_age
        self.hsts_include_subdomains = hsts_include_subdomains
        self.hsts_preload = hsts_preload
        self.frame_options = frame_options
        self.content_type_options = content_type_options
        self.referrer_policy = referrer_policy
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and add security headers.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Create a wrapper for the send function to add headers
        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                # Add security headers
                headers = message.get("headers", [])
                headers = self._add_security_headers(headers)
                message["headers"] = headers
            
            await send(message)
        
        # Call the next middleware/app
        await self.app(scope, receive, send_with_security_headers)
    
    def _add_security_headers(self, headers: list) -> list:
        """
        Add security headers to the response.
        
        Args:
            headers: List of headers
            
        Returns:
            List of headers with security headers added
        """
        # Convert headers to dict for easier manipulation
        header_dict = {}
        for name, value in headers:
            header_dict[name.decode()] = value.decode()
        
        # Add HSTS header (only for HTTPS)
        if self.hsts_max_age > 0:
            hsts_parts = [f"max-age={self.hsts_max_age}"]
            if self.hsts_include_subdomains:
                hsts_parts.append("includeSubDomains")
            if self.hsts_preload:
                hsts_parts.append("preload")
            header_dict["strict-transport-security"] = "; ".join(hsts_parts)
        
        # Add X-Frame-Options header
        if self.frame_options:
            header_dict["x-frame-options"] = self.frame_options
        
        # Add X-Content-Type-Options header
        if self.content_type_options:
            header_dict["x-content-type-options"] = self.content_type_options
        
        # Add Referrer-Policy header
        if self.referrer_policy:
            header_dict["referrer-policy"] = self.referrer_policy
        
        # Convert back to list of tuples
        return [(k.encode(), v.encode()) for k, v in header_dict.items()]

# Default security middleware with recommended settings
def default_security_middleware(app: ASGIApp) -> SecurityMiddleware:
    """
    Create a security middleware with default recommended settings.
    
    Args:
        app: The ASGI application
        
    Returns:
        A SecurityMiddleware instance
    """
    return SecurityMiddleware(
        app,
        hsts_max_age=31536000,  # 1 year
        hsts_include_subdomains=True,
        hsts_preload=False,
        frame_options="DENY",
        content_type_options="nosniff",
        referrer_policy="strict-origin-when-cross-origin"
    )