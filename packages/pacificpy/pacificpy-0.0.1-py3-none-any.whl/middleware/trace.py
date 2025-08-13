from typing import Callable, Any
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse


class TraceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically initialize trace_id in request state.
    """
    
    async def dispatch(
        self, 
        request: StarletteRequest, 
        call_next: Callable[[StarletteRequest], Any]
    ) -> StarletteResponse:
        """
        Process the request and initialize trace_id in request state.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or endpoint handler.
            
        Returns:
            The response from the next middleware or endpoint handler.
        """
        # Initialize state if not present
        if not hasattr(request, 'state'):
            from starlette.datastructures import State
            request.state = State()
        
        # Initialize trace_id if not present
        if not hasattr(request.state, 'trace_id'):
            request.state.trace_id = str(uuid.uuid4())
        
        # Call the next middleware or endpoint handler
        response = await call_next(request)
        
        return response