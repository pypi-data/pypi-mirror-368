"""
HTTP exceptions for PacificPy.

This module provides a base HTTPException class and common HTTP error subclasses
such as BadRequest, NotFound, Forbidden, Unauthorized, and Conflict.
"""

from typing import Any, Dict, Optional, Union

class HTTPException(Exception):
    """Base HTTP exception class."""
    
    def __init__(
        self,
        status_code: int,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize an HTTP exception.
        
        Args:
            status_code: HTTP status code
            detail: Error detail message
            headers: Additional headers to include in the response
        """
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(self.detail)

class BadRequest(HTTPException):
    """HTTP 400 Bad Request exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(400, detail, headers)

class Unauthorized(HTTPException):
    """HTTP 401 Unauthorized exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(401, detail, headers)

class Forbidden(HTTPException):
    """HTTP 403 Forbidden exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(403, detail, headers)

class NotFound(HTTPException):
    """HTTP 404 Not Found exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(404, detail, headers)

class MethodNotAllowed(HTTPException):
    """HTTP 405 Method Not Allowed exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(405, detail, headers)

class NotAcceptable(HTTPException):
    """HTTP 406 Not Acceptable exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(406, detail, headers)

class Conflict(HTTPException):
    """HTTP 409 Conflict exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(409, detail, headers)

class UnsupportedMediaType(HTTPException):
    """HTTP 415 Unsupported Media Type exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(415, detail, headers)

class PayloadTooLarge(HTTPException):
    """HTTP 413 Payload Too Large exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(413, detail, headers)

class UnprocessableEntity(HTTPException):
    """HTTP 422 Unprocessable Entity exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(422, detail, headers)

class TooManyRequests(HTTPException):
    """HTTP 429 Too Many Requests exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(429, detail, headers)

class InternalServerError(HTTPException):
    """HTTP 500 Internal Server Error exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(500, detail, headers)

class NotImplemented(HTTPException):
    """HTTP 501 Not Implemented exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(501, detail, headers)

class BadGateway(HTTPException):
    """HTTP 502 Bad Gateway exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(502, detail, headers)

class ServiceUnavailable(HTTPException):
    """HTTP 503 Service Unavailable exception."""
    
    def __init__(
        self,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(503, detail, headers)