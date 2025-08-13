from starlette.routing import Route, Router

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings
from pacificpy.core.http import Request, Response


async def custom_handler(request: Request) -> Response:
    """Custom handler for testing."""
    return Response.json({
        "message": "Custom endpoint",
        "path": request.url.path
    })


if __name__ == "__main__":
    # Create router with custom route
    api_router = Router([
        Route("/custom", custom_handler, methods=["GET"]),
    ])
    
    # Create the PacificApp
    app = PacificApp()
    
    # Mount custom router
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