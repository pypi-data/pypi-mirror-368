from typing import Callable, List, Union
import asyncio
import inspect


class LifecycleManager:
    """
    Manages application lifecycle events (startup/shutdown).
    """
    
    def __init__(self) -> None:
        """Initialize the lifecycle manager."""
        self._startup_handlers: List[Callable] = []
        self._shutdown_handlers: List[Callable] = []
    
    def on_startup(self, func: Callable) -> Callable:
        """
        Register a function to be called on application startup.
        
        Args:
            func: The function to register.
            
        Returns:
            The registered function.
        """
        self._startup_handlers.append(func)
        return func
    
    def on_shutdown(self, func: Callable) -> Callable:
        """
        Register a function to be called on application shutdown.
        
        Args:
            func: The function to register.
            
        Returns:
            The registered function.
        """
        self._shutdown_handlers.append(func)
        return func
    
    async def run_startup_handlers(self) -> None:
        """
        Run all registered startup handlers.
        """
        for handler in self._startup_handlers:
            if inspect.iscoroutinefunction(handler):
                await handler()
            else:
                handler()
    
    async def run_shutdown_handlers(self) -> None:
        """
        Run all registered shutdown handlers.
        """
        for handler in self._shutdown_handlers:
            if inspect.iscoroutinefunction(handler):
                await handler()
            else:
                handler()