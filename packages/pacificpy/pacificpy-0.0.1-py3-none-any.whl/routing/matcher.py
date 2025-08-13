from typing import Any, Awaitable, Callable, List, Optional, Union
from functools import wraps

from starlette.routing import Route as StarletteRoute
from starlette.requests import Request
from starlette.responses import Response

from .route import Route


class RouteMatcher:
    """
    Adapter that converts Pacific Route objects to Starlette Route objects
    with pre/post hooks support for DI.
    """
    
    def __init__(
        self,
        pre_hooks: Optional[List[Callable[[Request], Union[None, Awaitable[None]]]]] = None,
        post_hooks: Optional[List[Callable[[Request, Response], Union[None, Awaitable[None]]]]] = None,
    ) -> None:
        """
        Initialize RouteMatcher with optional pre/post hooks.
        
        Args:
            pre_hooks: Optional list of pre-processing hooks
            post_hooks: Optional list of post-processing hooks
        """
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []
    
    def match_route(self, route: Route) -> StarletteRoute:
        """
        Convert a Pacific Route to a Starlette Route with hooks.
        
        Args:
            route: Pacific Route object
            
        Returns:
            Starlette Route object with hooks
        """
        # Create wrapped handler with hooks
        wrapped_handler = self._wrap_handler(route.handler)
        
        # Create Starlette Route
        starlette_route = StarletteRoute(
            path=route.path,
            endpoint=wrapped_handler,
            methods=route.methods,
            name=route.name
        )
        
        return starlette_route
    
    def _wrap_handler(self, handler: Callable[..., Any]) -> Callable[..., Any]:
        """
        Wrap a handler with pre/post hooks.
        
        Args:
            handler: Original handler function
            
        Returns:
            Wrapped handler with hooks
        """
        @wraps(handler)
        async def wrapped_handler(request: Request) -> Response:
            # Run pre-hooks
            for hook in self.pre_hooks:
                result = hook(request)
                if hasattr(result, '__await__'):
                    await result
            
            # Run the original handler
            response = handler(request)
            if hasattr(response, '__await__'):
                response = await response
            
            # Run post-hooks
            for hook in self.post_hooks:
                result = hook(request, response)
                if hasattr(result, '__await__'):
                    await result
            
            return response
        
        return wrapped_handler
    
    def add_pre_hook(self, hook: Callable[[Request], Union[None, Awaitable[None]]]) -> None:
        """
        Add a pre-processing hook.
        
        Args:
            hook: Pre-processing hook function
        """
        self.pre_hooks.append(hook)
    
    def add_post_hook(self, hook: Callable[[Request, Response], Union[None, Awaitable[None]]]) -> None:
        """
        Add a post-processing hook.
        
        Args:
            hook: Post-processing hook function
        """
        self.post_hooks.append(hook)
    
    def match_routes(self, routes: List[Route]) -> List[StarletteRoute]:
        """
        Convert multiple Pacific Routes to Starlette Routes.
        
        Args:
            routes: List of Pacific Route objects
            
        Returns:
            List of Starlette Route objects
        """
        return [self.match_route(route) for route in routes]