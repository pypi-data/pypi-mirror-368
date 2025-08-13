"""
Memory cache backend for PacificPy.

This module provides an LRU cache with TTL, thread-safety, and statistics.
"""

import time
import threading
from typing import Any, Optional, Dict
from collections import OrderedDict

from ..decorators import CacheBackend

class LRUCacheBackend(CacheBackend):
    """LRU cache backend with TTL and thread-safety."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize the LRU cache backend.
        
        Args:
            max_size: Maximum number of items in the cache
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # Cache storage
        self._cache: OrderedDict[str, tuple[Any, float, float]] = OrderedDict()
        
        # Statistics
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
        }
        
        # Lock for thread-safety
        self._lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value, or None if not found or expired
        """
        with self._lock:
            # Check if key exists
            if key not in self._cache:
                self._stats["misses"] += 1
                return None
            
            # Get value, expiration time, and access time
            value, expires_at, access_time = self._cache[key]
            
            # Check if expired
            if time.time() > expires_at:
                # Expired, remove from cache
                del self._cache[key]
                self._stats["misses"] += 1
                return None
            
            # Update access time and move to end (LRU)
            self._cache.move_to_end(key, last=True)
            self._stats["hits"] += 1
            
            return value
    
    async def set(self, key: str, value: str, ttl: int = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds (overrides default)
        """
        with self._lock:
            # Set expiration time
            expires_at = time.time() + (ttl or self.default_ttl)
            
            # Add to cache
            self._cache[key] = (value, expires_at, time.time())
            self._stats["sets"] += 1
            
            # Check if cache is full
            if len(self._cache) > self.max_size:
                # Remove oldest item (LRU)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats["evictions"] += 1
            
            # Move to end (most recently used)
            self._cache.move_to_end(key, last=True)
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key was deleted, False otherwise
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1
                return True
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            A dictionary with cache statistics
        """
        with self._lock:
            return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset cache statistics."""
        with self._lock:
            self._stats = {
                "hits": 0,
                "misses": 0,
                "sets": 0,
                "deletes": 0,
                "evictions": 0,
            }
    
    def clear(self) -> None:
        """Clear the entire cache."""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """
        Get the current size of the cache.
        
        Returns:
            The number of items in the cache
        """
        with self._lock:
            return len(self._cache)
    
    def capacity(self) -> int:
        """
        Get the maximum capacity of the cache.
        
        Returns:
            The maximum number of items the cache can hold
        """
        return self.max_size
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get the remaining TTL for a key.
        
        Args:
            key: The cache key
            
        Returns:
            The remaining TTL in seconds, or None if key not found
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expires_at, access_time = self._cache[key]
            
            # Check if expired
            if time.time() > expires_at:
                # Expired, remove from cache
                del self._cache[key]
                return None
            
            return int(expires_at - time.time())
    
    async def cleanup(self) -> int:
        """
        Clean up expired items from the cache.
        
        Returns:
            The number of expired items removed
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expires_at, _) in self._cache.items()
                if current_time > expires_at
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)

# Thread-safe singleton instance
_memory_cache: Optional[LRUCacheBackend] = None
_memory_cache_lock = threading.Lock()

def get_memory_cache(max_size: int = 1000, default_ttl: int = 300) -> LRUCacheBackend:
    """
    Get a thread-safe singleton instance of the memory cache.
    
    Args:
        max_size: Maximum number of items in the cache
        default_ttl: Default time-to-live in seconds
        
    Returns:
        The memory cache instance
    """
    global _memory_cache
    
    with _memory_cache_lock:
        if _memory_cache is None:
            _memory_cache = LRUCacheBackend(max_size=max_size, default_ttl=default_ttl)
        return _memory_cache

# Example usage:
"""
# In your app setup:
from pacificpy.cache.decorators import configure_cache
from pacificpy.cache.backends.memory import get_memory_cache

# Configure cache with memory backend
memory_cache = get_memory_cache(max_size=1000, default_ttl=600)
configure_cache(backend=memory_cache)

# In your routes:
@app.get("/expensive-operation")
@cache(ttl=300)
async def expensive_operation(request):
    # Some expensive operation
    result = await perform_expensive_operation()
    return result

# Check cache statistics:
@app.get("/cache-stats")
async def cache_stats(request):
    stats = memory_cache.get_stats()
    return stats
"""