"""
Dependency Injection: OpenAPI integration
"""
from typing import Dict, Any, Callable, get_type_hints
import inspect
from .dependency import Depends

class OpenAPIDependencyInspector:
    """
    Inspects dependencies for OpenAPI documentation generation.
    """
    
    @staticmethod
    def get_dependencies_for_endpoint(handler: Callable) -> Dict[str, Dict[str, Any]]:
        """
        Extract dependency information for OpenAPI documentation.
        
        Args:
            handler: The endpoint handler function
            
        Returns:
            Dictionary of dependencies with their metadata
        """
        dependencies = {}
        
        try:
            type_hints = get_type_hints(handler)
        except (NameError, AttributeError):
            # Skip if we can't get type hints
            return dependencies
        
        sig = inspect.signature(handler)
        
        for param_name, param in sig.parameters.items():
            # Check if parameter is marked as a dependency
            dependency_info = None
            
            if isinstance(param.annotation, Depends):
                dependency_info = OpenAPIDependencyInspector._extract_dependency_info(
                    param.annotation, param_name, type_hints.get(param_name)
                )
            elif isinstance(param.default, Depends):
                dependency_info = OpenAPIDependencyInspector._extract_dependency_info(
                    param.default, param_name, type_hints.get(param_name)
                )
            
            if dependency_info:
                dependencies[param_name] = dependency_info
                
        return dependencies
    
    @staticmethod
    def _extract_dependency_info(depends: 'Depends', param_name: str, expected_type: Any) -> Dict[str, Any]:
        """
        Extract information about a dependency for documentation.
        
        Args:
            depends: The Depends object
            param_name: The parameter name
            expected_type: The expected type from type hints
            
        Returns:
            Dictionary with dependency information
        """
        dependency = depends.dependency
        callable_or_class = dependency.callable_or_class
        
        # Get dependency name
        dep_name = getattr(callable_or_class, '__name__', str(callable_or_class))
        
        # Determine if it affects input/output
        affects_input = False
        affects_output = False
        
        # Check if it's a Pydantic model (simplified check)
        if hasattr(expected_type, '__fields__'):
            affects_output = True
        
        # Check if it processes input data
        if hasattr(callable_or_class, '__annotations__'):
            try:
                callable_type_hints = get_type_hints(callable_or_class)
                # If any parameter is related to request data (query, body, path)
                for hint_name, hint_type in callable_type_hints.items():
                    if hint_name in ['query', 'body', 'path'] or 'Request' in str(hint_type):
                        affects_input = True
            except (NameError, AttributeError):
                pass
        
        return {
            'name': dep_name,
            'module': getattr(callable_or_class, '__module__', ''),
            'affects_input': affects_input,
            'affects_output': affects_output,
            'use_cache': dependency.use_cache,
            'type': str(expected_type) if expected_type else 'Unknown'
        }
    
    @staticmethod
    def add_dependency_schemas_to_openapi(openapi_schema: Dict[str, Any], handler: Callable) -> None:
        """
        Add dependency schemas to an OpenAPI schema.
        
        Args:
            openapi_schema: The OpenAPI schema to modify
            handler: The endpoint handler function
        """
        dependencies = OpenAPIDependencyInspector.get_dependencies_for_endpoint(handler)
        
        if not dependencies:
            return
        
        # Add dependencies to the schema
        if 'components' not in openapi_schema:
            openapi_schema['components'] = {'schemas': {}}
        elif 'schemas' not in openapi_schema['components']:
            openapi_schema['components']['schemas'] = {}
        
        for param_name, dep_info in dependencies.items():
            # Create a schema reference for the dependency
            schema_name = f"{dep_info['name']}Dependency"
            
            # Add to components schemas (simplified)
            openapi_schema['components']['schemas'][schema_name] = {
                'type': 'object',
                'properties': {
                    'dependency': {
                        'type': 'string',
                        'example': dep_info['name']
                    },
                    'module': {
                        'type': 'string',
                        'example': dep_info['module']
                    },
                    'cached': {
                        'type': 'boolean',
                        'example': dep_info['use_cache']
                    }
                }
            }
        
        # Add dependency information to the endpoint
        if 'x-dependencies' not in openapi_schema:
            openapi_schema['x-dependencies'] = dependencies