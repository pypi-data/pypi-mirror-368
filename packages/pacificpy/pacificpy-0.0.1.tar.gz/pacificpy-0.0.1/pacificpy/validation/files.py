"""
File upload validation for multipart/form-data.

This module provides utilities for validating file uploads,
including size limits, mime-type checking, and Pydantic integration.
"""

import mimetypes
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from starlette.datastructures import UploadFile
from starlette.requests import Request
from ..errors.http import BadRequest, PayloadTooLarge, UnsupportedMediaType

# Default file size limit (5 MB)
DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024

# Default allowed mime types
DEFAULT_ALLOWED_MIME_TYPES = {
    "text/plain",
    "application/json",
    "image/jpeg",
    "image/png",
    "application/pdf"
}

class FileUpload(BaseModel):
    """Pydantic model for file upload validation."""
    filename: str
    content_type: str
    size: int
    file: Union[bytes, UploadFile]
    
    class Config:
        arbitrary_types_allowed = True

async def validate_file_upload(
    request: Request,
    field_name: str,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
    allowed_mime_types: set = None
) -> FileUpload:
    """
    Validate a file upload from a multipart/form-data request.
    
    Args:
        request: The incoming request
        field_name: The name of the file field in the form
        max_file_size: Maximum allowed file size in bytes
        allowed_mime_types: Set of allowed mime types
        
    Returns:
        A FileUpload instance with validated file data
        
    Raises:
        BadRequest: If file is missing or invalid
        PayloadTooLarge: If file size exceeds the limit
        UnsupportedMediaType: If mime type is not allowed
    """
    # Get form data
    form = await request.form()
    
    # Check if file field exists
    if field_name not in form:
        raise BadRequest(f"Missing file field: {field_name}")
    
    # Get the uploaded file
    uploaded_file = form[field_name]
    
    # Check if it's actually a file
    if not isinstance(uploaded_file, UploadFile):
        raise BadRequest(f"Field {field_name} is not a file")
    
    # Check file size
    if uploaded_file.size > max_file_size:
        raise PayloadTooLarge(f"File too large (max: {max_file_size} bytes)")
    
    # Check mime type
    allowed_mimes = allowed_mime_types or DEFAULT_ALLOWED_MIME_TYPES
    if uploaded_file.content_type not in allowed_mimes:
        raise UnsupportedMediaType(
            f"Unsupported file type: {uploaded_file.content_type}"
        )
    
    # Create FileUpload instance
    return FileUpload(
        filename=uploaded_file.filename,
        content_type=uploaded_file.content_type,
        size=uploaded_file.size,
        file=uploaded_file
    )

async def validate_multiple_files(
    request: Request,
    field_name: str,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
    allowed_mime_types: set = None,
    max_files: int = 10
) -> List[FileUpload]:
    """
    Validate multiple file uploads from a multipart/form-data request.
    
    Args:
        request: The incoming request
        field_name: The name of the file field in the form
        max_file_size: Maximum allowed file size in bytes per file
        allowed_mime_types: Set of allowed mime types
        max_files: Maximum number of files allowed
        
    Returns:
        A list of FileUpload instances with validated file data
        
    Raises:
        BadRequest: If files are missing or invalid
        PayloadTooLarge: If file size exceeds the limit
        UnsupportedMediaType: If mime type is not allowed
    """
    # Get form data
    form = await request.form()
    
    # Get all files with the specified field name
    files = form.getlist(field_name)
    
    # Check number of files
    if len(files) > max_files:
        raise BadRequest(f"Too many files (max: {max_files})")
    
    # Validate each file
    validated_files = []
    for uploaded_file in files:
        # Check if it's actually a file
        if not isinstance(uploaded_file, UploadFile):
            raise BadRequest(f"Field {field_name} contains non-file data")
        
        # Check file size
        if uploaded_file.size > max_file_size:
            raise PayloadTooLarge(f"File too large (max: {max_file_size} bytes)")
        
        # Check mime type
        allowed_mimes = allowed_mime_types or DEFAULT_ALLOWED_MIME_TYPES
        if uploaded_file.content_type not in allowed_mimes:
            raise UnsupportedMediaType(
                f"Unsupported file type: {uploaded_file.content_type}"
            )
        
        # Create FileUpload instance
        validated_files.append(FileUpload(
            filename=uploaded_file.filename,
            content_type=uploaded_file.content_type,
            size=uploaded_file.size,
            file=uploaded_file
        ))
    
    return validated_files