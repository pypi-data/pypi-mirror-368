"""
Validation helpers for safe request parsing.

This module provides utilities for safely parsing request bodies with
size limits and content-type validation to prevent DoS attacks.
"""

import json
from typing import Any, Dict
from starlette.requests import Request
from ..errors.http import BadRequest, UnsupportedMediaType, PayloadTooLarge

# Default maximum body size (1 MB)
DEFAULT_MAX_BODY_SIZE = 1024 * 1024

async def parse_json_body_safe(
    request: Request,
    max_body_size: int = DEFAULT_MAX_BODY_SIZE
) -> Dict[str, Any]:
    """
    Safely parse JSON body with size limits and content-type validation.
    
    Args:
        request: The incoming request
        max_body_size: Maximum allowed body size in bytes (default: 1MB)
        
    Returns:
        Parsed JSON data as a dictionary
        
    Raises:
        UnsupportedMediaType: If content-type is not application/json
        PayloadTooLarge: If body size exceeds the limit
        BadRequest: If JSON is invalid
    """
    # Check content type
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        raise UnsupportedMediaType("Content-Type must be application/json")
    
    # Check content length
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            length = int(content_length)
            if length > max_body_size:
                raise PayloadTooLarge(f"Request body too large (max: {max_body_size} bytes)")
        except ValueError:
            # If we can't parse content-length, we'll check during reading
            pass
    
    # Read body with size limit
    try:
        body = await request.body()
    except Exception:
        # If reading fails, it might be due to size limits in the server
        raise PayloadTooLarge(f"Request body too large (max: {max_body_size} bytes)")
    
    # Check body size
    if len(body) > max_body_size:
        raise PayloadTooLarge(f"Request body too large (max: {max_body_size} bytes)")
    
    # Parse JSON
    try:
        data = json.loads(body.decode("utf-8"))
        return data
    except json.JSONDecodeError:
        raise BadRequest("Invalid JSON in request body")