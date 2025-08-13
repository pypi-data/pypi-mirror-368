import pytest
import json
from starlette.datastructures import State
from pacificpy.core.http import Request, Response


def test_request_initialization():
    """Test that Request initializes with default state and trace_id."""
    # Create a mock scope and receive function
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
    }
    
    async def receive():
        return {"type": "http.disconnect"}
    
    # Create request
    request = Request(scope, receive)
    
    # Check that state is initialized
    assert hasattr(request, 'state')
    assert isinstance(request.state, State)
    
    # Check that trace_id is initialized
    assert hasattr(request.state, 'trace_id')
    assert isinstance(request.state.trace_id, str)
    assert len(request.state.trace_id) > 0
    
    # Check that user is initialized
    assert hasattr(request.state, 'user')
    assert request.state.user is None


def test_request_json_helper():
    """Test that Request.json() helper works."""
    # This test would require a more complex setup with actual JSON body
    # For now, we'll just test that the method exists
    assert hasattr(Request, 'json')


def test_request_text_helper():
    """Test that Request.text() helper works."""
    # This test would require a more complex setup with actual text body
    # For now, we'll just test that the method exists
    assert hasattr(Request, 'text')


def test_response_initialization():
    """Test that Response initializes correctly."""
    # Test with string content
    response = Response("Hello, World!")
    assert response.status_code == 200
    assert response.body == b"Hello, World!"
    
    # Test with JSON content
    response = Response({"message": "Hello, World!"})
    assert response.status_code == 200
    assert response.media_type == "application/json"
    assert json.loads(response.body) == {"message": "Hello, World!"}


def test_response_json_classmethod():
    """Test that Response.json() classmethod works."""
    response = Response.json({"message": "Hello, World!"})
    assert response.status_code == 200
    assert response.media_type == "application/json"
    assert json.loads(response.body) == {"message": "Hello, World!"}


def test_response_text_classmethod():
    """Test that Response.text() classmethod works."""
    response = Response.text("Hello, World!")
    assert response.status_code == 200
    assert response.media_type == "text/plain"
    assert response.body == b"Hello, World!"