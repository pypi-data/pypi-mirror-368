from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from starlette.middleware import Middleware
from starlette.types import ASGIApp


class MiddlewareManager:
    """
    Manager for handling middleware with priorities and conditional inclusion.
    """
    
    def __init__(self) -> None:
        """Initialize the middleware manager."""
        self._middlewares: List[Tuple[int, Middleware]] = []
    
    def add_middleware(
        self, 
        middleware_class: Union[Type, Middleware],
        priority: int = 100,
        condition: Optional[Callable[[], bool]] = None,
        **kwargs: Any
    ) -> None:
        """
        Add middleware with priority and optional condition.
        
        Args:
            middleware_class: The middleware class or Middleware instance.
            priority: The priority of the middleware (lower numbers execute first).
            condition: Optional condition function that must return True to include middleware.
            **kwargs: Arguments to pass to the middleware constructor.
        """
        # Check condition if provided
        if condition is not None and not condition():
            return
        
        # Create Middleware instance if class is provided
        if isinstance(middleware_class, type):
            middleware = Middleware(middleware_class, **kwargs)
        else:
            middleware = middleware_class
        
        # Add middleware with priority
        self._middlewares.append((priority, middleware))
        
        # Sort middlewares by priority
        self._middlewares.sort(key=lambda x: x[0])
    
    def get_middlewares(self) -> List[Middleware]:
        """
        Get the list of middlewares sorted by priority.
        
        Returns:
            List of Middleware instances sorted by priority.
        """
        return [middleware for _, middleware in self._middlewares]
    
    def clear(self) -> None:
        """Clear all middlewares."""
        self._middlewares.clear()