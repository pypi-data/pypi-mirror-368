"""
Session backend interface for PacificPy.

This module defines the abstract base class for session backends,
providing a common interface for different session storage implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from starlette.requests import Request
from starlette.responses import Response

class SessionBackend(ABC):
    """Abstract base class for session backends."""
    
    @abstractmethod
    async def load(self, request: Request) -> Dict[str, Any]:
        """
        Load session data from the backend.
        
        Args:
            request: The incoming request
            
        Returns:
            A dictionary containing the session data
        """
        pass
    
    @abstractmethod
    async def save(self, response: Response, session: Dict[str, Any]) -> None:
        """
        Save session data to the backend.
        
        Args:
            response: The response to attach session data to
            session: The session data to save
        """
        pass
    
    @abstractmethod
    async def clear(self, response: Response) -> None:
        """
        Clear session data from the backend.
        
        Args:
            response: The response to clear session data from
        """
        pass

class Session:
    """Session data container."""
    
    def __init__(self, data: Dict[str, Any] = None):
        """
        Initialize a session.
        
        Args:
            data: Initial session data
        """
        self._data = data or {}
        self._modified = False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the session.
        
        Args:
            key: The key to get
            default: The default value if key doesn't exist
            
        Returns:
            The value associated with the key, or default
        """
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the session.
        
        Args:
            key: The key to set
            value: The value to set
        """
        self._data[key] = value
        self._modified = True
    
    def delete(self, key: str) -> None:
        """
        Delete a key from the session.
        
        Args:
            key: The key to delete
        """
        if key in self._data:
            del self._data[key]
            self._modified = True
    
    def clear(self) -> None:
        """Clear all session data."""
        self._data.clear()
        self._modified = True
    
    def keys(self):
        """Get session keys."""
        return self._data.keys()
    
    def values(self):
        """Get session values."""
        return self._data.values()
    
    def items(self):
        """Get session items."""
        return self._data.items()
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in session."""
        return key in self._data
    
    def __getitem__(self, key: str) -> Any:
        """Get item from session."""
        return self._data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set item in session."""
        self.set(key, value)
    
    def __delitem__(self, key: str) -> None:
        """Delete item from session."""
        self.delete(key)
    
    @property
    def data(self) -> Dict[str, Any]:
        """Get the session data."""
        return self._data.copy()
    
    @property
    def modified(self) -> bool:
        """Check if session has been modified."""
        return self._modified