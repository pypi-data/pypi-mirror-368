"""
Debug error pages for development.

This module provides HTML error pages with detailed tracebacks
for use in debug mode.
"""

import traceback
import html
from typing import Any
from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse
from starlette.routing import Route

async def debug_error_page(request: Request) -> HTMLResponse:
    """
    Debug error page with detailed traceback information.
    
    Args:
        request: The incoming request
        
    Returns:
        An HTML response with error details
    """
    # This endpoint should only be available in debug mode
    if not getattr(request.app, "debug", False):
        return PlainTextResponse("Not Found", status_code=404)
    
    # Get the exception from the request state (if available)
    exc = getattr(request.state, "exception", None)
    
    # Generate HTML page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Error Page</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #d32f2f; }}
            pre {{ background: #f5f5f5; padding: 15px; overflow-x: auto; }}
            .traceback {{ margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>Debug Error Page</h1>
        <div class="traceback">
            <h2>Traceback</h2>
            <pre>{html.escape(traceback.format_exc()) if exc else "No exception available"}</pre>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(html_content, status_code=500)

# Route for debug error page
debug_error_route = Route("/_debug/error", debug_error_page, methods=["GET"])

def add_debug_error_page(app) -> None:
    """
    Add the debug error page route to an application.
    
    Args:
        app: The Starlette application
    """
    # Only add in debug mode
    if getattr(app, "debug", False):
        app.router.routes.append(debug_error_route)