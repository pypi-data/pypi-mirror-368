from starlette.routing import Route, Router

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings
from pacificpy.core.http import Request, Response


async def handler_with_loaded_plugin(request: Request) -> Response:
    """Handler that demonstrates loading plugin from module."""
    # Get plugin manager from app (this would be available through context in real app)
    # For this example, we'll just return a simple response
    
    return Response.json({
        "message": "Plugin loading test",
        "plugin_loaded": True
    })


if __name__ == "__main__":
    # Create router with test routes
    api_router = Router([
        Route("/load-plugin", handler_with_loaded_plugin, methods=["GET"]),
    ])
    
    # Create the PacificApp
    app = PacificApp()
    
    # Mount router
    app.mount_router(api_router)
    
    # Load plugin from module
    try:
        app.plugins.load_plugin_from_module(
            "examples.example_plugin", 
            "ExamplePlugin", 
            "example-plugin", 
            {"example": "config"}
        )
        print("Plugin loaded successfully")
    except Exception as e:
        print(f"Failed to load plugin: {e}")
    
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