"""
Dependency Injection: Type validation
"""
import inspect
from typing import get_type_hints, Any, Callable
from .dependency import Depends

class TypeValidationError(Exception):
    """Raised when there's a type mismatch in dependency injection."""
    pass

def validate_dependency_types(handler: Callable, dependencies: dict) -> None:
    """
    Validate that dependency types match the expected types in the handler signature.
    
    Args:
        handler: The handler function to validate
        dependencies: Dictionary of resolved dependencies
        
    Raises:
        TypeValidationError: If there's a type mismatch
    """
    try:
        type_hints = get_type_hints(handler)
    except (NameError, AttributeError):
        # Skip validation if we can't get type hints
        return
    
    sig = inspect.signature(handler)
    
    for param_name, param in sig.parameters.items():
        # Skip parameters without type annotations
        if param_name not in type_hints:
            continue
            
        expected_type = type_hints[param_name]
        
        # Skip validation for non-dependency parameters
        if not isinstance(param.annotation, Depends) and not isinstance(param.default, Depends):
            continue
            
        # Check if this parameter has a resolved dependency
        if param_name in dependencies:
            actual_value = dependencies[param_name]
            actual_type = type(actual_value)
            
            # For Depends parameters, check if the actual type matches expected type
            if not _is_type_compatible(actual_type, expected_type):
                raise TypeValidationError(
                    f"Type mismatch for parameter '{param_name}' in {handler.__name__}. "
                    f"Expected {expected_type}, got {actual_type}."
                )

def _is_type_compatible(actual_type: type, expected_type: type) -> bool:
    """
    Check if actual_type is compatible with expected_type.
    
    Args:
        actual_type: The actual type of the value
        expected_type: The expected type from the type hint
        
    Returns:
        True if the types are compatible, False otherwise
    """
    # Handle basic type compatibility
    if expected_type is Any:
        return True
    
    # Direct type match
    if actual_type == expected_type:
        return True
    
    # Handle subclass relationships
    try:
        if issubclass(actual_type, expected_type):
            return True
    except TypeError:
        # Handle cases where issubclass fails (e.g., with generic types)
        pass
    
    # For callable types, check if both are callable
    if expected_type is Callable and callable(actual_type):
        return True
    
    return False