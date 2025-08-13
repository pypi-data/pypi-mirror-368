"""
Redis cache backend for PacificPy.

This module provides a Redis cache backend for storing JSON responses
with optional compression.
"""

import json
import time
from typing import Any, Optional
import zlib

from ..decorators import CacheBackend

# Try to import aioredis for async support
try:
    import aioredis
    AIREDIS_AVAILABLE = True
except ImportError:
    AIREDIS_AVAILABLE = False

# Try to import redis for sync support
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class RedisCacheBackend(CacheBackend):
    """Redis cache backend for storing JSON responses."""
    
    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        prefix: str = "cache:",
        default_ttl: int = 300,
        compress: bool = False,
        compression_level: int = 6,
    ):
        """
        Initialize the Redis cache backend.
        
        Args:
            url: The Redis connection URL
            prefix: Prefix for cache keys
            default_ttl: Default time-to-live in seconds
            compress: Whether to compress cached values
            compression_level: Compression level (1-9)
        """
        self.url = url
        self.prefix = prefix
        self.default_ttl = default_ttl
        self.compress = compress
        self.compression_level = compression_level
        
        # Redis client
        self.client: Optional[aioredis.Redis] = None
        self.sync_client: Optional[redis.Redis] = None
        
        # Initialize client based on available libraries
        if AIREDIS_AVAILABLE:
            self.client = aioredis.from_url(url)
        elif REDIS_AVAILABLE:
            self.sync_client = redis.from_url(url)
        else:
            raise RuntimeError("Either aioredis or redis package is required")
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value, or None if not found
        """
        full_key = f"{self.prefix}{key}"
        
        try:
            if self.client:
                # Async client
                value = await self.client.get(full_key)
            elif self.sync_client:
                # Sync client
                value = self.sync_client.get(full_key)
            else:
                return None
            
            if value is None:
                return None
            
            # Decompress if needed
            if self.compress:
                value = zlib.decompress(value)
            
            # Decode bytes to string
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            
            return value
        except Exception:
            # If any error occurs, treat as cache miss
            return None
    
    async def set(self, key: str, value: str, ttl: int = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds (overrides default)
        """
        full_key = f"{self.prefix}{key}"
        expires_at = ttl or self.default_ttl
        
        try:
            # Encode string to bytes
            if isinstance(value, str):
                value_bytes = value.encode("utf-8")
            else:
                value_bytes = str(value).encode("utf-8")
            
            # Compress if needed
            if self.compress:
                value_bytes = zlib.compress(value_bytes, self.compression_level)
            
            if self.client:
                # Async client
                await self.client.setex(full_key, expires_at, value_bytes)
            elif self.sync_client:
                # Sync client
                self.sync_client.setex(full_key, expires_at, value_bytes)
        except Exception:
            # If we can't set the value, continue without caching
            pass
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key was deleted, False otherwise
        """
        full_key = f"{self.prefix}{key}"
        
        try:
            if self.client:
                # Async client
                result = await self.client.delete(full_key)
            elif self.sync_client:
                # Sync client
                result = self.sync_client.delete(full_key)
            else:
                return False
            
            return result > 0
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key exists, False otherwise
        """
        full_key = f"{self.prefix}{key}"
        
        try:
            if self.client:
                # Async client
                return await self.client.exists(full_key) > 0
            elif self.sync_client:
                # Sync client
                return self.sync_client.exists(full_key) > 0
            else:
                return False
        except Exception:
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for a key.
        
        Args:
            key: The cache key
            ttl: Time to live in seconds
            
        Returns:
            True if expiration was set, False otherwise
        """
        full_key = f"{self.prefix}{key}"
        
        try:
            if self.client:
                # Async client
                return await self.client.expire(full_key, ttl)
            elif self.sync_client:
                # Sync client
                return self.sync_client.expire(full_key, ttl)
            else:
                return False
        except Exception:
            return False
    
    async def ttl(self, key: str) -> int:
        """
        Get time to live for a key.
        
        Args:
            key: The cache key
            
        Returns:
            Time to live in seconds, or -1 if key doesn't exist
        """
        full_key = f"{self.prefix}{key}"
        
        try:
            if self.client:
                # Async client
                return await self.client.ttl(full_key)
            elif self.sync_client:
                # Sync client
                return self.sync_client.ttl(full_key)
            else:
                return -1
        except Exception:
            return -1
    
    async def flush(self) -> None:
        """Flush all cache entries."""
        try:
            pattern = f"{self.prefix}*"
            
            if self.client:
                # Async client
                keys = await self.client.keys(pattern)
                if keys:
                    await self.client.delete(*keys)
            elif self.sync_client:
                # Sync client
                keys = self.sync_client.keys(pattern)
                if keys:
                    self.sync_client.delete(*keys)
        except Exception:
            # If we can't flush, continue
            pass

# Global Redis cache instance
_redis_cache: Optional[RedisCacheBackend] = None

def configure_redis_cache(
    url: str = "redis://localhost:6379/0",
    prefix: str = "cache:",
    default_ttl: int = 300,
    compress: bool = False,
) -> RedisCacheBackend:
    """
    Configure the global Redis cache.
    
    Args:
        url: The Redis connection URL
        prefix: Prefix for cache keys
        default_ttl: Default time-to-live in seconds
        compress: Whether to compress cached values
        
    Returns:
        The Redis cache instance
    """
    global _redis_cache
    _redis_cache = RedisCacheBackend(
        url=url,
        prefix=prefix,
        default_ttl=default_ttl,
        compress=compress,
    )
    return _redis_cache

def get_redis_cache() -> RedisCacheBackend:
    """
    Get the global Redis cache instance.
    
    Returns:
        The Redis cache instance
        
    Raises:
        RuntimeError: If Redis cache is not configured
    """
    if not _redis_cache:
        raise RuntimeError("Redis cache not configured")
    
    return _redis_cache

# Example usage:
"""
# In your app setup:
from pacificpy.cache.decorators import configure_cache
from pacificpy.cache.backends.redis import configure_redis_cache

# Configure Redis cache
redis_cache = configure_redis_cache(
    url="redis://localhost:6379/0",
    prefix="myapp:",
    default_ttl=600,
    compress=True
)

# Configure cache with Redis backend
configure_cache(backend=redis_cache)

# In your routes:
@app.get("/expensive-operation")
@cache(ttl=300)
async def expensive_operation(request):
    # Some expensive operation
    result = await perform_expensive_operation()
    return result

# Manual cache operations:
@app.post("/cache/{key}")
async def set_cache(key: str, value: dict):
    await redis_cache.set(key, json.dumps(value), ttl=3600)
    return {"status": "ok"}

@app.get("/cache/{key}")
async def get_cache(key: str):
    value = await redis_cache.get(key)
    if value:
        return json.loads(value)
    return {"error": "not found"}
"""