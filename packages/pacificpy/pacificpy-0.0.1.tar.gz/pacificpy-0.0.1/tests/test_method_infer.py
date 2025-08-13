import pytest
from pacificpy.routing.method_infer import infer_http_methods


# Test functions with different names
def get_users():
    """Get list of users."""
    pass


def post_users():
    """Create users with POST."""
    pass


def create_user():
    """Create a user."""
    pass


def update_user():
    """Update a user."""
    pass


def delete_user():
    """Delete a user."""
    pass


def patch_user():
    """Partially update a user."""
    pass


# Test functions with body parameters
def create_user_with_body(user_data):
    """Create a user with body parameter."""
    pass


def update_user_with_body(user_id: int, user_data):
    """Update a user with body parameter."""
    pass


def save_user_data(user_data):
    """Save user data - should be POST due to body parameter."""
    pass


def get_user_by_id(user_id: int):
    """Get user by ID - should be GET."""
    pass


def process_data(request):
    """Generic function with request parameter - should be GET."""
    pass


def test_infer_methods_explicit():
    """Test that explicit methods are returned as-is."""
    methods = infer_http_methods(get_users, ["POST", "PUT"])
    assert methods == ["POST", "PUT"]


def test_infer_methods_get_prefix():
    """Test inferring GET method from function name."""
    methods = infer_http_methods(get_users)
    assert methods == ["GET"]


def test_infer_methods_post_prefix():
    """Test inferring POST method from function name."""
    methods = infer_http_methods(post_users)
    assert methods == ["POST"]


def test_infer_methods_create_prefix():
    """Test inferring POST method from 'create_' prefix."""
    methods = infer_http_methods(create_user)
    assert methods == ["POST"]


def test_infer_methods_update_prefix():
    """Test inferring PUT method from 'update_' prefix."""
    methods = infer_http_methods(update_user)
    assert methods == ["PUT"]


def test_infer_methods_delete_prefix():
    """Test inferring DELETE method from function name."""
    methods = infer_http_methods(delete_user)
    assert methods == ["DELETE"]


def test_infer_methods_patch_prefix():
    """Test inferring PATCH method from function name."""
    methods = infer_http_methods(patch_user)
    assert methods == ["PATCH"]


def test_infer_methods_with_body_parameter():
    """Test inferring POST method from body parameter."""
    methods = infer_http_methods(create_user_with_body)
    assert methods == ["POST"]


def test_infer_methods_save_with_body_parameter():
    """Test inferring POST method from body parameter without special prefix."""
    methods = infer_http_methods(save_user_data)
    assert methods == ["POST"]


def test_infer_methods_update_with_body_parameter():
    """Test inferring PUT method from update_ prefix with body parameter."""
    methods = infer_http_methods(update_user_with_body)
    assert methods == ["PUT"]


def test_infer_methods_no_body_parameter():
    """Test that functions without body parameters default to GET."""
    methods = infer_http_methods(get_user_by_id)
    assert methods == ["GET"]
    
    methods = infer_http_methods(process_data)
    assert methods == ["GET"]


def test_infer_methods_default():
    """Test that unknown function names default to GET."""
    def unknown_function():
        pass
        
    methods = infer_http_methods(unknown_function)
    assert methods == ["GET"]