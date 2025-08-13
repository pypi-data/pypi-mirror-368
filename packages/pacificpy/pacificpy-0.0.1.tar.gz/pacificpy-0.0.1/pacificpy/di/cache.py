"""
Dependency Injection: Per-request cache
"""
from typing import Any, Dict, Callable

class DependencyCache:
    """
    Per-request cache for dependency injection.
    Uses Request.state to store cached dependencies.
    """
    
    NOT_FOUND = object()  # Sentinel value for cache misses
    
    def __init__(self, request_state: Dict[str, Any]):
        """
        Initialize the cache with a request's state.
        
        Args:
            request_state: The state dictionary from a request object
        """
        self._state = request_state
        # Ensure we have a place to store cached dependencies
        if '_di_cache' not in self._state:
            self._state['_di_cache'] = {}
        self._cache = self._state['_di_cache']
    
    def get(self, key: Callable) -> Any:
        """
        Get a cached value by key.
        
        Args:
            key: The dependency callable/class to look up
            
        Returns:
            The cached value, or NOT_FOUND if not in cache
        """
        cache_key = self._get_cache_key(key)
        return self._cache.get(cache_key, self.NOT_FOUND)
    
    def set(self, key: Callable, value: Any) -> None:
        """
        Set a cached value.
        
        Args:
            key: The dependency callable/class to cache
            value: The value to cache
        """
        cache_key = self._get_cache_key(key)
        self._cache[cache_key] = value
    
    def clear(self) -> None:
        """Clear all cached dependencies."""
        self._cache.clear()
    
    def _get_cache_key(self, callable_obj: Callable) -> str:
        """
        Generate a cache key for a callable.
        
        Args:
            callable_obj: The callable to generate a key for
            
        Returns:
            A string key for the cache
        """
        # Use the qualified name of the callable as the cache key
        return f"{callable_obj.__module__}.{callable_obj.__qualname__}"