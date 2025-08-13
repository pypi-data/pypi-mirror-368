from starlette.routing import Route, Router

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings
from pacificpy.core.http import Request, Response
from pacificpy.core.context import RequestContext


async def context_handler(request: Request) -> Response:
    """Handler that demonstrates using RequestContext."""
    # Get request from context
    context_request = RequestContext.get_request()
    
    # Get settings from context
    context_settings = RequestContext.get_settings()
    
    # Get trace_id from context
    trace_id = RequestContext.get_trace_id()
    
    # Get trace_id directly from request
    direct_trace_id = getattr(request.state, 'trace_id', None) if hasattr(request, 'state') else None
    
    # Verify that context request is the same as parameter
    requests_match = context_request is request
    
    # Check if context request has state and trace_id
    context_has_state = hasattr(context_request, 'state') if context_request else False
    context_trace_id = getattr(context_request.state, 'trace_id', None) if context_request and hasattr(context_request, 'state') else None
    
    return Response.json({
        "message": "Context test",
        "requests_match": requests_match,
        "trace_id": trace_id,
        "direct_trace_id": direct_trace_id,
        "context_has_state": context_has_state,
        "context_trace_id": context_trace_id,
        "settings_available": context_settings is not None
    })


if __name__ == "__main__":
    # Create router with test routes
    api_router = Router([
        Route("/context", context_handler, methods=["GET"]),
    ])
    
    # Create the PacificApp
    app = PacificApp()
    
    # Mount router
    app.mount_router(api_router)
    
    # Create settings
    settings = Settings.from_env()
    
    # Run the app with PacificPy server using settings
    run(
        app, 
        host=settings.host, 
        port=settings.port,
        use_uvloop=True,
        reload=settings.debug
    )