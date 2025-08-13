from datetime import datetime
from typing import Dict, Any
import time

from starlette.routing import Route, Router
from starlette.responses import JSONResponse

# Global variable to track application start time
_start_time = time.time()


async def ping_handler(request) -> JSONResponse:
    """
    Handle ping requests.
    
    Returns:
        JSON response with status "ok".
    """
    return JSONResponse({"status": "ok"})


async def health_handler(request) -> JSONResponse:
    """
    Handle health requests.
    
    Returns:
        JSON response with status, uptime, and trace_id.
    """
    # Calculate uptime
    uptime = time.time() - _start_time
    
    # Get trace_id from request state if available
    trace_id = getattr(request.state, 'trace_id', None) if hasattr(request, 'state') else None
    
    # Create health response
    health_data: Dict[str, Any] = {
        "status": "ok",
        "uptime": uptime,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add trace_id if available
    if trace_id:
        health_data["trace_id"] = trace_id
    
    return JSONResponse(health_data)


# Create router with health endpoints
health_router = Router([
    Route("/ping", ping_handler, methods=["GET"]),
    Route("/health", health_handler, methods=["GET"]),
])