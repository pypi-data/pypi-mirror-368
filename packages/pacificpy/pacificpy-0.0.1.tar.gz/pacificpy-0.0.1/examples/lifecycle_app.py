from starlette.routing import Route, Router
from starlette.responses import JSONResponse

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings


# Global variable to track startup
app_started = False


def ping_handler(request):
    return JSONResponse({"message": "pong", "app_started": app_started})


# Synchronous startup handler
def startup_handler():
    global app_started
    print("Application is starting up...")
    app_started = True


# Synchronous shutdown handler
def shutdown_handler():
    print("Application is shutting down...")


# Asynchronous startup handler
async def async_startup_handler():
    print("Async startup handler called")


# Asynchronous shutdown handler
async def async_shutdown_handler():
    print("Async shutdown handler called")


if __name__ == "__main__":
    # Create a router with a ping route
    ping_router = Router([
        Route("/ping", ping_handler, methods=["GET"])
    ])
    
    # Create the PacificApp and mount the router
    app = PacificApp()
    app.mount_router(ping_router)
    
    # Register lifecycle handlers
    app.on_startup(startup_handler)
    app.on_shutdown(shutdown_handler)
    app.on_startup(async_startup_handler)
    app.on_shutdown(async_shutdown_handler)
    
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