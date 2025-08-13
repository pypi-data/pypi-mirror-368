"""
Dependency Injection: Testing utilities
"""
from contextlib import contextmanager
from typing import Dict, Callable, Any

class DependencyOverrides:
    """
    Manages dependency overrides for testing.
    """
    
    def __init__(self):
        self._overrides: Dict[Callable, Callable] = {}
    
    def add_override(self, original: Callable, override: Callable) -> None:
        """
        Add a dependency override.
        
        Args:
            original: The original dependency to override
            override: The replacement dependency
        """
        self._overrides[original] = override
    
    def remove_override(self, original: Callable) -> None:
        """
        Remove a dependency override.
        
        Args:
            original: The original dependency to remove the override for
        """
        self._overrides.pop(original, None)
    
    def clear_overrides(self) -> None:
        """Clear all dependency overrides."""
        self._overrides.clear()
    
    def get_overrides(self) -> Dict[Callable, Callable]:
        """
        Get all current overrides.
        
        Returns:
            Dictionary of overrides
        """
        return self._overrides.copy()

# Global instance for application-wide overrides
_app_dependency_overrides = DependencyOverrides()

def set_app_dependency_override(original: Callable, override: Callable) -> None:
    """
    Set an application-wide dependency override.
    
    Args:
        original: The original dependency to override
        override: The replacement dependency
    """
    _app_dependency_overrides.add_override(original, override)

def clear_app_dependency_overrides() -> None:
    """Clear all application-wide dependency overrides."""
    _app_dependency_overrides.clear_overrides()

def get_app_dependency_overrides() -> Dict[Callable, Callable]:
    """
    Get all application-wide dependency overrides.
    
    Returns:
        Dictionary of overrides
    """
    return _app_dependency_overrides.get_overrides()

@contextmanager
def override_dependencies(overrides: Dict[Callable, Callable]):
    """
    Context manager for temporarily overriding dependencies in tests.
    
    Args:
        overrides: Dictionary mapping original dependencies to their replacements
        
    Example:
        with override_dependencies({db_client: mock_db_client}):
            response = client.get('/api/users')
    """
    original_overrides = _app_dependency_overrides.get_overrides()
    
    try:
        # Add new overrides
        for original, override in overrides.items():
            _app_dependency_overrides.add_override(original, override)
        
        yield _app_dependency_overrides.get_overrides()
    finally:
        # Restore original overrides
        _app_dependency_overrides.clear_overrides()
        for original, override in original_overrides.items():
            _app_dependency_overrides.add_override(original, override)