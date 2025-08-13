from starlette.routing import Route, Router
from starlette.responses import JSONResponse

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings


def ping_handler(request):
    return JSONResponse({"message": "pong"})


if __name__ == "__main__":
    # Create a router with a ping route
    ping_router = Router([
        Route("/ping", ping_handler, methods=["GET"])
    ])
    
    # Create the PacificApp and mount the router
    app = PacificApp()
    app.mount_router(ping_router)
    
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