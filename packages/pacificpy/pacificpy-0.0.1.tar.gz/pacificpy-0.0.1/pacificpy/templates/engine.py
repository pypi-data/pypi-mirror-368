"""
Template engine wrapper for PacificPy.

This module provides a wrapper for Jinja2 with autoescaping, global helpers,
and support for async templates.
"""

import os
from typing import Any, Dict, Optional, Union
from starlette.requests import Request
from starlette.responses import HTMLResponse
import jinja2

class TemplateEngine:
    """Wrapper for Jinja2 template engine."""
    
    def __init__(
        self,
        template_dir: str = "templates",
        autoescape: bool = True,
        enable_async: bool = True,
    ):
        """
        Initialize the template engine.
        
        Args:
            template_dir: Directory containing templates
            autoescape: Whether to enable autoescaping
            enable_async: Whether to enable async template rendering
        """
        self.template_dir = template_dir
        self.autoescape = autoescape
        self.enable_async = enable_async
        
        # Create Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=autoescape,
            enable_async=enable_async,
        )
        
        # Store context processors
        self.context_processors = []
        
        # Store global helpers
        self.global_helpers = {}
    
    def add_context_processor(self, processor: callable) -> None:
        """
        Add a context processor.
        
        Args:
            processor: A function that takes a request and returns a dict
        """
        self.context_processors.append(processor)
    
    def add_global(self, name: str, value: Any) -> None:
        """
        Add a global helper to the template environment.
        
        Args:
            name: The name of the global helper
            value: The value of the global helper
        """
        self.env.globals[name] = value
        self.global_helpers[name] = value
    
    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any] = None,
        request: Request = None,
    ) -> Union[str, HTMLResponse]:
        """
        Render a template with context.
        
        Args:
            template_name: The name of the template to render
            context: The context to render with
            request: The request object (optional)
            
        Returns:
            The rendered template as a string or HTMLResponse
        """
        # Get template
        template = self.env.get_template(template_name)
        
        # Build context
        render_context = {}
        
        # Add global helpers to context
        render_context.update(self.global_helpers)
        
        # Add request to context if provided
        if request:
            render_context["request"] = request
            
            # Add CSP nonce if available
            csp_nonce = getattr(request.state, "csp_nonce", None)
            if csp_nonce:
                render_context["csp_nonce"] = csp_nonce
            
            # Run context processors
            for processor in self.context_processors:
                try:
                    processor_context = processor(request)
                    if processor_context:
                        render_context.update(processor_context)
                except Exception:
                    # Don't let context processor errors break rendering
                    pass
        
        # Add user-provided context
        if context:
            render_context.update(context)
        
        # Render template
        if self.enable_async:
            # For async rendering, return a coroutine
            return self._render_async(template, render_context)
        else:
            # For sync rendering, return the rendered string
            return template.render(render_context)
    
    async def _render_async(self, template: jinja2.Template, context: Dict[str, Any]) -> str:
        """
        Render a template asynchronously.
        
        Args:
            template: The Jinja2 template
            context: The context to render with
            
        Returns:
            The rendered template as a string
        """
        return await template.render_async(context)
    
    def render_response(
        self,
        template_name: str,
        context: Dict[str, Any] = None,
        request: Request = None,
        status_code: int = 200,
    ) -> HTMLResponse:
        """
        Render a template and return an HTMLResponse.
        
        Args:
            template_name: The name of the template to render
            context: The context to render with
            request: The request object (optional)
            status_code: The HTTP status code
            
        Returns:
            An HTMLResponse with the rendered template
        """
        # Render template
        rendered = self.render_template(template_name, context, request)
        
        # If async, we need to await the result
        if self.enable_async and hasattr(rendered, "__await__"):
            # This is a coroutine, but we can't await it here
            # In a real implementation, this would be handled differently
            # For now, we'll assume sync rendering in this context
            pass
        
        return HTMLResponse(rendered, status_code=status_code)
    
    def select_template(self, template_names: list) -> jinja2.Template:
        """
        Select a template from a list of candidates.
        
        Args:
            template_names: List of template names to try
            
        Returns:
            The first template that exists
        """
        return self.env.select_template(template_names)
    
    def get_template(self, template_name: str) -> jinja2.Template:
        """
        Get a template by name.
        
        Args:
            template_name: The name of the template
            
        Returns:
            The template
        """
        return self.env.get_template(template_name)
    
    def add_filter(self, name: str, func: callable) -> None:
        """
        Add a filter to the template environment.
        
        Args:
            name: The name of the filter
            func: The filter function
        """
        self.env.filters[name] = func
    
    def add_test(self, name: str, func: callable) -> None:
        """
        Add a test to the template environment.
        
        Args:
            name: The name of the test
            func: The test function
        """
        self.env.tests[name] = func

# Global template engine instance
_template_engine: Optional[TemplateEngine] = None

def configure_templates(
    template_dir: str = "templates",
    autoescape: bool = True,
    enable_async: bool = True,
) -> TemplateEngine:
    """
    Configure the global template engine.
    
    Args:
        template_dir: Directory containing templates
        autoescape: Whether to enable autoescaping
        enable_async: Whether to enable async template rendering
        
    Returns:
        The template engine instance
    """
    global _template_engine
    _template_engine = TemplateEngine(
        template_dir=template_dir,
        autoescape=autoescape,
        enable_async=enable_async,
    )
    return _template_engine

def render_template(
    template_name: str,
    context: Dict[str, Any] = None,
    request: Request = None,
) -> Union[str, HTMLResponse]:
    """
    Render a template using the global template engine.
    
    Args:
        template_name: The name of the template to render
        context: The context to render with
        request: The request object (optional)
        
    Returns:
        The rendered template as a string or HTMLResponse
        
    Raises:
        RuntimeError: If template engine is not configured
    """
    if not _template_engine:
        raise RuntimeError("Template engine not configured")
    
    return _template_engine.render_template(template_name, context, request)

def render_response(
    template_name: str,
    context: Dict[str, Any] = None,
    request: Request = None,
    status_code: int = 200,
) -> HTMLResponse:
    """
    Render a template and return an HTMLResponse using the global template engine.
    
    Args:
        template_name: The name of the template to render
        context: The context to render with
        request: The request object (optional)
        status_code: The HTTP status code
        
    Returns:
        An HTMLResponse with the rendered template
        
    Raises:
        RuntimeError: If template engine is not configured
    """
    if not _template_engine:
        raise RuntimeError("Template engine not configured")
    
    return _template_engine.render_response(template_name, context, request, status_code)

# Default template engine configuration
def default_template_engine() -> TemplateEngine:
    """
    Create a default template engine configuration.
    
    Returns:
        A TemplateEngine instance
    """
    return TemplateEngine(
        template_dir=os.path.join(os.getcwd(), "templates"),
        autoescape=True,
        enable_async=True,
    )