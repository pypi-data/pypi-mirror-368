"""
Response model serialization using Pydantic v2.

This module provides automatic serialization of Pydantic models to JSON responses,
with support for exclude_none and by_alias options.
"""

from typing import Any, List, Type, Union, get_origin, get_args
from pydantic import BaseModel
from starlette.responses import JSONResponse

def serialize_response(
    response_data: Any,
    response_model: Type[BaseModel] = None,
    exclude_none: bool = False,
    by_alias: bool = False
) -> JSONResponse:
    """
    Serialize response data using a Pydantic model.
    
    Args:
        response_data: The data to serialize (can be a model instance, list of models, or dict)
        response_model: The Pydantic model class to use for serialization
        exclude_none: Whether to exclude fields with None values
        by_alias: Whether to use field aliases in the output
        
    Returns:
        A JSONResponse with the serialized data
    """
    # If response_data is already a dict, use it directly
    if isinstance(response_data, dict):
        return JSONResponse(response_data)
    
    # Handle list of models
    if isinstance(response_data, list):
        serialized_data = [
            _serialize_model(item, response_model, exclude_none, by_alias) 
            for item in response_data
        ]
        return JSONResponse(serialized_data)
    
    # Handle single model
    serialized_data = _serialize_model(response_data, response_model, exclude_none, by_alias)
    return JSONResponse(serialized_data)

def _serialize_model(
    data: Any,
    model_class: Type[BaseModel],
    exclude_none: bool,
    by_alias: bool
) -> dict:
    """
    Serialize a single model instance.
    
    Args:
        data: The model instance to serialize
        model_class: The Pydantic model class
        exclude_none: Whether to exclude fields with None values
        by_alias: Whether to use field aliases in the output
        
    Returns:
        A dictionary representation of the model
    """
    # If data is already a model instance, use its model_dump method
    if isinstance(data, BaseModel):
        return data.model_dump(exclude_none=exclude_none, by_alias=by_alias)
    
    # If we have a model class, try to create an instance from the data
    if model_class and isinstance(data, dict):
        model_instance = model_class(**data)
        return model_instance.model_dump(exclude_none=exclude_none, by_alias=by_alias)
    
    # If no model class is provided, return data as-is
    return data

def response_serializer(
    response_model: Type[BaseModel] = None,
    exclude_none: bool = False,
    by_alias: bool = False
) -> callable:
    """
    Decorator to automatically serialize handler responses using a Pydantic model.
    
    Args:
        response_model: The Pydantic model class to use for serialization
        exclude_none: Whether to exclude fields with None values
        by_alias: Whether to use field aliases in the output
        
    Returns:
        A decorator that can be applied to response handlers
    """
    def decorator(handler: callable) -> callable:
        async def wrapper(*args, **kwargs) -> JSONResponse:
            # Call the original handler
            response_data = await handler(*args, **kwargs)
            
            # Serialize the response data
            return serialize_response(
                response_data, 
                response_model, 
                exclude_none=exclude_none, 
                by_alias=by_alias
            )
        return wrapper
    return decorator