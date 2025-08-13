"""
Dependency Injection: Handler binder
"""
import inspect
from typing import Callable, Any, Dict, Awaitable
from .resolver import DependencyResolver
from .cache import DependencyCache

class HandlerBinder:
    """
    Binds a handler function with its dependencies, path parameters, 
    query parameters, and body parameters.
    """
    
    def __init__(self, resolver: DependencyResolver):
        self.resolver = resolver
    
    async def bind_and_call(
        self, 
        handler: Callable,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Any,
        cache: DependencyCache,
        dependency_overrides: Dict[Callable, Callable] = None
    ) -> Any:
        """
        Bind a handler with all its parameters and call it.
        
        Args:
            handler: The handler function to call
            path_params: Dictionary of path parameters
            query_params: Dictionary of query parameters
            body: The request body
            cache: The per-request dependency cache
            dependency_overrides: Optional dependency overrides for testing
            
        Returns:
            The result of calling the handler
        """
        if dependency_overrides is None:
            dependency_overrides = {}
            
        # Get function signature
        sig = inspect.signature(handler)
        
        # Prepare all arguments
        kwargs = {}
        
        # Resolve dependencies
        dependencies = await self.resolver.resolve_dependencies(
            handler, cache, dependency_overrides
        )
        kwargs.update(dependencies)
        
        # Add path parameters
        for param_name, param in sig.parameters.items():
            if param_name in path_params:
                kwargs[param_name] = path_params[param_name]
        
        # Add query parameters
        for param_name, param in sig.parameters.items():
            if param_name in query_params:
                kwargs[param_name] = query_params[param_name]
        
        # Add body parameter (if any)
        for param_name, param in sig.parameters.items():
            # Check if this parameter should receive the body
            # This is a simplified approach - in a real implementation,
            # you might use a special marker or annotation
            if param_name == 'body' or (param.annotation is not inspect.Parameter.empty and 
                                       hasattr(param.annotation, '__name__') and
                                       param.annotation.__name__.lower() == 'body'):
                kwargs[param_name] = body
        
        # Call the handler with all resolved arguments
        if inspect.iscoroutinefunction(handler):
            return await handler(**kwargs)
        else:
            return handler(**kwargs)