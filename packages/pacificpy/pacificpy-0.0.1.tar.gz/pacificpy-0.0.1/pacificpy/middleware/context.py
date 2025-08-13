from typing import Callable, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse


class ContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to manage request context.
    """
    
    def __init__(self, app, settings=None) -> None:
        """
        Initialize the context middleware.
        
        Args:
            app: The ASGI application.
            settings: The application settings.
        """
        super().__init__(app)
        self.settings = settings
    
    async def dispatch(
        self, 
        request: StarletteRequest, 
        call_next: Callable[[StarletteRequest], Any]
    ) -> StarletteResponse:
        """
        Process the request and manage context.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or endpoint handler.
            
        Returns:
            The response from the next middleware or endpoint handler.
        """
        # Import RequestContext here to avoid circular imports
        from ..core.context import RequestContext
        
        # Enter context with request and settings
        with RequestContext(request, self.settings):
            # Call the next middleware or endpoint handler
            response = await call_next(request)
        
        return response