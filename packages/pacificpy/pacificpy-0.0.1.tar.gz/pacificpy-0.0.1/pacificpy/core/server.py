import asyncio
import sys
from typing import Any

from starlette.types import ASGIApp


def run(
    app: ASGIApp,
    host: str = "127.0.0.1",
    port: int = 8000,
    use_uvloop: bool = True,
    reload: bool = False,
    **kwargs: Any
) -> None:
    """
    Run the ASGI application using uvicorn server.
    
    Args:
        app: The ASGI application to run.
        host: The host to bind to.
        port: The port to bind to.
        use_uvloop: Whether to use uvloop if available.
        reload: Whether to enable auto-reload on code changes.
        **kwargs: Additional arguments to pass to uvicorn.run().
    """
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is not installed. Please install it with 'pip install uvicorn'")
        sys.exit(1)
    
    # Check if uvloop is available and should be used
    if use_uvloop:
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            print("Using uvloop event loop policy")
        except ImportError:
            print("uvloop not available, using default asyncio event loop")
    
    # Prepare uvicorn config
    config = {
        "host": host,
        "port": port,
        "reload": reload,
        **kwargs
    }
    
    # Run the application
    uvicorn.run(app, **config)