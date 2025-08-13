"""
Form helpers for PacificPy templates.

This module provides utilities for creating CSRF-protected forms
and inserting hidden CSRF tokens.
"""

from typing import Dict, Any, Optional
from starlette.requests import Request

class FormHelper:
    """Helper for creating forms in templates."""
    
    def __init__(self, request: Request):
        """
        Initialize the form helper.
        
        Args:
            request: The request object
        """
        self.request = request
    
    def csrf_token(self) -> str:
        """
        Get the CSRF token for the current request.
        
        Returns:
            The CSRF token
        """
        # Try to get CSRF token from session
        session = getattr(self.request.state, "session", None)
        if session and "csrf_token" in session:
            return session["csrf_token"]
        
        # Try to get CSRF token from cookies
        return self.request.cookies.get("csrftoken", "")
    
    def hidden_csrf_token(self) -> str:
        """
        Generate a hidden CSRF token input field.
        
        Returns:
            HTML for a hidden CSRF token input
        """
        token = self.csrf_token()
        if not token:
            return ""
        
        return f'<input type="hidden" name="csrf_token" value="{token}">'
    
    def form_begin(
        self,
        action: str = "",
        method: str = "POST",
        enctype: str = "multipart/form-data",
        **kwargs
    ) -> str:
        """
        Generate the opening tag for a form with CSRF protection.
        
        Args:
            action: The form action
            method: The form method
            enctype: The form encoding type
            **kwargs: Additional attributes for the form tag
            
        Returns:
            HTML for the opening form tag
        """
        # Build attributes
        attrs = [f'action="{action}"', f'method="{method}"', f'enctype="{enctype}"']
        
        # Add any additional attributes
        for key, value in kwargs.items():
            attrs.append(f'{key}="{value}"')
        
        # Join attributes
        attrs_str = " ".join(attrs)
        
        # Return form opening tag with CSRF token
        return f'<form {attrs_str}>\n{self.hidden_csrf_token()}'
    
    def form_end(self) -> str:
        """
        Generate the closing tag for a form.
        
        Returns:
            HTML for the closing form tag
        """
        return "</form>"
    
    def input_field(
        self,
        name: str,
        type: str = "text",
        value: str = "",
        label: str = "",
        **kwargs
    ) -> str:
        """
        Generate an input field with optional label.
        
        Args:
            name: The input name
            type: The input type
            value: The input value
            label: The input label
            **kwargs: Additional attributes for the input tag
            
        Returns:
            HTML for the input field
        """
        # Build attributes
        attrs = [f'name="{name}"', f'type="{type}"', f'value="{value}"']
        
        # Add any additional attributes
        for key, value in kwargs.items():
            attrs.append(f'{key}="{value}"')
        
        # Join attributes
        attrs_str = " ".join(attrs)
        
        # Generate label if provided
        label_html = f'<label for="{name}">{label}</label>\n' if label else ""
        
        # Return input field
        return f'{label_html}<input {attrs_str}>'
    
    def textarea_field(
        self,
        name: str,
        value: str = "",
        label: str = "",
        rows: int = 4,
        cols: int = 50,
        **kwargs
    ) -> str:
        """
        Generate a textarea field with optional label.
        
        Args:
            name: The textarea name
            value: The textarea value
            label: The textarea label
            rows: The number of rows
            cols: The number of columns
            **kwargs: Additional attributes for the textarea tag
            
        Returns:
            HTML for the textarea field
        """
        # Build attributes
        attrs = [f'name="{name}"', f'rows="{rows}"', f'cols="{cols}"']
        
        # Add any additional attributes
        for key, value in kwargs.items():
            attrs.append(f'{key}="{value}"')
        
        # Join attributes
        attrs_str = " ".join(attrs)
        
        # Generate label if provided
        label_html = f'<label for="{name}">{label}</label>\n' if label else ""
        
        # Return textarea field
        return f'{label_html}<textarea {attrs_str}>{value}</textarea>'
    
    def select_field(
        self,
        name: str,
        options: list,
        selected: str = "",
        label: str = "",
        **kwargs
    ) -> str:
        """
        Generate a select field with options and optional label.
        
        Args:
            name: The select name
            options: List of (value, label) tuples
            selected: The selected value
            label: The select label
            **kwargs: Additional attributes for the select tag
            
        Returns:
            HTML for the select field
        """
        # Build attributes
        attrs = [f'name="{name}"']
        
        # Add any additional attributes
        for key, value in kwargs.items():
            attrs.append(f'{key}="{value}"')
        
        # Join attributes
        attrs_str = " ".join(attrs)
        
        # Generate options
        options_html = ""
        for value, option_label in options:
            selected_attr = ' selected' if value == selected else ''
            options_html += f'    <option value="{value}"{selected_attr}>{option_label}</option>\n'
        
        # Generate label if provided
        label_html = f'<label for="{name}">{label}</label>\n' if label else ""
        
        # Return select field
        return f'{label_html}<select {attrs_str}>\n{options_html}</select>'

# Global form helper function
def get_form_helper(request: Request) -> FormHelper:
    """
    Get a form helper for a request.
    
    Args:
        request: The request object
        
    Returns:
        A FormHelper instance
    """
    return FormHelper(request)

# Template global functions
def register_form_helpers(env) -> None:
    """
    Register form helpers as global functions in a Jinja2 environment.
    
    Args:
        env: The Jinja2 environment
    """
    env.globals["csrf_token"] = lambda: ""
    env.globals["hidden_csrf_token"] = lambda: ""
    env.globals["form_begin"] = lambda **kwargs: ""
    env.globals["form_end"] = lambda: ""
    env.globals["input_field"] = lambda **kwargs: ""
    env.globals["textarea_field"] = lambda **kwargs: ""
    env.globals["select_field"] = lambda **kwargs: ""

# Context processor for form helper
def form_context_processor(request: Request) -> Dict[str, Any]:
    """
    Context processor that adds form helper to template context.
    
    Args:
        request: The request object
        
    Returns:
        A dictionary with form helper context
    """
    return {
        "form": get_form_helper(request),
    }