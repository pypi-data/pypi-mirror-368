import uuid
import pytest
from pacificpy.routing.params import PathParamParser, parse_path_template, convert_path_params


def test_parse_path_template_basic():
    """Test parsing basic path templates without type annotations."""
    parser = PathParamParser()
    
    # Test simple path parameter
    path = "/users/{user_id}"
    processed_path, param_types = parser.parse_path_template(path)
    
    assert processed_path == "/users/{user_id}"
    assert param_types == {"user_id": str}


def test_parse_path_template_with_types():
    """Test parsing path templates with type annotations."""
    parser = PathParamParser()
    
    # Test path with int parameter
    path = "/users/{user_id:int}"
    processed_path, param_types = parser.parse_path_template(path)
    
    assert processed_path == "/users/{user_id}"
    assert param_types == {"user_id": int}
    
    # Test path with multiple typed parameters
    path = "/users/{user_id:int}/posts/{post_id:str}"
    processed_path, param_types = parser.parse_path_template(path)
    
    assert processed_path == "/users/{user_id}/posts/{post_id}"
    assert param_types == {"user_id": int, "post_id": str}


def test_parse_path_template_uuid():
    """Test parsing path templates with UUID parameters."""
    parser = PathParamParser()
    
    path = "/items/{item_id:uuid}"
    processed_path, param_types = parser.parse_path_template(path)
    
    assert processed_path == "/items/{item_id}"
    assert param_types == {"item_id": uuid.UUID}


def test_parse_path_template_unknown_type():
    """Test parsing path templates with unknown types (should default to str)."""
    parser = PathParamParser()
    
    path = "/items/{item_id:unknown}"
    processed_path, param_types = parser.parse_path_template(path)
    
    assert processed_path == "/items/{item_id}"
    assert param_types == {"item_id": str}


def test_convert_path_params_basic():
    """Test converting path parameters to their specified types."""
    param_values = {
        "user_id": "123",
        "name": "john",
        "active": "true"
    }
    
    param_types = {
        "user_id": int,
        "name": str,
        "active": bool
    }
    
    converted = convert_path_params(param_values, param_types)
    
    assert converted == {
        "user_id": 123,
        "name": "john",
        "active": True
    }


def test_convert_path_params_uuid():
    """Test converting UUID path parameters."""
    test_uuid = uuid.uuid4()
    
    param_values = {
        "item_id": str(test_uuid)
    }
    
    param_types = {
        "item_id": uuid.UUID
    }
    
    converted = convert_path_params(param_values, param_types)
    
    assert isinstance(converted["item_id"], uuid.UUID)
    assert converted["item_id"] == test_uuid


def test_convert_path_params_float():
    """Test converting float path parameters."""
    param_values = {
        "price": "123.45"
    }
    
    param_types = {
        "price": float
    }
    
    converted = convert_path_params(param_values, param_types)
    
    assert converted == {"price": 123.45}


def test_convert_path_params_boolean():
    """Test converting boolean path parameters."""
    param_values = {
        "flag1": "true",
        "flag2": "false",
        "flag3": "1",
        "flag4": "0"
    }
    
    param_types = {
        "flag1": bool,
        "flag2": bool,
        "flag3": bool,
        "flag4": bool
    }
    
    converted = convert_path_params(param_values, param_types)
    
    assert converted == {
        "flag1": True,
        "flag2": False,
        "flag3": True,
        "flag4": False
    }


def test_convert_path_params_invalid_int():
    """Test handling of invalid integer conversion."""
    param_values = {"user_id": "not_a_number"}
    param_types = {"user_id": int}
    
    with pytest.raises(ValueError, match="Cannot convert"):
        convert_path_params(param_values, param_types)


def test_convert_path_params_invalid_uuid():
    """Test handling of invalid UUID conversion."""
    param_values = {"item_id": "not_a_uuid"}
    param_types = {"item_id": uuid.UUID}
    
    with pytest.raises(ValueError, match="Cannot convert"):
        convert_path_params(param_values, param_types)


def test_path_param_parser_convenience_functions():
    """Test the convenience functions."""
    # Test parse_path_template
    processed_path, param_types = parse_path_template("/users/{user_id:int}")
    assert processed_path == "/users/{user_id}"
    assert param_types == {"user_id": int}
    
    # Test convert_path_params
    converted = convert_path_params({"user_id": "123"}, {"user_id": int})
    assert converted == {"user_id": 123}


def test_path_param_parser_edge_cases():
    """Test edge cases."""
    parser = PathParamParser()
    
    # Test empty path
    processed_path, param_types = parser.parse_path_template("")
    assert processed_path == ""
    assert param_types == {}
    
    # Test path without parameters
    processed_path, param_types = parser.parse_path_template("/users")
    assert processed_path == "/users"
    assert param_types == {}
    
    # Test multiple parameters of same type
    path = "/users/{user_id:int}/posts/{post_id:int}"
    processed_path, param_types = parser.parse_path_template(path)
    
    assert processed_path == "/users/{user_id}/posts/{post_id}"
    assert param_types == {"user_id": int, "post_id": int}