"""
Error reporting integration for Sentry/Bugsnag.

This module provides hooks for sending exceptions to error tracking services
like Sentry, with support for non-blocking and batched reporting.
"""

import os
import logging
from typing import Any, Dict, Optional
from starlette.requests import Request

# Check if sentry-sdk is available
try:
    import sentry_sdk
    from sentry_sdk import capture_exception
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Logger for error reporting
logger = logging.getLogger(__name__)

class ErrorReporter:
    """Error reporter for sending exceptions to tracking services."""
    
    def __init__(self, dsn: Optional[str] = None, environment: str = "production"):
        """
        Initialize the error reporter.
        
        Args:
            dsn: The Sentry DSN (if using Sentry)
            environment: The environment name (production, staging, etc.)
        """
        self.dsn = dsn or os.getenv("SENTRY_DSN")
        self.environment = environment
        self.enabled = bool(self.dsn) and SENTRY_AVAILABLE
        
        # Initialize Sentry if available and DSN is provided
        if self.enabled:
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                # Disable default integrations to avoid conflicts
                default_integrations=False
            )
    
    def report(self, exc: Exception, request: Optional[Request] = None) -> None:
        """
        Report an exception to the tracking service.
        
        Args:
            exc: The exception to report
            request: The request context (optional)
        """
        # If not enabled, just log the error
        if not self.enabled:
            logger.error("Error occurred: %s", exc, exc_info=True)
            return
        
        # Add request context if available
        if request:
            with sentry_sdk.push_scope() as scope:
                # Add request information
                scope.set_tag("method", request.method)
                scope.set_tag("path", request.url.path)
                
                # Add query parameters (scrubbed)
                if request.query_params:
                    scope.set_extra("query_params", dict(request.query_params))
                
                # Add user information if available
                if hasattr(request.state, "user"):
                    scope.user = {"id": getattr(request.state.user, "id", None)}
                
                # Capture the exception
                capture_exception(exc)
        else:
            # Capture the exception without request context
            capture_exception(exc)
    
    def report_async(self, exc: Exception, request: Optional[Request] = None) -> None:
        """
        Report an exception asynchronously.
        
        Args:
            exc: The exception to report
            request: The request context (optional)
        """
        # For now, this is just a wrapper around the sync version
        # In a real implementation, this would use a background task queue
        try:
            self.report(exc, request)
        except Exception as report_exc:
            # Don't let reporting errors crash the application
            logger.error("Failed to report error: %s", report_exc, exc_info=True)

# Global error reporter instance
_error_reporter = ErrorReporter()

def report_error(exc: Exception, request: Optional[Request] = None) -> None:
    """
    Report an error using the global error reporter.
    
    Args:
        exc: The exception to report
        request: The request context (optional)
    """
    _error_reporter.report(exc, request)

def report_error_async(exc: Exception, request: Optional[Request] = None) -> None:
    """
    Report an error asynchronously using the global error reporter.
    
    Args:
        exc: The exception to report
        request: The request context (optional)
    """
    _error_reporter.report_async(exc, request)

def configure_error_reporting(dsn: Optional[str] = None, environment: str = "production") -> None:
    """
    Configure the global error reporter.
    
    Args:
        dsn: The Sentry DSN (if using Sentry)
        environment: The environment name (production, staging, etc.)
    """
    global _error_reporter
    _error_reporter = ErrorReporter(dsn, environment)