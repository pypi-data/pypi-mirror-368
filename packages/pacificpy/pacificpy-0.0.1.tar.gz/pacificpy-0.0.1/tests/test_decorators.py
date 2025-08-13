import pytest
from pacificpy.routing import Route, route
from pacificpy.routing.decorators import _infer_methods_from_name, get_registered_routes


def test_route_decorator_basic():
    """Test the @route decorator with basic parameters."""
    
    @route("/test", methods=["GET"])
    def example_handler():
        return "Hello World"
    
    # Check that the function still works
    assert example_handler() == "Hello World"
    
    # Check that the route was attached
    assert hasattr(example_handler, '_route')
    route_obj = example_handler._route
    assert isinstance(route_obj, Route)
    assert route_obj.path == "/test"
    assert route_obj.methods == ["GET"]
    # Note: The handler will be the wrapper function, not the original
    assert route_obj.name == "example_handler"


def test_route_decorator_with_name():
    """Test the @route decorator with a custom name."""
    
    @route("/test", methods=["GET"], name="custom_name")
    def example_handler():
        return "Hello World"
    
    route_obj = example_handler._route
    assert route_obj.name == "custom_name"


def test_route_decorator_method_inference():
    """Test the @route decorator with automatic method inference."""
    
    @route("/users")
    def get_users():
        return "Users"
    
    route_obj = get_users._route
    assert route_obj.methods == ["GET"]
    
    @route("/users")
    def post_users():
        return "Created"
    
    route_obj = post_users._route
    assert route_obj.methods == ["POST"]


def test_route_decorator_with_dependencies_and_responses():
    """Test the @route decorator with dependencies and responses."""
    dependencies = ["dep1", "dep2"]
    responses = {200: {"description": "Success"}}
    
    @route("/test", methods=["GET"], dependencies=dependencies, responses=responses)
    def example_handler():
        return "Hello World"
    
    route_obj = example_handler._route
    assert route_obj.dependencies == dependencies
    assert route_obj.responses == responses


def test_infer_methods_from_name():
    """Test the _infer_methods_from_name helper function."""
    assert _infer_methods_from_name("get_users") == ["GET"]
    assert _infer_methods_from_name("post_users") == ["POST"]
    assert _infer_methods_from_name("put_users") == ["PUT"]
    assert _infer_methods_from_name("delete_users") == ["DELETE"]
    assert _infer_methods_from_name("patch_users") == ["PATCH"]
    assert _infer_methods_from_name("head_users") == ["HEAD"]
    assert _infer_methods_from_name("options_users") == ["OPTIONS"]
    # Default case
    assert _infer_methods_from_name("regular_function") == ["GET"]


def test_route_decorator_preserves_function_metadata():
    """Test that the @route decorator preserves function metadata."""
    
    @route("/test", methods=["GET"])
    def documented_handler():
        """This is a test function."""
        return "Hello World"
    
    # Check that the docstring is preserved
    assert documented_handler.__doc__ == "This is a test function."
    
    # Check that the function name is preserved
    assert documented_handler.__name__ == "documented_handler"


def test_route_decorator_with_string_method():
    """Test the @route decorator with a single string method."""
    
    @route("/test", methods="POST")
    def example_handler():
        return "Hello World"
    
    route_obj = example_handler._route
    assert route_obj.methods == ["POST"]