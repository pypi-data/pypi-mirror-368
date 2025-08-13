"""
Rate limiting middleware for PacificPy.

This module provides rate limiting middleware with support for
in-memory and Redis backends, limiting requests by IP or route.
"""

import time
import hashlib
from typing import Dict, Optional, Union
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import Response
from starlette.datastructures import Headers
from starlette.requests import Request

class RateLimitMiddleware:
    """ASGI middleware for rate limiting requests."""
    
    def __init__(
        self,
        app: ASGIApp,
        backend: "RateLimitBackend" = None,
        limit: int = 100,
        window: int = 60,  # 1 minute
        key_func: callable = None,
        exempt_paths: set = frozenset(),
        exempt_predicates: list = None,
    ):
        """
        Initialize the rate limiting middleware.
        
        Args:
            app: The ASGI application
            backend: The rate limit backend (default: in-memory)
            limit: Maximum requests per window
            window: Time window in seconds
            key_func: Function to generate rate limit keys
            exempt_paths: Paths that are exempt from rate limiting
            exempt_predicates: Functions that determine if a request is exempt
        """
        self.app = app
        self.backend = backend or InMemoryRateLimitBackend()
        self.limit = limit
        self.window = window
        self.key_func = key_func or self._default_key_func
        self.exempt_paths = exempt_paths
        self.exempt_predicates = exempt_predicates or []
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and apply rate limiting.
        
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
        
        # Generate rate limit key
        key = self.key_func(request)
        
        # Check rate limit
        try:
            allowed = await self.backend.is_allowed(key, self.limit, self.window)
        except Exception:
            # If backend fails, allow the request (fail open)
            allowed = True
        
        if not allowed:
            # Return 429 Too Many Requests
            response = Response("Too Many Requests", status_code=429)
            await response(scope, receive, send)
            return
        
        # Increment request count
        try:
            await self.backend.increment(key, self.window)
        except Exception:
            # If backend fails, continue anyway
            pass
        
        # Continue with the request
        await self.app(scope, receive, send)
    
    def _is_exempt(self, request: Request) -> bool:
        """
        Check if a request is exempt from rate limiting.
        
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
    
    def _default_key_func(self, request: Request) -> str:
        """
        Default function to generate rate limit keys.
        
        Args:
            request: The request
            
        Returns:
            A rate limit key
        """
        # Get client IP
        headers = Headers(scope=request.scope)
        x_forwarded_for = headers.get("x-forwarded-for")
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Create key from IP and path
        key_data = f"{client_ip}:{request.url.path}"
        return hashlib.sha256(key_data.encode()).hexdigest()

class RateLimitBackend:
    """Base class for rate limit backends."""
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        Check if a request is allowed based on rate limit.
        
        Args:
            key: The rate limit key
            limit: Maximum requests per window
            window: Time window in seconds
            
        Returns:
            True if allowed, False if rate limited
        """
        raise NotImplementedError
    
    async def increment(self, key: str, window: int) -> None:
        """
        Increment the request count for a key.
        
        Args:
            key: The rate limit key
            window: Time window in seconds
        """
        raise NotImplementedError

class InMemoryRateLimitBackend(RateLimitBackend):
    """In-memory rate limit backend."""
    
    def __init__(self):
        """Initialize the in-memory backend."""
        self.requests = {}  # key -> [(timestamp, count), ...]
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        Check if a request is allowed based on rate limit.
        
        Args:
            key: The rate limit key
            limit: Maximum requests per window
            window: Time window in seconds
            
        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()
        cutoff = now - window
        
        # Clean up old entries
        if key in self.requests:
            self.requests[key] = [
                (timestamp, count) 
                for timestamp, count in self.requests[key] 
                if timestamp > cutoff
            ]
        
        # Calculate current count
        current_count = sum(
            count 
            for timestamp, count in self.requests.get(key, []) 
            if timestamp > cutoff
        )
        
        return current_count < limit
    
    async def increment(self, key: str, window: int) -> None:
        """
        Increment the request count for a key.
        
        Args:
            key: The rate limit key
            window: Time window in seconds
        """
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Add new entry
        self.requests[key].append((now, 1))
        
        # Clean up old entries
        cutoff = now - window
        self.requests[key] = [
            (timestamp, count) 
            for timestamp, count in self.requests[key] 
            if timestamp > cutoff
        ]

# Helper functions
def exempt_from_rate_limit(path: str) -> callable:
    """
    Decorator to mark a path as exempt from rate limiting.
    
    Args:
        path: The path to exempt
        
    Returns:
        A decorator function
    """
    def decorator(func):
        if not hasattr(func, "_rate_limit_exempt_paths"):
            func._rate_limit_exempt_paths = set()
        func._rate_limit_exempt_paths.add(path)
        return func
    return decorator

# Default rate limit middleware
def default_rate_limit_middleware(app: ASGIApp) -> RateLimitMiddleware:
    """
    Create a rate limit middleware with default settings.
    
    Args:
        app: The ASGI application
        
    Returns:
        A RateLimitMiddleware instance
    """
    return RateLimitMiddleware(
        app,
        limit=100,
        window=60,
        exempt_paths={"/health", "/metrics"}
    )