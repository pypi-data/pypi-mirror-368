"""
CSRF protection middleware for PacificPy.

This module provides CSRF protection middleware that generates tokens
for safe methods and validates them for unsafe methods.
"""

import hashlib
import os
import secrets
from typing import Callable, Optional
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import Response
from starlette.datastructures import Headers
from starlette.requests import Request

class CSRFMiddleware:
    """ASGI middleware for CSRF protection."""
    
    def __init__(
        self,
        app: ASGIApp,
        secret_key: str,
        cookie_name: str = "csrftoken",
        header_name: str = "x-csrftoken",
        safe_methods: set = frozenset(["GET", "HEAD", "OPTIONS", "TRACE"]),
        exempt_paths: set = frozenset(),
        exempt_predicates: list = None,
        token_generator: Callable = None,
        token_store: "CSRFTokenStore" = None,
    ):
        """
        Initialize the CSRF middleware.
        
        Args:
            app: The ASGI application
            secret_key: Secret key for token generation
            cookie_name: Name of the CSRF cookie
            header_name: Name of the CSRF header
            safe_methods: HTTP methods that don't require CSRF protection
            exempt_paths: Paths that are exempt from CSRF protection
            exempt_predicates: Functions that determine if a request is exempt
            token_generator: Function to generate tokens
            token_store: Token store for stateful tokens
        """
        self.app = app
        self.secret_key = secret_key
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.safe_methods = safe_methods
        self.exempt_paths = exempt_paths
        self.exempt_predicates = exempt_predicates or []
        self.token_generator = token_generator or self._default_token_generator
        self.token_store = token_store or InMemoryCSRFTokenStore()
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and handle CSRF protection.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope)
        
        # Check if request is exempt
        if self._is_exempt(request):
            await self.app(scope, receive, send)
            return
        
        # Handle safe methods - set CSRF token cookie
        if request.method in self.safe_methods:
            async def send_with_csrf_cookie(message):
                if message["type"] == "http.response.start":
                    # Add CSRF token cookie
                    message = self._add_csrf_cookie(message, request)
                await send(message)
            
            await self.app(scope, receive, send_with_csrf_cookie)
            return
        
        # Handle unsafe methods - validate CSRF token
        try:
            self._validate_csrf_token(request)
        except CSRFValidationFailure as e:
            # Return 403 Forbidden for CSRF validation failures
            response = Response("CSRF validation failed", status_code=403)
            await response(scope, receive, send)
            return
        
        # Continue with the request
        await self.app(scope, receive, send)
    
    def _is_exempt(self, request: Request) -> bool:
        """
        Check if a request is exempt from CSRF protection.
        
        Args:
            request: The request to check
            
        Returns:
            True if the request is exempt, False otherwise
        """
        # Check exempt paths
        if request.url.path in self.exempt_paths:
            return True
        
        # Check exempt predicates
        for predicate in self.exempt_predicates:
            if predicate(request):
                return True
        
        return False
    
    def _add_csrf_cookie(self, message: dict, request: Request) -> dict:
        """
        Add CSRF token cookie to a response message.
        
        Args:
            message: The response message
            request: The request
            
        Returns:
            The modified response message
        """
        # Get or generate CSRF token
        token = self._get_or_generate_token(request)
        
        # Add cookie to headers
        headers = message.get("headers", [])
        header_dict = {k.decode(): v.decode() for k, v in headers}
        
        # Set cookie
        cookie_value = f"{self.cookie_name}={token}; Path=/; SameSite=Lax"
        if "set-cookie" in header_dict:
            header_dict["set-cookie"] = f"{header_dict['set-cookie']}, {cookie_value}"
        else:
            header_dict["set-cookie"] = cookie_value
        
        # Convert back to list of tuples
        message["headers"] = [(k.encode(), v.encode()) for k, v in header_dict.items()]
        return message
    
    def _get_or_generate_token(self, request: Request) -> str:
        """
        Get existing CSRF token or generate a new one.
        
        Args:
            request: The request
            
        Returns:
            A CSRF token
        """
        # Try to get existing token from cookies
        token = request.cookies.get(self.cookie_name)
        
        # If no token exists, generate a new one
        if not token:
            token = self.token_generator()
            # Store the token
            self.token_store.store_token(token, request)
        
        return token
    
    def _validate_csrf_token(self, request: Request) -> None:
        """
        Validate the CSRF token in a request.
        
        Args:
            request: The request to validate
            
        Raises:
            CSRFValidationFailure: If validation fails
        """
        # Get token from cookie
        cookie_token = request.cookies.get(self.cookie_name)
        if not cookie_token:
            raise CSRFValidationFailure("CSRF cookie missing")
        
        # Get token from header
        headers = Headers(scope=request.scope)
        header_token = headers.get(self.header_name.lower())
        if not header_token:
            # For form data, check in form fields
            if "content-type" in headers and "application/x-www-form-urlencoded" in headers["content-type"]:
                # For this implementation, we'll assume form data is handled elsewhere
                # In a full implementation, we'd parse the form data
                pass
            else:
                raise CSRFValidationFailure("CSRF header missing")
        
        # Validate tokens match
        if cookie_token != header_token:
            raise CSRFValidationFailure("CSRF tokens do not match")
        
        # Validate token exists in store
        if not self.token_store.validate_token(cookie_token, request):
            raise CSRFValidationFailure("CSRF token invalid or expired")
    
    def _default_token_generator(self) -> str:
        """
        Default token generator.
        
        Returns:
            A randomly generated token
        """
        return secrets.token_urlsafe(32)

class CSRFTokenStore:
    """Base class for CSRF token stores."""
    
    def store_token(self, token: str, request: Request) -> None:
        """
        Store a CSRF token.
        
        Args:
            token: The token to store
            request: The request
        """
        raise NotImplementedError
    
    def validate_token(self, token: str, request: Request) -> bool:
        """
        Validate a CSRF token.
        
        Args:
            token: The token to validate
            request: The request
            
        Returns:
            True if the token is valid, False otherwise
        """
        raise NotImplementedError

class InMemoryCSRFTokenStore(CSRFTokenStore):
    """In-memory CSRF token store (for development)."""
    
    def __init__(self):
        """Initialize the in-memory token store."""
        self.tokens = set()
    
    def store_token(self, token: str, request: Request) -> None:
        """
        Store a CSRF token in memory.
        
        Args:
            token: The token to store
            request: The request
        """
        self.tokens.add(token)
    
    def validate_token(self, token: str, request: Request) -> bool:
        """
        Validate a CSRF token from memory.
        
        Args:
            token: The token to validate
            request: The request
            
        Returns:
            True if the token is valid, False otherwise
        """
        return token in self.tokens

class CSRFValidationFailure(Exception):
    """Exception raised when CSRF validation fails."""
    
    pass

# Helper functions
def get_csrf_token(request: Request) -> Optional[str]:
    """
    Get the CSRF token from a request.
    
    Args:
        request: The request
        
    Returns:
        The CSRF token, or None if not found
    """
    return request.cookies.get("csrftoken")

def csrf_exempt(path: str) -> Callable:
    """
    Decorator to mark a path as exempt from CSRF protection.
    
    Args:
        path: The path to exempt
        
    Returns:
        A decorator function
    """
    def decorator(func):
        if not hasattr(func, "_csrf_exempt_paths"):
            func._csrf_exempt_paths = set()
        func._csrf_exempt_paths.add(path)
        return func
    return decorator