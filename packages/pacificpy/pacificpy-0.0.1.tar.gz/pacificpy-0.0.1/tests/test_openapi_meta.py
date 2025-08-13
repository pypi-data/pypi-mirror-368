import pytest
from pacificpy.routing import Route, get, post, OpenAPIMetadata, collect_openapi_metadata


def test_openapi_metadata_creation():
    """Test creating OpenAPIMetadata objects."""
    # Test with all parameters
    metadata = OpenAPIMetadata(
        summary="Get users",
        description="Retrieve a list of users",
        tags=["users", "read"],
        responses={
            200: {"description": "Successful response"},
            404: {"description": "User not found"}
        }
    )
    
    assert metadata.summary == "Get users"
    assert metadata.description == "Retrieve a list of users"
    assert metadata.tags == ["users", "read"]
    assert metadata.responses == {
        200: {"description": "Successful response"},
        404: {"description": "User not found"}
    }
    
    # Test conversion to dict
    metadata_dict = metadata.to_dict()
    assert "summary" in metadata_dict
    assert "description" in metadata_dict
    assert "tags" in metadata_dict
    assert "responses" in metadata_dict


def test_openapi_metadata_partial():
    """Test creating OpenAPIMetadata with partial information."""
    # Test with only summary
    metadata = OpenAPIMetadata(summary="Get users")
    assert metadata.summary == "Get users"
    assert metadata.description is None
    assert metadata.tags == []
    assert metadata.responses == {}
    
    # Test conversion to dict
    metadata_dict = metadata.to_dict()
    assert metadata_dict == {"summary": "Get users"}


def test_collect_openapi_metadata_from_function():
    """Test collecting OpenAPI metadata from a function."""
    @get(
        "/users",
        summary="List users",
        description="Get a list of all users",
        tags=["users"],
        openapi_responses={200: {"description": "List of users"}}
    )
    def get_users():
        """Get all users."""
        return {"users": []}
    
    route = get_users._route
    assert route.has_openapi is True
    assert route.openapi.summary == "List users"
    assert route.openapi.description == "Get a list of all users"
    assert route.openapi.tags == ["users"]
    assert route.openapi.responses == {200: {"description": "List of users"}}


def test_collect_openapi_metadata_from_docstring():
    """Test collecting OpenAPI metadata from function docstring."""
    @get("/users")
    def get_users():
        """Get all users.
        
        Retrieve a complete list of registered users.
        """
        return {"users": []}
    
    route = get_users._route
    assert route.has_openapi is True
    assert route.openapi.summary == "Get users"
    assert route.openapi.description == """Get all users.
        
        Retrieve a complete list of registered users.
        """


def test_collect_openapi_metadata_generated_summary():
    """Test that summary is generated from function name if not provided."""
    @get("/users")
    def get_all_users():
        return {"users": []}
    
    route = get_all_users._route
    assert route.openapi.summary == "Get all users"


def test_route_with_openapi_metadata():
    """Test creating a Route with OpenAPI metadata."""
    metadata = OpenAPIMetadata(
        summary="Test route",
        description="A test route for OpenAPI metadata",
        tags=["test"],
        responses={200: {"description": "Success"}}
    )
    
    def handler():
        return {"message": "test"}
    
    route = Route(
        path="/test",
        methods=["GET"],
        handler=handler,
        openapi=metadata
    )
    
    assert route.has_openapi is True
    assert route.openapi.summary == "Test route"
    assert route.openapi.description == "A test route for OpenAPI metadata"
    assert route.openapi.tags == ["test"]
    assert route.openapi.responses == {200: {"description": "Success"}}


def test_route_without_openapi_metadata():
    """Test creating a Route without OpenAPI metadata."""
    def handler():
        return {"message": "test"}
    
    route = Route(
        path="/test",
        methods=["GET"],
        handler=handler
    )
    
    assert route.has_openapi is False
    assert route.openapi is None


def test_collect_openapi_metadata_function_attributes():
    """Test collecting OpenAPI metadata from function attributes."""
    def handler():
        """Handler function."""
        return {"message": "test"}
    
    # Set function attributes
    handler.__openapi_summary__ = "Custom summary"
    handler.__openapi_tags__ = ["custom"]
    handler.__openapi_responses__ = {200: {"description": "Custom response"}}
    
    metadata = collect_openapi_metadata(handler)
    
    assert metadata.summary == "Custom summary"
    assert metadata.tags == ["custom"]
    assert metadata.responses == {200: {"description": "Custom response"}}


def test_openapi_metadata_merge():
    """Test merging OpenAPI metadata (placeholder test)."""
    # This would test the merge functionality if we had it exposed
    # For now, we'll just test that the module imports correctly
    from pacificpy.routing.meta import merge_openapi_metadata
    assert merge_openapi_metadata is not None