from typing import Any, Callable, Dict, List, Optional, Union

from .meta import OpenAPIMetadata


class Route:
    """
    Route class for endpoint metadata.
    
    Represents a single route with its metadata including path, methods,
    handler, name, dependencies and responses.
    """
    
    def __init__(
        self,
        path: str,
        methods: Union[List[str], str],
        handler: Callable[..., Any],
        name: Optional[str] = None,
        dependencies: Optional[List[Any]] = None,
        responses: Optional[Dict[int, Dict[str, Any]]] = None,
        openapi: Optional[OpenAPIMetadata] = None,
    ) -> None:
        """
        Initialize a Route instance.
        
        Args:
            path: The URL path for this route
            methods: HTTP methods this route accepts (GET, POST, etc.)
            handler: The function that handles requests to this route
            name: Optional name for the route
            dependencies: Optional list of dependencies for this route
            responses: Optional dictionary of response definitions
            openapi: Optional OpenAPI metadata
        """
        if not isinstance(path, str):
            raise TypeError("Path must be a string")
        
        if not path.startswith("/"):
            raise ValueError("Path must start with '/'")
            
        if not callable(handler):
            raise TypeError("Handler must be callable")
            
        if dependencies is None:
            dependencies = []
        elif not isinstance(dependencies, list):
            raise TypeError("Dependencies must be a list")
            
        if responses is None:
            responses = {}
        elif not isinstance(responses, dict):
            raise TypeError("Responses must be a dictionary")
            
        # Normalize methods to a list
        if isinstance(methods, str):
            methods = [methods]
        elif not isinstance(methods, list):
            raise TypeError("Methods must be a string or list of strings")
            
        # Validate methods
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        for method in methods:
            if not isinstance(method, str):
                raise TypeError("Each method must be a string")
            if method.upper() not in valid_methods:
                raise ValueError(f"Invalid HTTP method: {method}")
        
        self.path = path
        self.methods = [method.upper() for method in methods]
        self.handler = handler
        self.name = name
        self.dependencies = dependencies
        self.responses = responses
        self.openapi = openapi
    
    def __repr__(self) -> str:
        """Return a readable representation of the Route."""
        methods_str = ", ".join(self.methods)
        return (
            f"Route(path='{self.path}', methods=[{methods_str}], "
            f"handler={self.handler.__name__}, name={self.name!r})"
        )
    
    @property
    def has_dependencies(self) -> bool:
        """Check if the route has dependencies."""
        return bool(self.dependencies)
    
    @property
    def has_responses(self) -> bool:
        """Check if the route has response definitions."""
        return bool(self.responses)
    
    @property
    def has_openapi(self) -> bool:
        """Check if the route has OpenAPI metadata."""
        return self.openapi is not None