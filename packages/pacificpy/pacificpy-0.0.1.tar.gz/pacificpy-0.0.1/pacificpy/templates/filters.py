"""
Template filters for PacificPy.

This module provides useful filters for Jinja2 templates,
including safe URL generation, JavaScript escaping, and date formatting.
"""

import html
import json
import urllib.parse
from datetime import datetime
from typing import Any, Union

def safe_url(url: str) -> str:
    """
    Safely escape a URL for use in templates.
    
    Args:
        url: The URL to escape
        
    Returns:
        The escaped URL
    """
    return html.escape(url, quote=True)

def escape_js(text: str) -> str:
    """
    Escape text for safe inclusion in JavaScript strings.
    
    Args:
        text: The text to escape
        
    Returns:
        The escaped text
    """
    # Escape backslashes first
    text = text.replace("\\\\", "\\\\\\\\")
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

def safe_json(data: Any) -> str:
    """
    Safely serialize data to JSON for use in templates.
    
    Args:
        data: The data to serialize
        
    Returns:
        The JSON string
    """
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)

def format_date(date: Union[datetime, str], format: str = "%Y-%m-%d") -> str:
    """
    Format a date for display in templates.
    
    Args:
        date: The date to format (datetime object or ISO string)
        format: The format string
        
    Returns:
        The formatted date string
    """
    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date)
        except ValueError:
            return date  # Return as-is if parsing fails
    
    if isinstance(date, datetime):
        return date.strftime(format)
    
    return str(date)

def urlencode(value: str) -> str:
    """
    URL encode a string.
    
    Args:
        value: The string to encode
        
    Returns:
        The URL encoded string
    """
    return urllib.parse.quote_plus(value)

def urldecode(value: str) -> str:
    """
    URL decode a string.
    
    Args:
        value: The string to decode
        
    Returns:
        The URL decoded string
    """
    return urllib.parse.unquote_plus(value)

def truncate_chars(text: str, length: int, suffix: str = "...") -> str:
    """
    Truncate text to a specified length.
    
    Args:
        text: The text to truncate
        length: The maximum length
        suffix: The suffix to append if truncated
        
    Returns:
        The truncated text
    """
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix

def filesize_format(size: int) -> str:
    """
    Format a file size in human-readable format.
    
    Args:
        size: The file size in bytes
        
    Returns:
        The formatted file size
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

# Default filters dictionary
DEFAULT_FILTERS = {
    "safe_url": safe_url,
    "escape_js": escape_js,
    "safe_json": safe_json,
    "format_date": format_date,
    "urlencode": urlencode,
    "urldecode": urldecode,
    "truncate_chars": truncate_chars,
    "filesize_format": filesize_format,
}

# Filter registration function
def register_filters(env) -> None:
    """
    Register default filters with a Jinja2 environment.
    
    Args:
        env: The Jinja2 environment
    """
    for name, func in DEFAULT_FILTERS.items():
        env.filters[name] = func

# Filter decorator
def template_filter(name: str = None):
    """
    Decorator for creating custom template filters.
    
    Args:
        name: The name of the filter (defaults to function name)
        
    Returns:
        The decorator function
    """
    def decorator(func):
        filter_name = name or func.__name__
        DEFAULT_FILTERS[filter_name] = func
        return func
    return decorator