"""
Request validation wrapper using Pydantic v2.

This module provides automatic parsing of request body/params/query into Pydantic models
based on handler type hints. Supports JSON and form data.
"""

from typing import Any, Callable, Dict, Optional, Type, Union
from pydantic import BaseModel, ValidationError
import json
from starlette.requests import Request
from starlette.datastructures import FormData
from ..errors.http import BadRequest
from ..errors.handler import handle_validation_error

async def parse_request_data(
    request: Request,
    model_class: Type[BaseModel],
    location: str = "body"
) -> BaseModel:
    """
    Parse request data into a Pydantic model.
    
    Args:
        request: The incoming request
        model_class: The Pydantic model class to parse into
        location: Where to get data from ("body", "query", "path", "form")
        
    Returns:
        An instance of the model_class populated with request data
        
    Raises:
        BadRequest: If validation fails or data cannot be parsed
    """
    try:
        if location == "body":
            return await _parse_body(request, model_class)
        elif location == "query":
            return _parse_query(request, model_class)
        elif location == "path":
            return _parse_path(request, model_class)
        elif location == "form":
            return await _parse_form(request, model_class)
        else:
            raise ValueError(f"Unsupported location: {location}")
    except ValidationError as e:
        # Convert Pydantic validation errors to HTTP 400
        raise handle_validation_error(e)

async def _parse_body(request: Request, model_class: Type[BaseModel]) -> BaseModel:
    """Parse JSON body data into a Pydantic model."""
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        raise BadRequest("Content-Type must be application/json")
    
    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise BadRequest("Invalid JSON in request body")
    
    return model_class(**body)

def _parse_query(request: Request, model_class: Type[BaseModel]) -> BaseModel:
    """Parse query parameters into a Pydantic model."""
    # Convert query params to dict, handling multiple values
    query_dict = {}
    for key, value in request.query_params.multi_items():
        if key in query_dict:
            # Handle multiple values for same key
            if not isinstance(query_dict[key], list):
                query_dict[key] = [query_dict[key]]
            query_dict[key].append(value)
        else:
            query_dict[key] = value
    
    return model_class(**query_dict)

def _parse_path(request: Request, model_class: Type[BaseModel]) -> BaseModel:
    """Parse path parameters into a Pydantic model."""
    # Path params are typically in request.path_params
    return model_class(**getattr(request, "path_params", {}))

async def _parse_form(request: Request, model_class: Type[BaseModel]) -> BaseModel:
    """Parse form data into a Pydantic model."""
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" not in content_type and "application/x-www-form-urlencoded" not in content_type:
        raise BadRequest("Content-Type must be multipart/form-data or application/x-www-form-urlencoded")
    
    form_data = await request.form()
    form_dict = _convert_form_data_to_dict(form_data)
    return model_class(**form_dict)

def _convert_form_data_to_dict(form_data: FormData) -> Dict[str, Any]:
    """Convert Starlette FormData to a dictionary, handling multiple values."""
    result = {}
    for key, value in form_data.multi_items():
        if key in result:
            # Handle multiple values for same key
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(value)
        else:
            result[key] = value
    return result

def request_validator(
    model_class: Type[BaseModel],
    location: str = "body"
) -> Callable:
    """
    Decorator to automatically validate request data using a Pydantic model.
    
    Args:
        model_class: The Pydantic model class to validate against
        location: Where to get data from ("body", "query", "path", "form")
        
    Returns:
        A decorator that can be applied to request handlers
    """
    def decorator(handler: Callable) -> Callable:
        async def wrapper(request: Request, *args, **kwargs) -> Any:
            # Parse and validate request data
            validated_data = await parse_request_data(request, model_class, location)
            
            # Add validated data to kwargs so handler can access it
            kwargs[model_class.__name__.lower()] = validated_data
            
            # Call the original handler
            return await handler(request, *args, **kwargs)
        return wrapper
    return decorator