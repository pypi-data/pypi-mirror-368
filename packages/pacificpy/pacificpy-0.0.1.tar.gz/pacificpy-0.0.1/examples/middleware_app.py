from starlette.routing import Route, Router
from starlette.middleware.base import BaseHTTPMiddleware

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings
from pacificpy.core.http import Request, Response


# Global list to track middleware execution order
execution_order = []


class FirstMiddleware(BaseHTTPMiddleware):
    """First middleware with priority 10."""
    
    async def dispatch(self, request, call_next):
        execution_order.append("FirstMiddleware - Before")
        response = await call_next(request)
        execution_order.append("FirstMiddleware - After")
        return response


class SecondMiddleware(BaseHTTPMiddleware):
    """Second middleware with priority 20."""
    
    async def dispatch(self, request, call_next):
        execution_order.append("SecondMiddleware - Before")
        response = await call_next(request)
        execution_order.append("SecondMiddleware - After")
        return response


class ThirdMiddleware(BaseHTTPMiddleware):
    """Third middleware with priority 30."""
    
    async def dispatch(self, request, call_next):
        execution_order.append("ThirdMiddleware - Before")
        response = await call_next(request)
        execution_order.append("ThirdMiddleware - After")
        return response


async def test_handler(request: Request) -> Response:
    """Test handler that returns execution order."""
    global execution_order
    
    # Save current execution order
    order = execution_order.copy()
    
    # Clear execution order for next request
    execution_order.clear()
    
    return Response.json({
        "message": "Test response",
        "execution_order": order
    })


if __name__ == "__main__":
    # Create router with test route
    api_router = Router([
        Route("/test", test_handler, methods=["GET"]),
    ])
    
    # Create the PacificApp
    app = PacificApp()
    
    # Add middlewares with different priorities
    # Lower priority numbers execute first
    app.add_middleware(ThirdMiddleware, priority=30)
    app.add_middleware(FirstMiddleware, priority=10)
    app.add_middleware(SecondMiddleware, priority=20)
    
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