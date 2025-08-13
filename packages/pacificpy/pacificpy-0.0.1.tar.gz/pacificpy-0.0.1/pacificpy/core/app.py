from typing import Any, Callable, Dict, List, Optional, Type, Union

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import BaseRoute, Router
from starlette.types import ASGIApp, Receive, Scope, Send

from .lifecycle import LifecycleManager
from .middleware import MiddlewareManager
from .endpoints.health import health_router
from .context import RequestContext
from .plugins import PluginManager
from ..middleware.context import ContextMiddleware
from ..middleware.trace import TraceMiddleware
from ..middleware.background import BackgroundTaskMiddleware


class PacificApp:
    def __init__(self, settings: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the PacificApp with optional settings.
        
        Args:
            settings: Optional dictionary of application settings.
        """
        self.settings = settings or {}
        self.routers: List[Router] = []
        self.middleware_manager = MiddlewareManager()
        self.lifecycle = LifecycleManager()
        self.plugins = PluginManager()
        
        # Create the underlying Starlette app
        self._app: Optional[Starlette] = None

    def add_middleware(
        self, 
        middleware_class: Union[Type, Middleware],
        priority: int = 100,
        condition: Optional[Callable[[], bool]] = None,
        **kwargs: Any
    ) -> None:
        """
        Add middleware with priority and optional condition.
        
        Args:
            middleware_class: The middleware class or Middleware instance.
            priority: The priority of the middleware (lower numbers execute first).
            condition: Optional condition function that must return True to include middleware.
            **kwargs: Arguments to pass to the middleware constructor.
        """
        self.middleware_manager.add_middleware(
            middleware_class, 
            priority=priority, 
            condition=condition, 
            **kwargs
        )
        # Reset the app so it's recreated with new middleware
        self._app = None

    def mount_router(self, router: Router) -> None:
        """
        Mount a router to the application.
        
        Args:
            router: The router to mount.
        """
        self.routers.append(router)
        # Reset the app so it's recreated with new routers
        self._app = None

    def on_startup(self, func: Callable) -> Callable:
        """
        Register a function to be called on application startup.
        
        Args:
            func: The function to register.
            
        Returns:
            The registered function.
        """
        return self.lifecycle.on_startup(func)

    def on_shutdown(self, func: Callable) -> Callable:
        """
        Register a function to be called on application shutdown.
        
        Args:
            func: The function to register.
            
        Returns:
            The registered function.
        """
        return self.lifecycle.on_shutdown(func)

    def register_plugin(self, plugin) -> None:
        """
        Register a plugin with the application.
        
        Args:
            plugin: The plugin to register.
        """
        self.plugins.register_plugin(plugin)

    def startup(self) -> None:
        """
        Create the underlying Starlette app with all routers, middlewares and events.
        This method is called automatically when the app is first used.
        """
        if self._app is None:
            # Create routes from all mounted routers
            routes: List[BaseRoute] = []
            for router in self.routers:
                routes.extend(router.routes)
            
            # Add built-in health router
            routes.extend(health_router.routes)
            
            # Add trace middleware with high priority (low number)
            self.middleware_manager.add_middleware(
                TraceMiddleware,
                priority=5
            )
            
            # Add context middleware with high priority (low number)
            self.middleware_manager.add_middleware(
                ContextMiddleware,
                priority=10,
                settings=self.settings
            )
            
            # Add background task middleware
            self.middleware_manager.add_middleware(
                BackgroundTaskMiddleware,
                priority=15
            )
            
            # Get middlewares from manager
            middlewares = self.middleware_manager.get_middlewares()
            
            # Create startup and shutdown event handlers
            async def startup_handler():
                # Run lifecycle startup handlers
                await self.lifecycle.run_startup_handlers()
                # Run plugin startup hooks
                await self.plugins.run_startup_hooks()
            
            async def shutdown_handler():
                # Run lifecycle shutdown handlers
                await self.lifecycle.run_shutdown_handlers()
                # Run plugin shutdown hooks
                await self.plugins.run_shutdown_hooks()
            
            # Create the Starlette app
            self._app = Starlette(
                routes=routes,
                middleware=middlewares,
                on_startup=[startup_handler],
                on_shutdown=[shutdown_handler]
            )

    def shutdown(self) -> None:
        """
        Perform any necessary cleanup.
        """
        # Currently no specific cleanup needed
        pass

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        ASGI application callable that proxies to the underlying Starlette app.
        
        Args:
            scope: The ASGI scope.
            receive: The receive channel.
            send: The send channel.
        """
        # Ensure the app is created
        self.startup()
        
        # Proxy to the underlying Starlette app
        assert self._app is not None
        await self._app(scope, receive, send)