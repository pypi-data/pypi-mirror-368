from starlette.routing import Route, Router
from starlette.middleware.base import BaseHTTPMiddleware

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings
from pacificpy.core.http import Request, Response


# Global list to track middleware execution order
execution_order = []


class ConditionalMiddleware(BaseHTTPMiddleware):
    """Conditional middleware that only runs when enabled."""
    
    async def dispatch(self, request, call_next):
        execution_order.append("ConditionalMiddleware - Before")
        response = await call_next(request)
        execution_order.append("ConditionalMiddleware - After")
        return response


class AlwaysMiddleware(BaseHTTPMiddleware):
    """Middleware that always runs."""
    
    async def dispatch(self, request, call_next):
        execution_order.append("AlwaysMiddleware - Before")
        response = await call_next(request)
        execution_order.append("AlwaysMiddleware - After")
        return response


# Global flag to control conditional middleware
middleware_enabled = False


def is_middleware_enabled():
    """Condition function for conditional middleware."""
    return middleware_enabled


async def test_handler(request: Request) -> Response:
    """Test handler that returns execution order."""
    global execution_order
    
    # Save current execution order
    order = execution_order.copy()
    
    # Clear execution order for next request
    execution_order.clear()
    
    return Response.json({
        "message": "Test response",
        "execution_order": order,
        "middleware_enabled": middleware_enabled
    })


async def toggle_handler(request: Request) -> Response:
    """Handler to toggle middleware enabled state."""
    global middleware_enabled
    middleware_enabled = not middleware_enabled
    
    return Response.json({
        "message": "Middleware state toggled",
        "middleware_enabled": middleware_enabled
    })


if __name__ == "__main__":
    # Create router with test routes
    api_router = Router([
        Route("/test", test_handler, methods=["GET"]),
        Route("/toggle", toggle_handler, methods=["POST"]),
    ])
    
    # Create the PacificApp
    app = PacificApp()
    
    # Add always running middleware
    app.add_middleware(AlwaysMiddleware, priority=10)
    
    # Add conditional middleware with condition
    app.add_middleware(
        ConditionalMiddleware, 
        priority=20, 
        condition=is_middleware_enabled
    )
    
    # Mount router
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