"""
Dependency Injection: Lifecycle management
"""
from typing import List, Callable, Awaitable, Union
import asyncio

class LifecycleManager:
    """
    Manages the lifecycle of dependencies, handling startup and shutdown events.
    """
    
    def __init__(self):
        self._startup_handlers: List[Callable] = []
        self._shutdown_handlers: List[Callable] = []
    
    def add_startup_handler(self, handler: Callable) -> None:
        """
        Add a startup handler.
        
        Args:
            handler: A callable to run at application startup
        """
        self._startup_handlers.append(handler)
    
    def add_shutdown_handler(self, handler: Callable) -> None:
        """
        Add a shutdown handler.
        
        Args:
            handler: A callable to run at application shutdown
        """
        self._shutdown_handlers.append(handler)
    
    async def run_startup(self) -> None:
        """Run all registered startup handlers."""
        for handler in self._startup_handlers:
            if hasattr(handler, 'startup'):
                startup_method = handler.startup
                if asyncio.iscoroutinefunction(startup_method):
                    await startup_method()
                else:
                    startup_method()
            else:
                # If the handler itself is callable
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
    
    async def run_shutdown(self) -> None:
        """Run all registered shutdown handlers."""
        # Run shutdown handlers in reverse order
        for handler in reversed(self._shutdown_handlers):
            if hasattr(handler, 'shutdown'):
                shutdown_method = handler.shutdown
                if asyncio.iscoroutinefunction(shutdown_method):
                    await shutdown_method()
                else:
                    shutdown_method()
            else:
                # If the handler itself is callable
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
    
    def register(self, dependency: object) -> None:
        """
        Register a dependency for lifecycle management.
        
        Args:
            dependency: An object that may have startup/shutdown methods
        """
        # Check for startup method
        if hasattr(dependency, 'startup'):
            self.add_startup_handler(dependency)
        
        # Check for shutdown method
        if hasattr(dependency, 'shutdown'):
            self.add_shutdown_handler(dependency)