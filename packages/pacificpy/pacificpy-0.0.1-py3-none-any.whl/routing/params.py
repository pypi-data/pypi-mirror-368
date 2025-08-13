import re
import uuid
from typing import Any, Dict, Optional, Pattern, Tuple, Type, Union
from datetime import datetime


class PathParamParser:
    """
    Parser for path parameters with type conversion support.
    
    Supports parsing path parameters with type annotations like:
    - /users/{user_id:int}
    - /items/{item_id:uuid}
    - /posts/{post_id:str}
    """
    
    # Built-in type converters
    TYPE_CONVERTERS = {
        'int': int,
        'str': str,
        'float': float,
        'bool': lambda x: x.lower() in ('1', 'true', 'yes', 'on'),
        'uuid': uuid.UUID,
    }
    
    # Pattern to match path parameters with type annotations
    PARAM_PATTERN: Pattern = re.compile(r'\{([^}:]+)(?::([^}]+))?\}')
    
    def __init__(self) -> None:
        """Initialize the path parameter parser."""
        pass
    
    def parse_path_template(self, path: str) -> Tuple[str, Dict[str, Type]]:
        """
        Parse a path template and extract parameter names and types.
        
        Args:
            path: Path template with parameters like /users/{user_id:int}
            
        Returns:
            Tuple of (processed_path, param_types) where:
            - processed_path: Path with type annotations removed
            - param_types: Dictionary mapping parameter names to their types
        """
        param_types: Dict[str, Type] = {}
        
        def replace_param(match):
            param_name = match.group(1)
            param_type_str = match.group(2) or 'str'  # Default to str
            
            # Store the parameter type
            param_type = self._get_type_converter(param_type_str)
            param_types[param_name] = param_type
            
            # Return the parameter without type annotation for routing
            return f'{{{param_name}}}'
        
        # Replace parameters with type annotations
        processed_path = self.PARAM_PATTERN.sub(replace_param, path)
        
        return processed_path, param_types
    
    def _get_type_converter(self, type_str: str) -> Type:
        """
        Get the type converter for a type string.
        
        Args:
            type_str: String representation of type (int, str, uuid, etc.)
            
        Returns:
            Type converter function
        """
        # Handle built-in types
        if type_str in self.TYPE_CONVERTERS:
            return self.TYPE_CONVERTERS[type_str]
        
        # For unknown types, default to str
        return str
    
    def convert_path_params(self, param_values: Dict[str, str], param_types: Dict[str, Type]) -> Dict[str, Any]:
        """
        Convert path parameter values to their specified types.
        
        Args:
            param_values: Dictionary of parameter names to string values
            param_types: Dictionary of parameter names to their types
            
        Returns:
            Dictionary of parameter names to converted values
            
        Raises:
            ValueError: If a parameter value cannot be converted to its type
        """
        converted_params: Dict[str, Any] = {}
        
        for param_name, param_value in param_values.items():
            # Get the expected type
            param_type = param_types.get(param_name, str)
            
            # Convert the value
            try:
                converted_value = self._convert_value(param_value, param_type)
                converted_params[param_name] = converted_value
            except (ValueError, TypeError) as e:
                raise ValueError(f"Cannot convert parameter '{param_name}' with value '{param_value}' to type {param_type.__name__}: {e}")
        
        return converted_params
    
    def _convert_value(self, value: str, target_type: Type) -> Any:
        """
        Convert a string value to the target type.
        
        Args:
            value: String value to convert
            target_type: Target type to convert to
            
        Returns:
            Converted value
            
        Raises:
            ValueError: If conversion fails
        """
        # Handle None case
        if value is None:
            return None
            
        # Handle string type (no conversion needed)
        if target_type is str:
            return value
            
        # Handle boolean type
        if target_type is bool:
            return value.lower() in ('1', 'true', 'yes', 'on')
            
        # Handle UUID type
        if target_type is uuid.UUID:
            return uuid.UUID(value)
            
        # Handle numeric types
        try:
            return target_type(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot convert '{value}' to {target_type.__name__}: {e}")
    
    def get_path_regex(self, path: str) -> Tuple[Pattern, Dict[str, Type]]:
        """
        Generate a regex pattern for a path template and extract parameter types.
        
        Args:
            path: Path template with parameters
            
        Returns:
            Tuple of (regex_pattern, param_types)
        """
        # First parse the path to get parameter types
        processed_path, param_types = self.parse_path_template(path)
        
        # Convert the path to a regex pattern
        # Escape special regex characters except for our parameter placeholders
        escaped_path = re.escape(processed_path)
        
        # Replace parameter placeholders with regex capture groups
        # This is a simplified approach - in a real implementation, you might want
        # to use a more sophisticated pattern matching system
        regex_pattern = escaped_path.replace(r'\{', '(?P<').replace(r'\}', '>[^/]*)')
        
        # Compile the regex pattern
        pattern = re.compile(f'^{regex_pattern}$')
        
        return pattern, param_types


# Global instance for convenience
_default_parser = PathParamParser()


def parse_path_template(path: str) -> Tuple[str, Dict[str, Type]]:
    """
    Parse a path template and extract parameter names and types.
    
    Args:
        path: Path template with parameters like /users/{user_id:int}
        
    Returns:
        Tuple of (processed_path, param_types)
    """
    return _default_parser.parse_path_template(path)


def convert_path_params(param_values: Dict[str, str], param_types: Dict[str, Type]) -> Dict[str, Any]:
    """
    Convert path parameter values to their specified types.
    
    Args:
        param_values: Dictionary of parameter names to string values
        param_types: Dictionary of parameter names to their types
        
    Returns:
        Dictionary of parameter names to converted values
    """
    return _default_parser.convert_path_params(param_values, param_types)