import pytest
from pacificpy.routing import Route


def example_handler():
    pass


def test_route_creation():
    """Test creating a Route instance with valid parameters."""
    route = Route(
        path="/test",
        methods=["GET", "POST"],
        handler=example_handler,
        name="test_route"
    )
    
    assert route.path == "/test"
    assert route.methods == ["GET", "POST"]
    assert route.handler == example_handler
    assert route.name == "test_route"
    assert route.dependencies == []
    assert route.responses == {}


def test_route_creation_with_string_method():
    """Test creating a Route with a single string method."""
    route = Route(
        path="/test",
        methods="GET",
        handler=example_handler
    )
    
    assert route.methods == ["GET"]


def test_route_repr():
    """Test the Route repr method."""
    route = Route(
        path="/test",
        methods=["GET"],
        handler=example_handler,
        name="test_route"
    )
    
    repr_str = repr(route)
    assert "Route(" in repr_str
    assert "path='/test'" in repr_str
    assert "methods=[GET]" in repr_str
    assert "handler=example_handler" in repr_str
    assert "name='test_route'" in repr_str


def test_route_validation_path_must_start_with_slash():
    """Test that path must start with a slash."""
    with pytest.raises(ValueError, match="Path must start with '/'"):
        Route(
            path="test",  # Missing leading slash
            methods=["GET"],
            handler=example_handler
        )


def test_route_validation_invalid_method():
    """Test that invalid HTTP methods are rejected."""
    with pytest.raises(ValueError, match="Invalid HTTP method"):
        Route(
            path="/test",
            methods=["INVALID"],
            handler=example_handler
        )


def test_route_validation_non_callable_handler():
    """Test that handler must be callable."""
    with pytest.raises(TypeError, match="Handler must be callable"):
        Route(
            path="/test",
            methods=["GET"],
            handler="not_callable"
        )


def test_route_with_dependencies_and_responses():
    """Test creating a Route with dependencies and responses."""
    dependencies = ["dep1", "dep2"]
    responses = {200: {"description": "Success"}}
    
    route = Route(
        path="/test",
        methods=["GET"],
        handler=example_handler,
        dependencies=dependencies,
        responses=responses
    )
    
    assert route.dependencies == dependencies
    assert route.responses == responses
    assert route.has_dependencies is True
    assert route.has_responses is True


def test_route_methods_normalization():
    """Test that methods are normalized to uppercase."""
    route = Route(
        path="/test",
        methods=["get", "post"],
        handler=example_handler
    )
    
    assert route.methods == ["GET", "POST"]