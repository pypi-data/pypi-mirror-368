"""
DI integration for request validation.

This module provides integration between the validation system and
the dependency injection system, automatically validating dependencies
that return Pydantic models.
"""

from typing import Any, Callable, Type, get_type_hints
from pydantic import BaseModel, ValidationError
from ..errors.http import InternalServerError
from ..di import Dependency
from .request import parse_request_data
from .errors import handle_validation_error
from starlette.requests import Request

async def validate_dependency_result(
    dependency: Dependency,
    result: Any,
    request: Request
) -> Any:
    """
    Validate a dependency's result if it's annotated with a Pydantic model.
    
    Args:
        dependency: The dependency that was resolved
        result: The result of the dependency resolution
        request: The current request
        
    Returns:
        The validated result
        
    Raises:
        InternalServerError: If validation fails
    """
    # Get the return type annotation of the dependency
    type_hints = get_type_hints(dependency.func)
    return_type = type_hints.get("return")
    
    # Check if the return type is a Pydantic model
    if return_type and isinstance(return_type, type) and issubclass(return_type, BaseModel):
        try:
            # If result is already a model instance, validate it
            if isinstance(result, return_type):
                # Re-validate to ensure it's valid
                return return_type(**result.model_dump())
            # If result is a dict, create a model instance from it
            elif isinstance(result, dict):
                return return_type(**result)
            # If result is something else, try to validate it directly
            else:
                return return_type(result)
        except ValidationError as e:
            # In development, provide detailed error information
            if getattr(request.app, "debug", False):
                raise InternalServerError(f"Dependency validation failed: {e}")
            else:
                # In production, provide a generic error
                raise InternalServerError("Internal server error")
        except Exception as e:
            # Handle other validation errors
            if getattr(request.app, "debug", False):
                raise InternalServerError(f"Dependency validation error: {e}")
            else:
                raise InternalServerError("Internal server error")
    
    # If not a Pydantic model, return the result as-is
    return result

def validated_dependency(dependency_func: Callable) -> Callable:
    """
    Decorator to mark a dependency function for automatic validation.
    
    Args:
        dependency_func: The dependency function to decorate
        
    Returns:
        The decorated dependency function
    """
    # Mark the dependency for validation
    dependency_func._validated = True
    return dependency_func