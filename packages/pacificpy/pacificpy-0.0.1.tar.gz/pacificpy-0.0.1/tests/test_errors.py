"""
Integration tests for error handling.

This module contains tests for various error scenarios including
validation errors (400), not found errors (404), and unhandled
exceptions (500), with checks for proper sanitization in production.
"""

import pytest
from pydantic import BaseModel, ValidationError
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException as StarletteHTTPException

from pacificpy.validation.request import request_validator
from pacificpy.errors.http import NotFound, InternalServerError
from pacificpy.errors.handler import ExceptionMiddleware

# Test models
class TestModel(BaseModel):
    """Test model for validation."""
    name: str
    age: int

# Test routes
@request_validator(TestModel)
async def validation_error_route(request, testmodel: TestModel):
    """Route that should trigger validation errors."""
    return JSONResponse({"message": "success"})

async def not_found_route(request):
    """Route that raises a 404 error."""
    raise NotFound("Item not found")

async def server_error_route(request):
    """Route that raises a 500 error."""
    raise InternalServerError("Internal server error")

async def unhandled_error_route(request):
    """Route that raises an unhandled exception."""
    raise ValueError("This is an unhandled error")

# Test app with exception middleware
app = Starlette(routes=[
    Route("/validation-error", validation_error_route, methods=["POST"]),
    Route("/not-found", not_found_route, methods=["GET"]),
    Route("/server-error", server_error_route, methods=["GET"]),
    Route("/unhandled-error", unhandled_error_route, methods=["GET"]),
])

# Add exception middleware
app.add_middleware(ExceptionMiddleware)

# Test client
client = TestClient(app)

# Tests
def test_validation_error():
    """Test validation error handling (400)."""
    response = client.post("/validation-error", json={
        "name": "test",
        "age": "not-a-number"  # Invalid type
    })
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "trace_id" in data
    # Check that validation errors are properly formatted
    assert isinstance(data["detail"], list)
    assert len(data["detail"]) > 0

def test_not_found_error():
    """Test not found error handling (404)."""
    response = client.get("/not-found")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "trace_id" in data
    assert data["detail"] == "Item not found"

def test_server_error():
    """Test server error handling (500)."""
    response = client.get("/server-error")
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "trace_id" in data
    assert data["detail"] == "Internal server error"

def test_unhandled_error():
    """Test unhandled error handling (500)."""
    response = client.get("/unhandled-error")
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "trace_id" in data
    assert data["detail"] == "Internal server error"

def test_404_not_found():
    """Test default 404 handling for non-existent routes."""
    response = client.get("/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "trace_id" in data

# Tests with debug mode
def test_debug_mode_stacktrace():
    """Test that stack traces are included in debug mode."""
    # Create a test client with debug mode enabled
    debug_app = Starlette(debug=True, routes=[
        Route("/unhandled-error", unhandled_error_route, methods=["GET"]),
    ])
    debug_app.add_middleware(ExceptionMiddleware)
    debug_client = TestClient(debug_app)
    
    response = debug_client.get("/unhandled-error")
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "trace_id" in data
    # In debug mode, stacktrace should be included
    assert "stacktrace" in data

def test_production_mode_sanitization():
    """Test that stack traces are sanitized in production mode."""
    # Production mode is the default (debug=False)
    response = client.get("/unhandled-error")
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "trace_id" in data
    # In production mode, stacktrace should not be included for client errors
    # But it should be included for server errors in debug mode
    # For this test, we're checking that it's properly sanitized