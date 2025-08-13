"""
Dependency Injection: Depends helper
"""
from typing import Callable, Any, Union, get_type_hints
from dataclasses import dataclass

# Type alias for callable or class
CallableOrClass = Union[Callable[..., Any], type]

@dataclass
class Dependency:
    """Represents a dependency that can be resolved by the DI system."""
    callable_or_class: CallableOrClass
    use_cache: bool = True
    
    def __post_init__(self):
        # Store type hints for later validation
        try:
            self.type_hints = get_type_hints(self.callable_or_class)
        except (NameError, AttributeError):
            # In case of forward references or other issues
            self.type_hints = {}

class Depends:
    """
    Marks a parameter in a handler signature as a dependency.
    Similar to FastAPI's Depends but adapted for PacificPy.
    """
    def __init__(self, dependency: Union[CallableOrClass, Dependency], *, use_cache: bool = True):
        if isinstance(dependency, Dependency):
            self.dependency = dependency
        else:
            self.dependency = Dependency(dependency, use_cache=use_cache)
        
    def __repr__(self):
        callable_or_class = self.dependency.callable_or_class
        name = getattr(callable_or_class, '__name__', str(callable_or_class))
        return f"Depends({name})"