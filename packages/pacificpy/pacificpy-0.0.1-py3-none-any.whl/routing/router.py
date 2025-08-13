from typing import Iterator, List, Optional, Union
from .route import Route


class APIRouter:
    """
    API Router for managing grouped routes with prefix support.
    
    Supports nested routers and prefix inheritance.
    """
    
    def __init__(self, prefix: Optional[str] = None) -> None:
        """
        Initialize an APIRouter.
        
        Args:
            prefix: Optional prefix for all routes in this router
        """
        if prefix is not None and not isinstance(prefix, str):
            raise TypeError("Prefix must be a string or None")
            
        if prefix is not None and not prefix.startswith("/"):
            raise ValueError("Prefix must start with '/'")
            
        # Normalize prefix - remove trailing slash if present
        if prefix is not None and prefix != "/" and prefix.endswith("/"):
            prefix = prefix.rstrip("/")
            
        self.prefix = prefix or ""
        self.routes: List[Route] = []
        self.sub_routers: List['APIRouter'] = []
    
    def add_route(self, route: Route) -> None:
        """
        Add a route to this router.
        
        Args:
            route: Route object to add
        """
        if not isinstance(route, Route):
            raise TypeError("route must be a Route instance")
            
        self.routes.append(route)
    
    def include_router(self, router: 'APIRouter') -> None:
        """
        Include another router in this router.
        
        Args:
            router: Another APIRouter instance to include
        """
        if not isinstance(router, APIRouter):
            raise TypeError("router must be an APIRouter instance")
            
        self.sub_routers.append(router)
    
    def iter_routes(self) -> Iterator[Route]:
        """
        Iterate through all routes in this router and sub-routers.
        
        Yields:
            Route objects with adjusted paths based on prefixes
        """
        # Yield routes from this router with adjusted paths
        for route in self.routes:
            # Create a new route with adjusted path
            adjusted_path = self._apply_prefix(route.path)
            if adjusted_path != route.path:
                # Create a new route with the adjusted path
                adjusted_route = Route(
                    path=adjusted_path,
                    methods=route.methods,
                    handler=route.handler,
                    name=route.name,
                    dependencies=route.dependencies,
                    responses=route.responses
                )
                yield adjusted_route
            else:
                yield route
        
        # Recursively yield routes from sub-routers
        for sub_router in self.sub_routers:
            for route in sub_router.iter_routes():
                # Apply both this router's prefix and the sub-router's prefix
                adjusted_path = self._apply_prefix(route.path)
                if adjusted_path != route.path:
                    # Create a new route with the adjusted path
                    adjusted_route = Route(
                        path=adjusted_path,
                        methods=route.methods,
                        handler=route.handler,
                        name=route.name,
                        dependencies=route.dependencies,
                        responses=route.responses
                    )
                    yield adjusted_route
                else:
                    yield route
    
    def _apply_prefix(self, path: str) -> str:
        """
        Apply the router's prefix to a path.
        
        Args:
            path: Path to apply prefix to
            
        Returns:
            Path with prefix applied
        """
        # If no prefix, return path as is
        if not self.prefix:
            return path
            
        # If path is root, use prefix only
        if path == "/":
            return self.prefix
            
        # Combine prefix and path
        if self.prefix.endswith("/"):
            return self.prefix + path.lstrip("/")
        else:
            return self.prefix + path
    
    def get_routes(self) -> List[Route]:
        """
        Get all routes in this router and sub-routers.
        
        Returns:
            List of all routes
        """
        return list(self.iter_routes())
    
    def route_count(self) -> int:
        """
        Get the total number of routes in this router and sub-routers.
        
        Returns:
            Total route count
        """
        count = len(self.routes)
        for sub_router in self.sub_routers:
            count += sub_router.route_count()
        return count