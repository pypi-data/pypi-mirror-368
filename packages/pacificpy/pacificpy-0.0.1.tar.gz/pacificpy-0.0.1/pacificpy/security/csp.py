"""
Content Security Policy (CSP) helper for PacificPy.

This module provides utilities for generating CSP headers with nonce support
and Jinja2 helpers for inserting nonces into script and style tags.
"""

import secrets
from typing import Dict, List, Optional, Set
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
from starlette.datastructures import Headers

class CSPMiddleware:
    """ASGI middleware for Content Security Policy headers."""
    
    def __init__(
        self,
        app: ASGIApp,
        policies: Dict[str, List[str]] = None,
        report_only: bool = False,
        nonce_enabled: bool = True,
    ):
        """
        Initialize the CSP middleware.
        
        Args:
            app: The ASGI application
            policies: CSP policies as a dictionary
            report_only: Whether to use Content-Security-Policy-Report-Only
            nonce_enabled: Whether to generate nonces for scripts/styles
        """
        self.app = app
        self.policies = policies or self._default_policies()
        self.report_only = report_only
        self.nonce_enabled = nonce_enabled
    
    def _default_policies(self) -> Dict[str, List[str]]:
        """Get default CSP policies."""
        return {
            "default-src": ["'self'"],
            "script-src": ["'self'"],
            "style-src": ["'self'"],
            "img-src": ["'self'", "data:"],
            "font-src": ["'self'"],
            "connect-src": ["'self'"],
            "media-src": ["'self'"],
            "object-src": ["'none'"],
            "child-src": ["'self'"],
            "frame-src": ["'self'"],
            "worker-src": ["'self'"],
        }
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and add CSP headers.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Generate nonce if enabled
        if self.nonce_enabled:
            nonce = secrets.token_urlsafe(16)
        else:
            nonce = None
        
        # Store nonce in request state for use in templates
        if nonce:
            scope["state"] = getattr(scope, "state", {})
            scope["state"]["csp_nonce"] = nonce
        
        # Create a wrapper for the send function to add CSP headers
        async def send_with_csp_headers(message):
            if message["type"] == "http.response.start":
                # Add CSP headers
                message = self._add_csp_headers(message, nonce)
            await send(message)
        
        # Call the next middleware/app
        await self.app(scope, receive, send_with_csp_headers)
    
    def _add_csp_headers(self, message: dict, nonce: Optional[str] = None) -> dict:
        """
        Add CSP headers to a response message.
        
        Args:
            message: The response message
            nonce: The nonce to include in policies
            
        Returns:
            The modified response message
        """
        # Build CSP header value
        policies = self.policies.copy()
        
        # Add nonce to script-src and style-src if enabled
        if nonce:
            if "script-src" in policies:
                policies["script-src"] = policies["script-src"] + [f"'nonce-{nonce}'"]
            else:
                policies["script-src"] = [f"'nonce-{nonce}'"]
            
            if "style-src" in policies:
                policies["style-src"] = policies["style-src"] + [f"'nonce-{nonce}'"]
            else:
                policies["style-src"] = [f"'nonce-{nonce}'"]
        
        # Build CSP string
        csp_parts = []
        for directive, sources in policies.items():
            csp_parts.append(f"{directive} {' '.join(sources)}")
        
        csp_value = "; ".join(csp_parts)
        
        # Add CSP header
        headers = message.get("headers", [])
        header_dict = {k.decode(): v.decode() for k, v in headers}
        
        if self.report_only:
            header_dict["content-security-policy-report-only"] = csp_value
        else:
            header_dict["content-security-policy"] = csp_value
        
        # Convert back to list of tuples
        message["headers"] = [(k.encode(), v.encode()) for k, v in header_dict.items()]
        return message

# Helper functions
def get_csp_nonce(request: Request) -> Optional[str]:
    """
    Get the CSP nonce from a request.
    
    Args:
        request: The request
        
    Returns:
        The CSP nonce, or None if not found
    """
    return getattr(request.state, "csp_nonce", None)

def csp_nonce_jinja2_helper(request: Request) -> str:
    """
    Jinja2 helper for inserting CSP nonce into templates.
    
    Args:
        request: The request
        
    Returns:
        The nonce attribute string for script/style tags
    """
    nonce = get_csp_nonce(request)
    if nonce:
        return f' nonce="{nonce}"'
    return ""

# Default CSP middleware
def default_csp_middleware(app: ASGIApp) -> CSPMiddleware:
    """
    Create a CSP middleware with default policies.
    
    Args:
        app: The ASGI application
        
    Returns:
        A CSPMiddleware instance
    """
    return CSPMiddleware(app)