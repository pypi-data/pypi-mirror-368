import traceback
from starlette.routing import Route, Router
from starlette.middleware import Middleware

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings
from pacificpy.core.http import Request, Response
from pacificpy.middleware.trace import TraceMiddleware


async def ping_handler(request: Request) -> Response:
    """Handle ping requests with trace_id."""
    try:
        # Access trace_id and user from request state
        trace_id = getattr(request.state, 'trace_id', None)
        user = getattr(request.state, 'user', None)
        
        return Response.json({
            "message": "pong",
            "trace_id": trace_id,
            "user": user
        })
    except Exception as e:
        print(f"Error in ping_handler: {e}")
        print(traceback.format_exc())
        return Response.json({
            "error": str(e)
        }, status_code=500)


async def echo_handler(request: Request) -> Response:
    """Handle echo requests."""
    try:
        # Access trace_id from request state
        trace_id = getattr(request.state, 'trace_id', None)
        
        # Get JSON data from request
        data = await request.json()
        
        # Return the same data with trace_id
        return Response.json({
            "echo": data,
            "trace_id": trace_id
        })
    except Exception as e:
        print(f"Error in echo_handler: {e}")
        print(traceback.format_exc())
        return Response.json({
            "error": str(e)
        }, status_code=500)


async def text_handler(request: Request) -> Response:
    """Handle text requests."""
    try:
        # Get text data from request
        body = await request.body()
        text = body.decode('utf-8')
        
        # Return a text response
        return Response.text(f"Received: {text}")
    except Exception as e:
        print(f"Error in text_handler: {e}")
        print(traceback.format_exc())
        return Response.json({
            "error": str(e)
        }, status_code=500)


if __name__ == "__main__":
    # Create routers with routes
    api_router = Router([
        Route("/ping", ping_handler, methods=["GET"]),
        Route("/echo", echo_handler, methods=["POST"]),
        Route("/text", text_handler, methods=["POST"]),
    ])
    
    # Create the PacificApp with trace middleware
    app = PacificApp()
    app.add_middleware(Middleware(TraceMiddleware))
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