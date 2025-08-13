"""
Tests for request and response validation.

This module contains tests for validating request body, query parameters,
path parameters, file uploads, and response models.
"""

import pytest
from pydantic import BaseModel, Field
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from typing import List, Optional

from pacificpy.validation.request import request_validator
from pacificpy.validation.response import response_serializer
from pacificpy.validation.params import validate_query_params
from pacificpy.validation.files import validate_file_upload

# Test models
class UserCreate(BaseModel):
    """Test model for user creation."""
    username: str
    email: str
    age: int

class UserResponse(BaseModel):
    """Test model for user response."""
    id: int
    username: str
    email: str
    age: int

# Test routes
@request_validator(UserCreate)
@response_serializer(UserResponse)
async def create_user(request, usercreate: UserCreate):
    """Test route for creating a user."""
    # Simulate creating a user
    user_data = {
        "id": 1,
        "username": usercreate.username,
        "email": usercreate.email,
        "age": usercreate.age
    }
    return user_data

async def list_users(request):
    """Test route for listing users with query params."""
    # Validate query parameters
    param_types = {
        "limit": int,
        "offset": int,
        "active": bool
    }
    validated_params = validate_query_params(dict(request.query_params), param_types)
    
    return JSONResponse({
        "users": [],
        "limit": validated_params.get("limit", 10),
        "offset": validated_params.get("offset", 0),
        "active": validated_params.get("active", True)
    })

# Test app
app = Starlette(routes=[
    Route("/users", create_user, methods=["POST"]),
    Route("/users", list_users, methods=["GET"]),
])

# Test client
client = TestClient(app)

# Tests
def test_body_validation_success():
    """Test successful body validation."""
    response = client.post("/users", json={
        "username": "testuser",
        "email": "test@example.com",
        "age": 25
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["age"] == 25

def test_body_validation_error():
    """Test body validation error."""
    response = client.post("/users", json={
        "username": "testuser",
        "email": "invalid-email",  # Invalid email format
        "age": "not-a-number"      # Invalid type
    })
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert len(data["detail"]) == 2

def test_query_param_validation():
    """Test query parameter validation."""
    response = client.get("/users?limit=20&offset=10&active=true")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 20
    assert data["offset"] == 10
    assert data["active"] is True

def test_query_param_validation_error():
    """Test query parameter validation error."""
    response = client.get("/users?limit=not-a-number")
    assert response.status_code == 400

def test_response_serialization():
    """Test response model serialization."""
    response = client.post("/users", json={
        "username": "testuser",
        "email": "test@example.com",
        "age": 25
    })
    assert response.status_code == 200
    data = response.json()
    # Check that response matches UserResponse model
    assert "id" in data
    assert "username" in data
    assert "email" in data
    assert "age" in data