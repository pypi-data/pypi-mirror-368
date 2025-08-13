import os
import pytest
from pacificpy.routing import discover_endpoints, APIRouter, Route


def test_discover_endpoints_basic():
    """Test basic endpoint discovery."""
    # Path to our test endpoints directory
    endpoints_path = os.path.join(
        os.path.dirname(__file__), 
        "..", "examples", "demo", "endpoints"
    )
    
    # Discover endpoints
    router = discover_endpoints(endpoints_path)
    
    # Check that we got an APIRouter
    assert isinstance(router, APIRouter)
    
    # Check that we found some routes
    routes = router.get_routes()
    assert len(routes) > 0
    
    # Check for specific routes
    route_paths = [route.path for route in routes]
    assert "/users" in route_paths
    assert "/users/{user_id}" in route_paths
    assert "/posts" in route_paths
    assert "/posts/{post_id}" in route_paths
    
    # Verify we have both GET and POST methods for /users
    users_routes = [r for r in routes if r.path == "/users"]
    assert len(users_routes) == 2  # Two routes with same path but different methods
    
    # Check that one has GET and one has POST
    methods = []
    for route in users_routes:
        methods.extend(route.methods)
    
    assert "GET" in methods
    assert "POST" in methods


def test_discover_endpoints_ignored_files():
    """Test that files starting with underscore are ignored."""
    endpoints_path = os.path.join(
        os.path.dirname(__file__), 
        "..", "examples", "demo", "endpoints"
    )
    
    router = discover_endpoints(endpoints_path)
    routes = router.get_routes()
    
    # Check that the ignored endpoint is not in the routes
    route_paths = [route.path for route in routes]
    assert "/ignored" not in route_paths


def test_discover_endpoints_nonexistent_path():
    """Test discovery with nonexistent path."""
    with pytest.raises(FileNotFoundError):
        discover_endpoints("/path/that/does/not/exist")


def test_discover_endpoints_not_directory():
    """Test discovery with a file instead of directory."""
    file_path = os.path.join(
        os.path.dirname(__file__), 
        "..", "examples", "demo", "endpoints", "users.py"
    )
    
    with pytest.raises(ValueError):
        discover_endpoints(file_path)


def test_discover_endpoints_empty_directory():
    """Test discovery with empty directory."""
    # Create a temporary empty directory
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        router = discover_endpoints(temp_dir)
        assert isinstance(router, APIRouter)
        assert len(router.get_routes()) == 0


def test_discover_endpoints_with_package():
    """Test discovery with package parameter."""
    endpoints_path = os.path.join(
        os.path.dirname(__file__), 
        "..", "examples", "demo", "endpoints"
    )
    
    # This should work even with a package parameter
    router = discover_endpoints(endpoints_path, package="examples.demo.endpoints")
    assert isinstance(router, APIRouter)
    
    # Should still find routes
    routes = router.get_routes()
    assert len(routes) > 0