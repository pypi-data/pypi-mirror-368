from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps
import inspect

from .route import Route
from .meta import collect_openapi_metadata, OpenAPIMetadata


def route(
    path: str,
    methods: Optional[Union[List[str], str]] = None,
    name: Optional[str] = None,
    dependencies: Optional[List[Any]] = None,
    responses: Optional[Dict[int, Dict[str, Any]]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    openapi_responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
):
    """
    Decorator that converts a function into a Route.
    
    Automatically extracts HTTP methods from function name if not specified:
    - Functions starting with 'get_' -> GET
    - Functions starting with 'post_' -> POST
    - Functions starting with 'put_' -> PUT
    - Functions starting with 'delete_' -> DELETE
    - Functions starting with 'patch_' -> PATCH
    
    Args:
        path: The URL path for this route
        methods: HTTP methods this route accepts. If not provided, 
                 will be inferred from function name.
        name: Optional name for the route
        dependencies: Optional list of dependencies for this route
        responses: Optional dictionary of response definitions
        summary: Short summary of what the route does
        description: Detailed description of the route
        tags: Tags for grouping operations
        openapi_responses: OpenAPI response definitions
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Determine methods if not provided
        if methods is None:
            func_methods = _infer_methods_from_name(func.__name__)
        else:
            func_methods = methods
            
        # Collect OpenAPI metadata
        openapi_metadata = collect_openapi_metadata(
            func,
            summary=summary,
            description=description,
            tags=tags,
            responses=openapi_responses
        )
            
        # Create the route
        route_obj = Route(
            path=path,
            methods=func_methods,
            handler=func,
            name=name or func.__name__,
            dependencies=dependencies,
            responses=responses,
            openapi=openapi_metadata
        )
        
        # Attach the route to the function as an attribute
        func._route = route_obj
        
        # Preserve function metadata
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Also attach the route to the wrapper
        wrapper._route = route_obj
        
        return wrapper
    return decorator


def get(
    path: str,
    name: Optional[str] = None,
    dependencies: Optional[List[Any]] = None,
    responses: Optional[Dict[int, Dict[str, Any]]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    openapi_responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
):
    """
    Decorator for GET routes.
    
    Syntactic sugar for @route(path, methods=["GET"]).
    
    Args:
        path: The URL path for this route
        name: Optional name for the route
        dependencies: Optional list of dependencies for this route
        responses: Optional dictionary of response definitions
        summary: Short summary of what the route does
        description: Detailed description of the route
        tags: Tags for grouping operations
        openapi_responses: OpenAPI response definitions
    """
    return route(
        path=path,
        methods=["GET"],
        name=name,
        dependencies=dependencies,
        responses=responses,
        summary=summary,
        description=description,
        tags=tags,
        openapi_responses=openapi_responses
    )


def post(
    path: str,
    name: Optional[str] = None,
    dependencies: Optional[List[Any]] = None,
    responses: Optional[Dict[int, Dict[str, Any]]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    openapi_responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
):
    """
    Decorator for POST routes.
    
    Syntactic sugar for @route(path, methods=["POST"]).
    
    Args:
        path: The URL path for this route
        name: Optional name for the route
        dependencies: Optional list of dependencies for this route
        responses: Optional dictionary of response definitions
        summary: Short summary of what the route does
        description: Detailed description of the route
        tags: Tags for grouping operations
        openapi_responses: OpenAPI response definitions
    """
    return route(
        path=path,
        methods=["POST"],
        name=name,
        dependencies=dependencies,
        responses=responses,
        summary=summary,
        description=description,
        tags=tags,
        openapi_responses=openapi_responses
    )


def put(
    path: str,
    name: Optional[str] = None,
    dependencies: Optional[List[Any]] = None,
    responses: Optional[Dict[int, Dict[str, Any]]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    openapi_responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
):
    """
    Decorator for PUT routes.
    
    Syntactic sugar for @route(path, methods=["PUT"]).
    
    Args:
        path: The URL path for this route
        name: Optional name for the route
        dependencies: Optional list of dependencies for this route
        responses: Optional dictionary of response definitions
        summary: Short summary of what the route does
        description: Detailed description of the route
        tags: Tags for grouping operations
        openapi_responses: OpenAPI response definitions
    """
    return route(
        path=path,
        methods=["PUT"],
        name=name,
        dependencies=dependencies,
        responses=responses,
        summary=summary,
        description=description,
        tags=tags,
        openapi_responses=openapi_responses
    )


def delete(
    path: str,
    name: Optional[str] = None,
    dependencies: Optional[List[Any]] = None,
    responses: Optional[Dict[int, Dict[str, Any]]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    openapi_responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
):
    """
    Decorator for DELETE routes.
    
    Syntactic sugar for @route(path, methods=["DELETE"]).
    
    Args:
        path: The URL path for this route
        name: Optional name for the route
        dependencies: Optional list of dependencies for this route
        responses: Optional dictionary of response definitions
        summary: Short summary of what the route does
        description: Detailed description of the route
        tags: Tags for grouping operations
        openapi_responses: OpenAPI response definitions
    """
    return route(
        path=path,
        methods=["DELETE"],
        name=name,
        dependencies=dependencies,
        responses=responses,
        summary=summary,
        description=description,
        tags=tags,
        openapi_responses=openapi_responses
    )


def patch(
    path: str,
    name: Optional[str] = None,
    dependencies: Optional[List[Any]] = None,
    responses: Optional[Dict[int, Dict[str, Any]]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    openapi_responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
):
    """
    Decorator for PATCH routes.
    
    Syntactic sugar for @route(path, methods=["PATCH"]).
    
    Args:
        path: The URL path for this route
        name: Optional name for the route
        dependencies: Optional list of dependencies for this route
        responses: Optional dictionary of response definitions
        summary: Short summary of what the route does
        description: Detailed description of the route
        tags: Tags for grouping operations
        openapi_responses: OpenAPI response definitions
    """
    return route(
        path=path,
        methods=["PATCH"],
        name=name,
        dependencies=dependencies,
        responses=responses,
        summary=summary,
        description=description,
        tags=tags,
        openapi_responses=openapi_responses
    )


def _infer_methods_from_name(func_name: str) -> List[str]:
    """
    Infer HTTP methods from function name prefix.
    
    Args:
        func_name: Name of the function
        
    Returns:
        List of HTTP methods
    """
    method_map = {
        'get_': 'GET',
        'post_': 'POST',
        'put_': 'PUT',
        'delete_': 'DELETE',
        'patch_': 'PATCH',
        'head_': 'HEAD',
        'options_': 'OPTIONS'
    }
    
    for prefix, method in method_map.items():
        if func_name.startswith(prefix):
            return [method]
    
    # Default to GET if no prefix matches
    return ['GET']


# Registry for routes - this would be used by the router
_route_registry = []


def register_route(route: Route) -> None:
    """
    Register a route in the global registry.
    
    Args:
        route: Route object to register
    """
    _route_registry.append(route)


def get_registered_routes() -> List[Route]:
    """
    Get all registered routes.
    
    Returns:
        List of registered routes
    """
    return _route_registry.copy()