import pytest
import time
import asyncio
from starlette.testclient import TestClient

from pacificpy.core.app import PacificApp
from pacificpy.core.endpoints.health import ping_handler, health_handler


@pytest.mark.asyncio
async def test_ping_handler():
    """Test that ping handler returns correct response."""
    # Create a mock request
    class MockRequest:
        pass
    
    request = MockRequest()
    
    # Call ping handler
    response = await ping_handler(request)
    
    # Check response
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    # Parse JSON response
    data = response.body.decode('utf-8')
    import json
    json_data = json.loads(data)
    
    assert json_data == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_handler():
    """Test that health handler returns correct response."""
    # Create a mock request with state
    class MockState:
        def __init__(self):
            self.trace_id = "test-trace-id"
    
    class MockRequest:
        def __init__(self):
            self.state = MockState()
    
    request = MockRequest()
    
    # Call health handler
    response = await health_handler(request)
    
    # Check response
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    # Parse JSON response
    data = response.body.decode('utf-8')
    import json
    json_data = json.loads(data)
    
    # Check health data
    assert json_data["status"] == "ok"
    assert "uptime" in json_data
    assert isinstance(json_data["uptime"], (int, float))
    assert json_data["uptime"] >= 0
    assert "timestamp" in json_data
    assert json_data["trace_id"] == "test-trace-id"


def test_health_endpoints_integration():
    """Test that health endpoints are integrated into PacificApp."""
    # Create app
    app = PacificApp()
    
    # Create test client
    client = TestClient(app)
    
    # Test /ping endpoint
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
    # Test /health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    
    # Check health response data
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime" in data
    assert isinstance(data["uptime"], (int, float))
    assert data["uptime"] >= 0
    assert "timestamp" in data