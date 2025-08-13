"""
Query and path parameter validation using Pydantic.

This module provides utilities for validating and converting query and path parameters
to their specified types using Pydantic.
"""

from typing import Any, Dict, List, Type, Union, get_origin, get_args
from pydantic import BaseModel, ValidationError, create_model
from ..errors.http import BadRequest
from .errors import handle_validation_error

def validate_query_params(
    query_dict: Dict[str, Any],
    param_types: Dict[str, Type]
) -> Dict[str, Any]:
    """
    Validate and convert query parameters to their specified types.
    
    Args:
        query_dict: Dictionary of query parameters
        param_types: Dictionary mapping parameter names to their types
        
    Returns:
        A dictionary with validated and converted parameters
        
    Raises:
        BadRequest: If validation fails
    """
    # Create a Pydantic model for validation
    fields = {
        name: (param_type, ...) 
        for name, param_type in param_types.items()
    }
    Model = create_model("QueryParams", **fields)
    
    try:
        # Validate the query parameters
        validated = Model(**query_dict)
        return validated.model_dump()
    except ValidationError as e:
        raise handle_validation_error(e)

def validate_path_params(
    path_dict: Dict[str, Any],
    param_types: Dict[str, Type]
) -> Dict[str, Any]:
    """
    Validate and convert path parameters to their specified types.
    
    Args:
        path_dict: Dictionary of path parameters
        param_types: Dictionary mapping parameter names to their types
        
    Returns:
        A dictionary with validated and converted parameters
        
    Raises:
        BadRequest: If validation fails
    """
    # Path parameter validation is similar to query params
    return validate_query_params(path_dict, param_types)

def convert_param_value(value: Any, param_type: Type) -> Any:
    """
    Convert a parameter value to its specified type.
    
    Args:
        value: The parameter value to convert
        param_type: The target type
        
    Returns:
        The converted value
        
    Raises:
        ValueError: If conversion fails
    """
    # Handle list types
    if get_origin(param_type) is list or param_type is List:
        # Get the inner type if it's a List[type]
        inner_type = get_args(param_type)[0] if get_args(param_type) else str
        
        # Handle list values
        if isinstance(value, list):
            return [convert_param_value(item, inner_type) for item in value]
        elif isinstance(value, str):
            # Split comma-separated values
            items = value.split(",")
            return [convert_param_value(item.strip(), inner_type) for item in items]
        else:
            return [convert_param_value(value, inner_type)]
    
    # Handle boolean values
    if param_type is bool:
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        elif isinstance(value, (int, float)):
            return value == 1
        else:
            return bool(value)
    
    # Handle integer values
    if param_type is int:
        if isinstance(value, int):
            return value
        elif isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to int")
        else:
            return int(value)
    
    # Handle string values
    if param_type is str:
        return str(value)
    
    # For other types, try direct conversion
    return param_type(value)