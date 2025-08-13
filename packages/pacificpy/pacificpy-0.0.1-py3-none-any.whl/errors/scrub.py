"""
Exception scrubbing for secure logging.

This module provides utilities for scrubbing sensitive data from exceptions
before logging, including authorization headers and passwords.
"""

import re
from typing import Any, Dict, List, Union

# Default sensitive keys to scrub
DEFAULT_SENSITIVE_KEYS = {
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "key",
    "authorization",
    "auth",
    "cookie",
    "session"
}

# Default patterns for scrubbing
DEFAULT_SCRUB_PATTERNS = [
    (re.compile(r"(?i)(password|passwd|pwd)\\s*[:=]\\s*[\'\\"][^\'\\"]*[\'\\"]"), r"\\1: ***"),
    (re.compile(r"(?i)(secret|token|key)\\s*[:=]\\s*[\'\\"][^\'\\"]*[\'\\"]"), r"\\1: ***"),
    (re.compile(r"(?i)(authorization|auth)\\s*[:=]\\s*[\'\\"][^\'\\"]*[\'\\"]"), r"\\1: ***"),
]

class ExceptionScrubber:
    """Utility for scrubbing sensitive data from exceptions."""
    
    def __init__(
        self,
        sensitive_keys: set = None,
        scrub_patterns: List[tuple] = None
    ):
        """
        Initialize the exception scrubber.
        
        Args:
            sensitive_keys: Set of keys to consider sensitive
            scrub_patterns: List of (pattern, replacement) tuples for regex scrubbing
        """
        self.sensitive_keys = sensitive_keys or DEFAULT_SENSITIVE_KEYS
        self.scrub_patterns = scrub_patterns or DEFAULT_SCRUB_PATTERNS
    
    def scrub(self, data: Any) -> Any:
        """
        Scrub sensitive data from an object.
        
        Args:
            data: The data to scrub
            
        Returns:
            The scrubbed data
        """
        if isinstance(data, dict):
            return self._scrub_dict(data)
        elif isinstance(data, (list, tuple)):
            return [self.scrub(item) for item in data]
        elif isinstance(data, str):
            return self._scrub_string(data)
        else:
            return data
    
    def _scrub_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Scrub sensitive data from a dictionary."""
        scrubbed = {}
        for key, value in data.items():
            # Scrub sensitive keys
            if key.lower() in self.sensitive_keys:
                scrubbed[key] = "***"
            else:
                scrubbed[key] = self.scrub(value)
        return scrubbed
    
    def _scrub_string(self, data: str) -> str:
        """Scrub sensitive data from a string using regex patterns."""
        scrubbed = data
        for pattern, replacement in self.scrub_patterns:
            scrubbed = pattern.sub(replacement, scrubbed)
        return scrubbed

# Global scrubber instance
_scrubber = ExceptionScrubber()

def scrub_exception_data(data: Any) -> Any:
    """
    Scrub sensitive data from exception context.
    
    Args:
        data: The data to scrub
        
    Returns:
        The scrubbed data
    """
    return _scrubber.scrub(data)

def add_sensitive_key(key: str) -> None:
    """
    Add a key to the list of sensitive keys.
    
    Args:
        key: The key to add
    """
    _scrubber.sensitive_keys.add(key.lower())

def add_scrub_pattern(pattern: str, replacement: str) -> None:
    """
    Add a regex pattern for scrubbing.
    
    Args:
        pattern: The regex pattern to match
        replacement: The replacement string
    """
    compiled_pattern = re.compile(pattern, re.IGNORECASE)
    _scrubber.scrub_patterns.append((compiled_pattern, replacement))