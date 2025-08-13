from starlette.routing import Route, Router

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings
from pacificpy.core.http import Request, Response
from pacificpy.core.plugins import Plugin


# Global variable to track plugin execution
plugin_startup_called = False
plugin_name = None


class StartupPlugin(Plugin):
    """
    Plugin that tracks startup execution.
    """
    
    async def on_startup(self) -> None:
        """Called when the application starts up."""
        global plugin_startup_called, plugin_name
        plugin_startup_called = True
        plugin_name = self.name
        print(f"StartupPlugin '{self.name}' executed with config: {self.config}")


async def handler_with_plugin(request: Request) -> Response:
    """Handler that demonstrates plugin functionality."""
    global plugin_startup_called, plugin_name
    
    return Response.json({
        "message": "Plugin test",
        "plugin_startup_called": plugin_startup_called,
        "plugin_name": plugin_name
    })


if __name__ == "__main__":
    # Create router with test routes
    api_router = Router([
        Route("/plugin-test", handler_with_plugin, methods=["GET"]),
    ])
    
    # Create the PacificApp
    app = PacificApp()
    
    # Mount router
    app.mount_router(api_router)
    
    # Register a plugin
    plugin = StartupPlugin("startup-plugin", {"test": "config"})
    app.register_plugin(plugin)
    
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