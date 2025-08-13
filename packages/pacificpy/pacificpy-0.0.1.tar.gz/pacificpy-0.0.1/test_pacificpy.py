#!/usr/bin/env python3
"""
Simple test script to verify PacificPy installation and basic functionality.
"""

from pacificpy.core.app import PacificApp
from pacificpy.core.http import Request, Response
from pacificpy.core.server import run


async def hello_handler(request: Request) -> Response:
    """Simple hello world handler."""
    return Response.json({
        "message": "Hello, PacificPy!",
        "version": "0.0.1"
    })


if __name__ == "__main__":
    # Create a simple app
    app = PacificApp()
    
    # Add a route
    from starlette.routing import Route, Router
    router = Router([Route("/", hello_handler, methods=["GET"])])
    app.mount_router(router)
    
    # Run the app
    print("Starting PacificPy test server on http://127.0.0.1:8000")
    print("Press CTRL+C to stop")
    run(app, host="127.0.0.1", port=8000)