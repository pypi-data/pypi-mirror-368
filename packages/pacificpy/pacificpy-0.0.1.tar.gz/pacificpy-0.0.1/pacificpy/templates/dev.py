"""
Development utilities for PacificPy templates.

This module provides utilities for template development,
including auto-reload in debug mode.
"""

import os
import time
from typing import Dict, Set
from starlette.types import ASGIApp, Receive, Scope, Send
import jinja2

class TemplateReloadMiddleware:
    """ASGI middleware for automatic template reloading in development."""
    
    def __init__(
        self,
        app: ASGIApp,
        template_dirs: list = None,
        check_interval: float = 1.0,
    ):
        """
        Initialize the template reload middleware.
        
        Args:
            app: The ASGI application
            template_dirs: List of template directories to monitor
            check_interval: Interval between checks for file changes (seconds)
        """
        self.app = app
        self.template_dirs = template_dirs or ["templates"]
        self.check_interval = check_interval
        self.last_check = 0.0
        self.file_timestamps: Dict[str, float] = {}
        self.template_envs: Set[jinja2.Environment] = set()
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and check for template changes.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check for template changes if enough time has passed
        current_time = time.time()
        if current_time - self.last_check > self.check_interval:
            self._check_for_changes()
            self.last_check = current_time
        
        await self.app(scope, receive, send)
    
    def _check_for_changes(self) -> None:
        """Check for changes in template files."""
        changed_files = []
        
        # Check each template directory
        for template_dir in self.template_dirs:
            if not os.path.exists(template_dir):
                continue
                
            # Walk the directory tree
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Get current modification time
                    try:
                        mtime = os.path.getmtime(file_path)
                    except OSError:
                        continue
                    
                    # Check if file has changed
                    if file_path not in self.file_timestamps:
                        # New file
                        self.file_timestamps[file_path] = mtime
                        changed_files.append(file_path)
                    elif self.file_timestamps[file_path] != mtime:
                        # Modified file
                        self.file_timestamps[file_path] = mtime
                        changed_files.append(file_path)
        
        # If any files have changed, clear template caches
        if changed_files:
            self._clear_template_caches()
    
    def _clear_template_caches(self) -> None:
        """Clear template caches in all registered environments."""
        for env in self.template_envs:
            env.cache.clear()
    
    def register_template_env(self, env: jinja2.Environment) -> None:
        """
        Register a Jinja2 environment for auto-reload.
        
        Args:
            env: The Jinja2 environment
        """
        self.template_envs.add(env)

# Global template reload middleware
_template_reload_middleware: TemplateReloadMiddleware = None

def configure_template_reload(
    app: ASGIApp,
    template_dirs: list = None,
    check_interval: float = 1.0,
) -> TemplateReloadMiddleware:
    """
    Configure template auto-reload for development.
    
    Args:
        app: The ASGI application
        template_dirs: List of template directories to monitor
        check_interval: Interval between checks for file changes (seconds)
        
    Returns:
        The template reload middleware
    """
    global _template_reload_middleware
    _template_reload_middleware = TemplateReloadMiddleware(
        app,
        template_dirs=template_dirs,
        check_interval=check_interval,
    )
    return _template_reload_middleware

def register_template_env(env: jinja2.Environment) -> None:
    """
    Register a Jinja2 environment for auto-reload.
    
    Args:
        env: The Jinja2 environment
    """
    if _template_reload_middleware:
        _template_reload_middleware.register_template_env(env)

# Development template engine with auto-reload
class DevelopmentTemplateEngine:
    """Template engine with auto-reload for development."""
    
    def __init__(
        self,
        template_dir: str = "templates",
        autoescape: bool = True,
        enable_async: bool = True,
        debug: bool = True,
    ):
        """
        Initialize the development template engine.
        
        Args:
            template_dir: Directory containing templates
            autoescape: Whether to enable autoescaping
            enable_async: Whether to enable async template rendering
            debug: Whether to enable debug mode with auto-reload
        """
        self.template_dir = template_dir
        self.debug = debug
        
        # Create Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=autoescape,
            enable_async=enable_async,
        )
        
        # Register with auto-reload if in debug mode
        if debug:
            register_template_env(self.env)
    
    def get_template(self, template_name: str) -> jinja2.Template:
        """
        Get a template by name.
        
        Args:
            template_name: The name of the template
            
        Returns:
            The template
        """
        return self.env.get_template(template_name)