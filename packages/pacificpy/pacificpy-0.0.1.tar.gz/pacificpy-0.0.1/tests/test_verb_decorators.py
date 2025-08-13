import pytest
from pacificpy.routing import Route, get, post, put, delete, patch


def test_get_decorator():
    """Test the @get decorator."""
    
    @get("/users")
    def get_users():
        return {"users": ["Alice", "Bob"]}
    
    # Check that the function still works
    assert get_users() == {"users": ["Alice", "Bob"]}
    
    # Check that the route was attached
    assert hasattr(get_users, '_route')
    route = get_users._route
    assert isinstance(route, Route)
    assert route.path == "/users"
    assert route.methods == ["GET"]
    assert route.handler == get_users._route.handler
    assert route.name == "get_users"


def test_post_decorator():
    """Test the @post decorator."""
    
    @post("/users")
    def create_user():
        return {"message": "User created"}
    
    route = create_user._route
    assert route.path == "/users"
    assert route.methods == ["POST"]
    assert route.name == "create_user"


def test_put_decorator():
    """Test the @put decorator."""
    
    @put("/users/{user_id}")
    def update_user(user_id: str):
        return {"message": f"User {user_id} updated"}
    
    route = update_user._route
    assert route.path == "/users/{user_id}"
    assert route.methods == ["PUT"]
    assert route.name == "update_user"


def test_delete_decorator():
    """Test the @delete decorator."""
    
    @delete("/users/{user_id}")
    def delete_user(user_id: str):
        return {"message": f"User {user_id} deleted"}
    
    route = delete_user._route
    assert route.path == "/users/{user_id}"
    assert route.methods == ["DELETE"]
    assert route.name == "delete_user"


def test_patch_decorator():
    """Test the @patch decorator."""
    
    @patch("/users/{user_id}")
    def partial_update_user(user_id: str):
        return {"message": f"User {user_id} partially updated"}
    
    route = partial_update_user._route
    assert route.path == "/users/{user_id}"
    assert route.methods == ["PATCH"]
    assert route.name == "partial_update_user"


def test_decorator_with_options():
    """Test decorators with additional options."""
    
    @post("/users", name="create_user_endpoint", dependencies=["auth"])
    def create_user():
        return {"message": "User created"}
    
    route = create_user._route
    assert route.path == "/users"
    assert route.methods == ["POST"]
    assert route.name == "create_user_endpoint"
    assert route.dependencies == ["auth"]


def test_decorator_preserves_function_metadata():
    """Test that decorators preserve function metadata."""
    
    @get("/users")
    def documented_handler():
        """This is a documented handler."""
        return {"users": []}
    
    # Check that the docstring is preserved
    assert documented_handler.__doc__ == "This is a documented handler."
    
    # Check that the function name is preserved
    assert documented_handler.__name__ == "documented_handler"
    
    # Check that the route name matches the function name
    assert documented_handler._route.name == "documented_handler"