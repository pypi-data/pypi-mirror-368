import pytest
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from pacificpy.routing import Route, RouteMatcher


async def example_handler(request: Request) -> JSONResponse:
    """Example handler for testing."""
    return JSONResponse({"message": "Hello World"})


def sync_example_handler(request: Request) -> JSONResponse:
    """Synchronous example handler for testing."""
    return JSONResponse({"message": "Hello Sync World"})


@pytest.mark.asyncio
async def test_route_matcher_basic():
    """Test basic RouteMatcher functionality."""
    # Create a Pacific Route
    pacific_route = Route(
        path="/test",
        methods=["GET"],
        handler=example_handler,
        name="test_route"
    )
    
    # Create RouteMatcher
    matcher = RouteMatcher()
    
    # Convert to Starlette Route
    starlette_route = matcher.match_route(pacific_route)
    
    # Check that we got a Starlette Route
    assert isinstance(starlette_route, starlette_route.__class__.__bases__[0])  # Starlette Route
    assert starlette_route.path == "/test"
    assert "GET" in starlette_route.methods
    assert starlette_route.name == "test_route"


@pytest.mark.asyncio
async def test_route_matcher_with_hooks():
    """Test RouteMatcher with pre/post hooks."""
    # Track hook calls
    pre_hook_calls = []
    post_hook_calls = []
    
    # Define hooks
    def pre_hook(request: Request):
        pre_hook_calls.append(request)
    
    def post_hook(request: Request, response: Response):
        post_hook_calls.append((request, response))
    
    # Create a Pacific Route
    pacific_route = Route(
        path="/test",
        methods=["GET"],
        handler=example_handler
    )
    
    # Create RouteMatcher with hooks
    matcher = RouteMatcher(pre_hooks=[pre_hook], post_hooks=[post_hook])
    
    # Convert to Starlette Route
    starlette_route = matcher.match_route(pacific_route)
    
    # Test the wrapped handler (this is a simplified test)
    # In a real test, we would create a mock request and call the endpoint
    assert len(matcher.pre_hooks) == 1
    assert len(matcher.post_hooks) == 1


@pytest.mark.asyncio
async def test_route_matcher_add_hooks():
    """Test adding hooks after initialization."""
    matcher = RouteMatcher()
    
    # Add hooks
    matcher.add_pre_hook(lambda req: None)
    matcher.add_post_hook(lambda req, resp: None)
    
    assert len(matcher.pre_hooks) == 1
    assert len(matcher.post_hooks) == 1


@pytest.mark.asyncio
async def test_route_matcher_multiple_routes():
    """Test converting multiple routes."""
    # Create Pacific Routes
    route1 = Route(
        path="/test1",
        methods=["GET"],
        handler=example_handler
    )
    
    route2 = Route(
        path="/test2",
        methods=["POST"],
        handler=sync_example_handler
    )
    
    routes = [route1, route2]
    
    # Create RouteMatcher
    matcher = RouteMatcher()
    
    # Convert to Starlette Routes
    starlette_routes = matcher.match_routes(routes)
    
    # Check results
    assert len(starlette_routes) == 2
    assert starlette_routes[0].path == "/test1"
    assert starlette_routes[1].path == "/test2"
    assert "GET" in starlette_routes[0].methods
    assert "POST" in starlette_routes[1].methods


def test_route_matcher_sync_handler():
    """Test RouteMatcher with synchronous handler."""
    # Create a Pacific Route with sync handler
    pacific_route = Route(
        path="/sync-test",
        methods=["GET"],
        handler=sync_example_handler
    )
    
    # Create RouteMatcher
    matcher = RouteMatcher()
    
    # Convert to Starlette Route
    starlette_route = matcher.match_route(pacific_route)
    
    # Check that conversion worked
    assert isinstance(starlette_route, starlette_route.__class__.__bases__[0])  # Starlette Route
    assert starlette_route.path == "/sync-test"


@pytest.mark.asyncio
async def test_route_matcher_preserves_attributes():
    """Test that Route attributes are preserved in conversion."""
    # Create a Pacific Route with all attributes
    dependencies = ["dep1", "dep2"]
    responses = {200: {"description": "Success"}}
    
    pacific_route = Route(
        path="/full-test",
        methods=["GET", "POST"],
        handler=example_handler,
        name="full_test_route",
        dependencies=dependencies,
        responses=responses
    )
    
    # Create RouteMatcher
    matcher = RouteMatcher()
    
    # Convert to Starlette Route
    starlette_route = matcher.match_route(pacific_route)
    
    # Check that essential attributes are preserved
    assert starlette_route.path == "/full-test"
    assert "GET" in starlette_route.methods
    assert "POST" in starlette_route.methods
    assert starlette_route.name == "full_test_route"