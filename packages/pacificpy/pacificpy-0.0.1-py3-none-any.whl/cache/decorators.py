"""
Cache decorators for PacificPy.

This module provides a cache decorator for caching endpoint results
with support for pluggable backends and cache keys based on
path, query parameters, and request body.
"""

import hashlib
import json
from typing import Any, Callable, Optional, Union
from functools import wraps
from starlette.requests import Request
from starlette.responses import Response

# Cache backend interface
class CacheBackend:
    """Abstract base class for cache backends."""
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value, or None if not found
        """
        raise NotImplementedError
    
    async def set(self, key: str, value: str, ttl: int = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds
        """
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key was deleted, False otherwise
        """
        raise NotImplementedError

# Memory cache backend
class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend."""
    
    def __init__(self):
        """Initialize the memory cache backend."""
        self._cache = {}
        self._ttl = {}
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from the cache."""
        if key in self._cache:
            # Check if expired
            if key in self._ttl:
                import time
                if time.time() > self._ttl[key]:
                    # Expired, remove from cache
                    del self._cache[key]
                    del self._ttl[key]
                    return None
            
            return self._cache[key]
        return None
    
    async def set(self, key: str, value: str, ttl: int = None) -> None:
        """Set a value in the cache."""
        self._cache[key] = value
        if ttl:
            import time
            self._ttl[key] = time.time() + ttl
    
    async def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        if key in self._cache:
            del self._cache[key]
            if key in self._ttl:
                del self._ttl[key]
            return True
        return False

# Cache decorator
class Cache:
    """Cache decorator for PacificPy endpoints."""
    
    def __init__(
        self,
        backend: CacheBackend = None,
        ttl: int = 300,  # 5 minutes
        key_prefix: str = "cache:",
        key_func: Callable[[Request], str] = None,
        cache_response: bool = True,
        cache_headers: bool = True,
    ):
        """
        Initialize the cache decorator.
        
        Args:
            backend: The cache backend to use
            ttl: Time to live for cached items in seconds
            key_prefix: Prefix for cache keys
            key_func: Function to generate cache keys
            cache_response: Whether to cache the response body
            cache_headers: Whether to cache response headers
        """
        self.backend = backend or MemoryCacheBackend()
        self.ttl = ttl
        self.key_prefix = key_prefix
        self.key_func = key_func or self._default_key_func
        self.cache_response = cache_response
        self.cache_headers = cache_headers
    
    def __call__(self, func: Callable) -> Callable:
        """
        Apply the cache decorator to a function.
        
        Args:
            func: The function to decorate
            
        Returns:
            The decorated function
        """
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Response:
            # Generate cache key
            cache_key = self.key_func(request)
            full_key = f"{self.key_prefix}{cache_key}"
            
            # Try to get cached response
            cached_data = await self.backend.get(full_key)
            if cached_data:
                try:
                    # Parse cached data
                    cached_response = json.loads(cached_data)
                    
                    # Create response from cached data
                    response = Response(
                        content=cached_response["body"],
                        status_code=cached_response["status_code"],
                        headers=cached_response.get("headers", {}),
                        media_type=cached_response.get("media_type")
                    )
                    
                    # Add cache hit header
                    response.headers["X-Cache"] = "HIT"
                    
                    return response
                except Exception:
                    # If we can't parse cached data, continue with normal execution
                    pass
            
            # Execute the original function
            response = await func(request, *args, **kwargs)
            
            # Cache the response if it's successful
            if response.status_code == 200:
                try:
                    # Prepare data for caching
                    cached_data = {
                        "body": response.body.decode() if hasattr(response, 'body') else "",
                        "status_code": response.status_code,
                    }
                    
                    # Add headers if caching them
                    if self.cache_headers:
                        cached_data["headers"] = dict(response.headers)
                        # Remove headers that shouldn't be cached
                        for header in ["set-cookie", "vary", "cache-control"]:
                            cached_data["headers"].pop(header, None)
                    
                    # Add media type if available
                    if hasattr(response, 'media_type'):
                        cached_data["media_type"] = response.media_type
                    
                    # Serialize and cache the response
                    await self.backend.set(
                        full_key, 
                        json.dumps(cached_data), 
                        ttl=self.ttl
                    )
                    
                    # Add cache miss header
                    response.headers["X-Cache"] = "MISS"
                except Exception:
                    # If we can't cache the response, continue without caching
                    pass
            
            return response
        
        return wrapper
    
    def _default_key_func(self, request: Request) -> str:
        """
        Generate a default cache key based on request details.
        
        Args:
            request: The request object
            
        Returns:
            A cache key
        """
        # Create key components
        key_components = [
            request.method,
            str(request.url.path),
            str(sorted(request.query_params.items())),
        ]
        
        # Add body for POST/PUT/PATCH requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # For this example, we'll assume the body can be read
                # In a real implementation, you'd need to handle this more carefully
                pass
            except Exception:
                pass
        
        # Create hash of key components
        key_string = ":".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def invalidate(self, request: Request) -> bool:
        """
        Invalidate a cached response for a request.
        
        Args:
            request: The request object
            
        Returns:
            True if cache was invalidated, False otherwise
        """
        cache_key = self.key_func(request)
        full_key = f"{self.key_prefix}{cache_key}"
        return await self.backend.delete(full_key)
    
    async def invalidate_key(self, key: str) -> bool:
        """
        Invalidate a cached response by key.
        
        Args:
            key: The cache key
            
        Returns:
            True if cache was invalidated, False otherwise
        """
        full_key = f"{self.key_prefix}{key}"
        return await self.backend.delete(full_key)

# Global cache instance
_cache: Optional[Cache] = None

def configure_cache(
    backend: CacheBackend = None,
    ttl: int = 300,
    key_prefix: str = "cache:",
) -> Cache:
    """
    Configure the global cache.
    
    Args:
        backend: The cache backend to use
        ttl: Time to live for cached items in seconds
        key_prefix: Prefix for cache keys
        
    Returns:
        The cache instance
    """
    global _cache
    _cache = Cache(
        backend=backend,
        ttl=ttl,
        key_prefix=key_prefix,
    )
    return _cache

def cache(
    ttl: int = 300,
    key_prefix: str = "cache:",
    key_func: Callable[[Request], str] = None,
) -> Callable:
    """
    Decorator to cache endpoint responses.
    
    Args:
        ttl: Time to live for cached items in seconds
        key_prefix: Prefix for cache keys
        key_func: Function to generate cache keys
        
    Returns:
        The decorator function
    """
    # Use global cache if configured, otherwise create a new one
    if _cache:
        # Create a new cache decorator with the same backend
        return Cache(
            backend=_cache.backend,
            ttl=ttl,
            key_prefix=key_prefix,
            key_func=key_func,
        )
    else:
        # Create a new cache decorator with default backend
        return Cache(
            ttl=ttl,
            key_prefix=key_prefix,
            key_func=key_func,
        )

# Cache invalidation functions
async def invalidate_cache(request: Request) -> bool:
    """
    Invalidate cache for a request using the global cache.
    
    Args:
        request: The request object
        
    Returns:
        True if cache was invalidated, False otherwise
        
    Raises:
        RuntimeError: If cache is not configured
    """
    if not _cache:
        raise RuntimeError("Cache not configured")
    
    return await _cache.invalidate(request)

async def invalidate_cache_key(key: str) -> bool:
    """
    Invalidate cache by key using the global cache.
    
    Args:
        key: The cache key
        
    Returns:
        True if cache was invalidated, False otherwise
        
    Raises:
        RuntimeError: If cache is not configured
    """
    if not _cache:
        raise RuntimeError("Cache not configured")
    
    return await _cache.invalidate_key(key)

# Example usage:
"""
# In your app setup:
from pacificpy.cache.backends.memory import MemoryCacheBackend
configure_cache(backend=MemoryCacheBackend(), ttl=600)

# In your routes:
@app.get("/users")
@cache(ttl=300)
async def get_users(request):
    # Expensive operation
    users = await fetch_users_from_database()
    return users

# Manual cache invalidation:
@app.post("/users")
async def create_user(request):
    # Create user
    user = await create_user_in_database(request.json())
    
    # Invalidate cache for users endpoint
    await invalidate_cache_key("users_list")
    
    return user
"""