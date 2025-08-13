"""
Validation configuration settings.

This module provides configuration options for request validation,
including strict vs permissive validation modes.
"""

from typing import Any, Dict
import os

# Default to strict validation for security
VALIDATION_STRICT = os.getenv("VALIDATION_STRICT", "true").lower() == "true"

# Configuration class for validation settings
class ValidationConfig:
    """Configuration class for validation settings."""
    
    def __init__(self, strict: bool = VALIDATION_STRICT):
        """
        Initialize validation configuration.
        
        Args:
            strict: Whether to use strict validation (default: True)
        """
        self.strict = strict
    
    def get_pydantic_config(self) -> Dict[str, Any]:
        """
        Get Pydantic model configuration based on validation mode.
        
        Returns:
            A dictionary with Pydantic configuration options
        """
        if self.strict:
            # In strict mode, extra fields are not allowed
            return {"extra": "forbid"}
        else:
            # In permissive mode, extra fields are ignored
            return {"extra": "ignore"}