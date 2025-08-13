import pytest
from pacificpy.routing import Route, APIRouter


def example_handler():
    return "Hello World"


def test_api_router_creation():
    """Test creating an APIRouter with and without prefix."""
    # Test without prefix
    router = APIRouter()
    assert router.prefix == ""
    assert router.routes == []
    assert router.sub_routers == []
    
    # Test with prefix
    router = APIRouter("/api")
    assert router.prefix == "/api"
    
    # Test with root prefix
    router = APIRouter("/")
    assert router.prefix == "/"


def test_api_router_add_route():
    """Test adding routes to an APIRouter."""
    router = APIRouter()
    route = Route("/test", ["GET"], example_handler)
    
    router.add_route(route)
    assert len(router.routes) == 1
    assert router.routes[0] == route


def test_api_router_add_route_validation():
    """Test that add_route validates input."""
    router = APIRouter()
    
    with pytest.raises(TypeError, match="route must be a Route instance"):
        router.add_route("not a route")


def test_api_router_include_router():
    """Test including another router."""
    router1 = APIRouter()
    router2 = APIRouter("/api")
    
    router1.include_router(router2)
    assert len(router1.sub_routers) == 1
    assert router1.sub_routers[0] == router2


def test_api_router_include_router_validation():
    """Test that include_router validates input."""
    router = APIRouter()
    
    with pytest.raises(TypeError, match="router must be an APIRouter instance"):
        router.include_router("not a router")


def test_api_router_iter_routes():
    """Test iterating through routes."""
    router = APIRouter()
    
    # Add some routes
    route1 = Route("/test1", ["GET"], example_handler)
    route2 = Route("/test2", ["POST"], example_handler)
    
    router.add_route(route1)
    router.add_route(route2)
    
    routes = list(router.iter_routes())
    assert len(routes) == 2
    assert routes[0].path == "/test1"
    assert routes[1].path == "/test2"


def test_api_router_nested_prefixes():
    """Test nested router prefixes."""
    # Create main router with prefix
    main_router = APIRouter("/api")
    
    # Create sub-router with its own prefix
    sub_router = APIRouter("/v1")
    
    # Add a route to the sub-router
    route = Route("/users", ["GET"], example_handler)
    sub_router.add_route(route)
    
    # Include sub-router in main router
    main_router.include_router(sub_router)
    
    # Get all routes - should have the combined prefix
    routes = list(main_router.iter_routes())
    assert len(routes) == 1
    assert routes[0].path == "/api/v1/users"


def test_api_router_complex_nesting():
    """Test complex nested router structure."""
    # Main router
    main_router = APIRouter("/api")
    
    # First level sub-router
    v1_router = APIRouter("/v1")
    
    # Second level sub-router
    users_router = APIRouter("/users")
    
    # Add routes at different levels
    main_route = Route("/status", ["GET"], example_handler)
    v1_route = Route("/info", ["GET"], example_handler)
    users_route = Route("/", ["GET"], example_handler)
    user_detail_route = Route("/{id}", ["GET"], example_handler)
    
    main_router.add_route(main_route)
    v1_router.add_route(v1_route)
    users_router.add_route(users_route)
    users_router.add_route(user_detail_route)
    
    # Build the hierarchy
    v1_router.include_router(users_router)
    main_router.include_router(v1_router)
    
    # Get all routes
    routes = list(main_router.iter_routes())
    assert len(routes) == 4
    
    # Check paths are correctly prefixed
    paths = [route.path for route in routes]
    assert "/api/status" in paths
    assert "/api/v1/info" in paths
    assert "/api/v1/users" in paths  # Fixed: removed trailing slash
    assert "/api/v1/users/{id}" in paths


def test_api_router_get_routes():
    """Test the get_routes method."""
    router = APIRouter()
    
    route1 = Route("/test1", ["GET"], example_handler)
    route2 = Route("/test2", ["POST"], example_handler)
    
    router.add_route(route1)
    router.add_route(route2)
    
    routes = router.get_routes()
    assert len(routes) == 2
    assert routes[0].path == "/test1"
    assert routes[1].path == "/test2"


def test_api_router_route_count():
    """Test the route_count method."""
    main_router = APIRouter()
    sub_router = APIRouter("/api")
    
    # Add routes to main router
    main_router.add_route(Route("/test1", ["GET"], example_handler))
    main_router.add_route(Route("/test2", ["POST"], example_handler))
    
    # Add routes to sub-router
    sub_router.add_route(Route("/users", ["GET"], example_handler))
    sub_router.add_route(Route("/posts", ["GET"], example_handler))
    sub_router.add_route(Route("/posts", ["POST"], example_handler))
    
    # Include sub-router
    main_router.include_router(sub_router)
    
    # Check counts
    assert main_router.route_count() == 5
    assert sub_router.route_count() == 3


def test_api_router_prefix_validation():
    """Test prefix validation."""
    with pytest.raises(ValueError, match="Prefix must start with '/'"):
        APIRouter("api")  # Missing leading slash
    
    with pytest.raises(TypeError, match="Prefix must be a string or None"):
        APIRouter(123)  # Not a string


def test_api_router_prefix_normalization():
    """Test that prefixes are normalized."""
    # Trailing slash should be removed
    router = APIRouter("/api/")
    assert router.prefix == "/api"
    
    # Root path should remain as is
    router = APIRouter("/")
    assert router.prefix == "/"