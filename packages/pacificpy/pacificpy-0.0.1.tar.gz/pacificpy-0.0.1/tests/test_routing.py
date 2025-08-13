import pytest
import uuid
from pacificpy.routing import (
    Route, 
    APIRouter, 
    discover_endpoints, 
    get, 
    post, 
    put, 
    delete,
    route,
    infer_http_methods,
    parse_path_template,
    convert_path_params
)


# Test handlers
def example_handler():
    return {"message": "Hello World"}


def get_users():
    """Get list of users."""
    return {"users": ["Alice", "Bob"]}


def create_user():
    """Create a new user."""
    return {"message": "User created"}


def update_user(user_id: str):
    """Update a user."""
    return {"message": f"User {user_id} updated"}


def delete_user(user_id: str):
    """Delete a user."""
    return {"message": f"User {user_id} deleted"}


def test_route_registration():
    """Test basic route registration."""
    # Create a router
    router = APIRouter()
    
    # Create and register routes
    get_route = Route("/users", ["GET"], get_users, name="get_users")
    post_route = Route("/users", ["POST"], create_user, name="create_user")
    
    router.add_route(get_route)
    router.add_route(post_route)
    
    # Verify routes are registered
    routes = router.get_routes()
    assert len(routes) == 2
    
    # Check route properties
    assert routes[0].path == "/users"
    assert routes[0].methods == ["GET"]
    assert routes[0].name == "get_users"
    
    assert routes[1].path == "/users"
    assert routes[1].methods == ["POST"]
    assert routes[1].name == "create_user"


def test_nested_routers():
    """Test nested router functionality."""
    # Create main router
    main_router = APIRouter("/api")
    
    # Create sub-router
    v1_router = APIRouter("/v1")
    
    # Create another sub-router
    users_router = APIRouter("/users")
    
    # Add routes to users router
    users_router.add_route(Route("/", ["GET"], get_users, name="list_users"))
    users_router.add_route(Route("/", ["POST"], create_user, name="create_user"))
    users_router.add_route(Route("/{user_id}", ["PUT"], update_user, name="update_user"))
    users_router.add_route(Route("/{user_id}", ["DELETE"], delete_user, name="delete_user"))
    
    # Build hierarchy
    v1_router.include_router(users_router)
    main_router.include_router(v1_router)
    
    # Get all routes
    routes = main_router.get_routes()
    assert len(routes) == 4
    
    # Check that paths are correctly prefixed
    paths = [route.path for route in routes]
    assert "/api/v1/users" in paths
    assert "/api/v1/users/{user_id}" in paths
    
    # Check methods
    methods = []
    for route in routes:
        methods.extend(route.methods)
    
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_auto_method_inference():
    """Test automatic HTTP method inference."""
    # Test name-based inference
    assert infer_http_methods(get_users) == ["GET"]
    assert infer_http_methods(create_user) == ["POST"]
    assert infer_http_methods(update_user) == ["PUT"]
    assert infer_http_methods(delete_user) == ["DELETE"]
    
    # Test explicit methods override
    assert infer_http_methods(get_users, ["POST"]) == ["POST"]
    
    # Test function with body parameter
    def save_data(data):
        pass
    
    assert infer_http_methods(save_data) == ["POST"]
    
    # Test unknown function name
    def unknown_function():
        pass
    
    assert infer_http_methods(unknown_function) == ["GET"]


def test_path_parameters():
    """Test path parameter parsing and conversion."""
    # Test parsing path templates
    processed_path, param_types = parse_path_template("/users/{user_id:int}")
    assert processed_path == "/users/{user_id}"
    assert param_types["user_id"] == int
    
    # Test multiple parameters
    processed_path, param_types = parse_path_template("/users/{user_id:int}/posts/{post_id:str}")
    assert processed_path == "/users/{user_id}/posts/{post_id}"
    assert param_types["user_id"] == int
    assert param_types["post_id"] == str
    
    # Test UUID parameter
    processed_path, param_types = parse_path_template("/items/{item_id:uuid}")
    assert processed_path == "/items/{item_id}"
    assert param_types["item_id"] == uuid.UUID
    
    # Test parameter conversion
    param_values = {"user_id": "123", "name": "john"}
    param_types = {"user_id": int, "name": str}
    
    converted = convert_path_params(param_values, param_types)
    assert converted["user_id"] == 123
    assert converted["name"] == "john"
    
    # Test UUID conversion
    test_uuid = uuid.uuid4()
    param_values = {"item_id": str(test_uuid)}
    param_types = {"item_id": uuid.UUID}
    
    converted = convert_path_params(param_values, param_types)
    assert isinstance(converted["item_id"], uuid.UUID)
    assert converted["item_id"] == test_uuid


def test_decorator_integration():
    """Test integration of all decorators."""
    # Test @get decorator
    @get("/users")
    def decorated_get_users():
        return {"users": ["Alice", "Bob"]}
    
    assert decorated_get_users._route.methods == ["GET"]
    
    # Test @post decorator
    @post("/users")
    def decorated_create_user():
        return {"message": "User created"}
    
    assert decorated_create_user._route.methods == ["POST"]
    
    # Test @route decorator with method inference
    @route("/users/{user_id}")
    def get_user(user_id: str):
        return {"user_id": user_id}
    
    assert get_user._route.methods == ["GET"]
    
    # Test @route decorator with explicit methods
    @route("/users", methods=["PUT"])
    def decorated_update_users():
        return {"message": "Users updated"}
    
    assert decorated_update_users._route.methods == ["PUT"]


def test_autodiscovery_integration():
    """Test autodiscovery integration."""
    import os
    
    # Test autodiscovery with our example endpoints
    endpoints_path = os.path.join(os.path.dirname(__file__), "..", "examples", "demo", "endpoints")
    
    # Make sure the path exists
    if os.path.exists(endpoints_path):
        router = discover_endpoints(endpoints_path)
        
        # Should find some routes
        routes = router.get_routes()
        assert len(routes) > 0
        
        # Check that we have routes with different methods
        methods = set()
        for route in routes:
            methods.update(route.methods)
            
        assert "GET" in methods
        assert "POST" in methods


def test_router_utilities():
    """Test router utility methods."""
    router = APIRouter()
    
    # Add some routes
    router.add_route(Route("/users", ["GET"], get_users))
    router.add_route(Route("/users", ["POST"], create_user))
    router.add_route(Route("/posts", ["GET"], example_handler))
    
    # Test route count
    assert router.route_count() == 3
    
    # Test empty router
    empty_router = APIRouter()
    assert empty_router.route_count() == 0
    assert len(empty_router.get_routes()) == 0


def test_route_properties():
    """Test route property helpers."""
    # Route with dependencies
    route_with_deps = Route(
        "/users", 
        ["GET"], 
        get_users, 
        dependencies=["auth", "db"]
    )
    
    assert route_with_deps.has_dependencies is True
    
    # Route without dependencies
    route_without_deps = Route("/users", ["GET"], get_users)
    assert route_without_deps.has_dependencies is False
    
    # Route with responses
    route_with_responses = Route(
        "/users", 
        ["GET"], 
        get_users, 
        responses={200: {"description": "Success"}}
    )
    
    assert route_with_responses.has_responses is True
    
    # Route without responses
    route_without_responses = Route("/users", ["GET"], get_users)
    assert route_without_responses.has_responses is False


def test_openapi_metadata_integration():
    """Test OpenAPI metadata integration."""
    @get(
        "/users",
        summary="List users",
        description="Get a list of all users",
        tags=["users", "read"],
        openapi_responses={200: {"description": "Success"}}
    )
    def users_with_openapi():
        return {"users": []}
    
    route = users_with_openapi._route
    assert route.has_openapi is True
    assert route.openapi.summary == "List users"
    assert route.openapi.description == "Get a list of all users"
    assert "users" in route.openapi.tags
    assert "read" in route.openapi.tags
    assert 200 in route.openapi.responses


if __name__ == "__main__":
    pytest.main([__file__])