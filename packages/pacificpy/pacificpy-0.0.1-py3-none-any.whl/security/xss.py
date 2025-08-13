"""
XSS protection helpers for PacificPy.

This module provides utilities for preventing XSS attacks,
including HTML escaping and safe JavaScript serialization.
"""

import html
import json
from typing import Any, Union
from starlette.requests import Request

def escape_html(text: str) -> str:
    """
    Escape HTML special characters in text.
    
    Args:
        text: The text to escape
        
    Returns:
        The escaped text
    """
    return html.escape(text, quote=True)

def escape_js(text: str) -> str:
    """
    Escape text for safe inclusion in JavaScript strings.
    
    Args:
        text: The text to escape
        
    Returns:
        The escaped text
    """
    # Escape backslashes first
    text = text.replace("\\", "\\\\")
    # Escape quotes
    text = text.replace("'", "\\'")
    text = text.replace('"', '\\"')
    # Escape forward slashes
    text = text.replace("/", "\\/")
    # Escape newlines
    text = text.replace("\n", "\\n")
    # Escape carriage returns
    text = text.replace("\r", "\\r")
    # Escape tabs
    text = text.replace("\t", "\\t")
    # Escape null bytes
    text = text.replace("\x00", "\\x00")
    # Escape line separators
    text = text.replace("\u2028", "\\u2028")
    text = text.replace("\u2029", "\\u2029")
    
    return text

def safe_json_dumps(data: Any) -> str:
    """
    Safely serialize data to JSON for use in HTML/JS contexts.
    
    Args:
        data: The data to serialize
        
    Returns:
        The JSON string
    """
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)

def safe_json_script_tag(data: Any, nonce: str = None) -> str:
    """
    Generate a safe JSON script tag.
    
    Args:
        data: The data to serialize
        nonce: The CSP nonce (optional)
        
    Returns:
        A script tag with JSON data
    """
    json_data = safe_json_dumps(data)
    nonce_attr = f' nonce="{nonce}"' if nonce else ""
    return f'<script{nonce_attr} type="application/json">{json_data}</script>'

def xss_escape_jinja2_helper(text: str) -> str:
    """
    Jinja2 helper for escaping text to prevent XSS.
    
    Args:
        text: The text to escape
        
    Returns:
        The escaped text
    """
    return escape_html(text)

def xss_safe_json_jinja2_helper(data: Any) -> str:
    """
    Jinja2 helper for safely serializing data to JSON.
    
    Args:
        data: The data to serialize
        
    Returns:
        The JSON string
    """
    return safe_json_dumps(data)

def xss_safe_js_var_jinja2_helper(var_name: str, data: Any) -> str:
    """
    Jinja2 helper for safely creating a JavaScript variable.
    
    Args:
        var_name: The variable name
        data: The data to serialize
        
    Returns:
        A JavaScript variable declaration
    """
    json_data = safe_json_dumps(data)
    return f"var {var_name} = {json_data};"

# Default set of Jinja2 helpers for XSS protection
JINJA2_HELPERS = {
    "e": xss_escape_jinja2_helper,
    "escape": xss_escape_jinja2_helper,
    "safe_json": xss_safe_json_jinja2_helper,
    "safe_js_var": xss_safe_js_var_jinja2_helper,
}