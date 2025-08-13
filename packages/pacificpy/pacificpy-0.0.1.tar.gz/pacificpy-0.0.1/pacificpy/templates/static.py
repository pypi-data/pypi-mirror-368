"""
Static files serving for PacificPy.

This module provides secure static file serving with proper
Cache-Control headers, ETag support, and optional X-Accel-Redirect support.
"""

import os
import hashlib
import time
from typing import Optional, Tuple
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import Response, FileResponse
from starlette.datastructures import Headers

class StaticFilesMiddleware:
    """ASGI middleware for serving static files."""
    
    def __init__(
        self,
        app: ASGIApp,
        static_dir: str = "static",
        path_prefix: str = "/static",
        cache_max_age: int = 3600,  # 1 hour
        etag_enabled: bool = True,
        x_accel_redirect: bool = False,
        x_accel_redirect_prefix: str = "/internal",
    ):
        """
        Initialize the static files middleware.
        
        Args:
            app: The ASGI application
            static_dir: Directory containing static files
            path_prefix: URL prefix for static files
            cache_max_age: Cache max age in seconds
            etag_enabled: Whether to enable ETag generation
            x_accel_redirect: Whether to use X-Accel-Redirect for Nginx
            x_accel_redirect_prefix: Prefix for X-Accel-Redirect
        """
        self.app = app
        self.static_dir = os.path.abspath(static_dir)
        self.path_prefix = path_prefix.rstrip("/")
        self.cache_max_age = cache_max_age
        self.etag_enabled = etag_enabled
        self.x_accel_redirect = x_accel_redirect
        self.x_accel_redirect_prefix = x_accel_redirect_prefix
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and serve static files if applicable.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request_path = scope["path"]
        
        # Check if request path matches static files prefix
        if not request_path.startswith(self.path_prefix):
            await self.app(scope, receive, send)
            return
        
        # Get the file path
        file_path = request_path[len(self.path_prefix):].lstrip("/")
        full_path = os.path.join(self.static_dir, file_path)
        
        # Security check: prevent directory traversal
        if not os.path.abspath(full_path).startswith(self.static_dir):
            response = Response("Forbidden", status_code=403)
            await response(scope, receive, send)
            return
        
        # Check if file exists
        if not os.path.isfile(full_path):
            await self.app(scope, receive, send)
            return
        
        # Handle the static file request
        await self._serve_static_file(scope, receive, send, full_path)
    
    async def _serve_static_file(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        file_path: str,
    ) -> None:
        """
        Serve a static file.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
            file_path: The path to the file to serve
        """
        # Get file stats
        stat = os.stat(file_path)
        file_size = stat.st_size
        last_modified = stat.st_mtime
        
        # Generate ETag if enabled
        etag = None
        if self.etag_enabled:
            etag = self._generate_etag(file_path, last_modified, file_size)
        
        # Check If-None-Match header
        headers = Headers(scope=scope)
        if_none_match = headers.get("if-none-match")
        if if_none_match and etag and if_none_match == etag:
            # Return 304 Not Modified
            response = Response("", status_code=304)
            await response(scope, receive, send)
            return
        
        # Check If-Modified-Since header
        if_modified_since = headers.get("if-modified-since")
        if if_modified_since:
            try:
                if_modified_since_ts = time.mktime(
                    time.strptime(if_modified_since, "%a, %d %b %Y %H:%M:%S GMT")
                )
                if if_modified_since_ts >= last_modified:
                    # Return 304 Not Modified
                    response = Response("", status_code=304)
                    await response(scope, receive, send)
                    return
            except ValueError:
                pass  # Invalid date format, ignore
        
        # Prepare response headers
        response_headers = {
            "content-length": str(file_size),
            "last-modified": time.strftime(
                "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(last_modified)
            ),
            "cache-control": f"public, max-age={self.cache_max_age}",
        }
        
        # Add ETag header if enabled
        if etag:
            response_headers["etag"] = etag
        
        # Use X-Accel-Redirect if enabled
        if self.x_accel_redirect:
            # Calculate internal path
            relative_path = os.path.relpath(file_path, self.static_dir)
            internal_path = f"{self.x_accel_redirect_prefix}/{relative_path}"
            
            response_headers["x-accel-redirect"] = internal_path
            response = Response("", headers=response_headers)
            await response(scope, receive, send)
            return
        
        # Serve file directly
        file_response = FileResponse(
            file_path,
            headers=response_headers,
        )
        await file_response(scope, receive, send)
    
    def _generate_etag(self, file_path: str, last_modified: float, file_size: int) -> str:
        """
        Generate an ETag for a file.
        
        Args:
            file_path: The path to the file
            last_modified: The last modified time
            file_size: The file size
            
        Returns:
            The ETag
        """
        # Create a simple ETag based on file metadata
        etag_data = f"{file_path}-{last_modified}-{file_size}"
        return hashlib.md5(etag_data.encode()).hexdigest()

# Helper functions
def static_files_middleware(
    app: ASGIApp,
    static_dir: str = "static",
    path_prefix: str = "/static",
    cache_max_age: int = 3600,
    etag_enabled: bool = True,
) -> StaticFilesMiddleware:
    """
    Create a static files middleware with default settings.
    
    Args:
        app: The ASGI application
        static_dir: Directory containing static files
        path_prefix: URL prefix for static files
        cache_max_age: Cache max age in seconds
        etag_enabled: Whether to enable ETag generation
        
    Returns:
        A StaticFilesMiddleware instance
    """
    return StaticFilesMiddleware(
        app,
        static_dir=static_dir,
        path_prefix=path_prefix,
        cache_max_age=cache_max_age,
        etag_enabled=etag_enabled,
    )

# Default static files configuration
def default_static_files(app: ASGIApp) -> StaticFilesMiddleware:
    """
    Create a default static files middleware configuration.
    
    Args:
        app: The ASGI application
        
    Returns:
        A StaticFilesMiddleware instance
    """
    return StaticFilesMiddleware(
        app,
        static_dir=os.path.join(os.getcwd(), "static"),
        path_prefix="/static",
        cache_max_age=3600,
        etag_enabled=True,
    )