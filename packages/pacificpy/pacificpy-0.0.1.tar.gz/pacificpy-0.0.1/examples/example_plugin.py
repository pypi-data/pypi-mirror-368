from pacificpy.core.plugins import Plugin


class ExamplePlugin(Plugin):
    """
    Example plugin that demonstrates plugin functionality.
    """
    
    async def on_startup(self) -> None:
        """
        Called when the application starts up.
        """
        print(f"Plugin '{self.name}' starting up with config: {self.config}")
        # Simulate some startup work
        print(f"Plugin '{self.name}' startup complete")
    
    async def on_shutdown(self) -> None:
        """
        Called when the application shuts down.
        """
        print(f"Plugin '{self.name}' shutting down")
        # Simulate some shutdown work
        print(f"Plugin '{self.name}' shutdown complete")