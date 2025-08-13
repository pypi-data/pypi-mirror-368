"""
Centralized validation error formatting.

This module provides consistent JSON formatting for Pydantic validation errors
in the style of OpenAPI: {"detail": [{"loc":..., "msg":..., "type":...}]}
"""

from typing import List, Dict, Any
from pydantic import ValidationError
from ..errors.http import BadRequest

def format_validation_error(error: ValidationError) -> Dict[str, Any]:
    """
    Format a Pydantic ValidationError into a consistent JSON structure.
    
    Args:
        error: The Pydantic ValidationError to format
        
    Returns:
        A dictionary with the error details in OpenAPI style
    """
    details = []
    for err in error.errors():
        detail = {
            "loc": list(err["loc"]),
            "msg": err["msg"],
            "type": err["type"]
        }
        details.append(detail)
    
    return {"detail": details}

def handle_validation_error(error: ValidationError) -> BadRequest:
    """
    Convert a Pydantic ValidationError to an HTTP 400 BadRequest exception
    with formatted error details.
    
    Args:
        error: The Pydantic ValidationError to convert
        
    Returns:
        A BadRequest exception with JSON formatted error details
    """
    formatted_error = format_validation_error(error)
    return BadRequest(formatted_error)