from starlette.routing import Route, Router
from starlette.middleware import Middleware

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings
from pacificpy.core.http import Request, Response
from pacificpy.middleware.trace import TraceMiddleware


async def ping_handler(request: Request) -> Response:
    """Handle ping requests with trace_id."""
    return Response.json({
        "message": "pong"
    })


if __name__ == "__main__":
    # Create routers with routes
    api_router = Router([
        Route("/ping", ping_handler, methods=["GET"]),
    ])
    
    # Create the PacificApp
    app = PacificApp()
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