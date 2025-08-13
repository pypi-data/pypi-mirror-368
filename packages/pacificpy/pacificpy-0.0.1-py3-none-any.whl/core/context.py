from typing import Optional, Any
from contextvars import ContextVar
from starlette.requests import Request


# Context variables for request and settings
_request_context: ContextVar[Optional[Request]] = ContextVar("_request_context", default=None)
_settings_context: ContextVar[Optional[Any]] = ContextVar("_settings_context", default=None)


class RequestContext:
    """
    Context manager for accessing current request and settings.
    """
    
    def __init__(self, request: Request, settings: Optional[Any] = None) -> None:
        """
        Initialize the request context.
        
        Args:
            request: The current request object.
            settings: The current settings object (optional).
        """
        self.request = request
        self.settings = settings
        self._token_request = None
        self._token_settings = None
    
    def __enter__(self) -> "RequestContext":
        """
        Enter the context manager.
        
        Returns:
            The request context instance.
        """
        self._token_request = _request_context.set(self.request)
        if self.settings is not None:
            self._token_settings = _settings_context.set(self.settings)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context manager.
        """
        if self._token_request is not None:
            _request_context.reset(self._token_request)
        if self._token_settings is not None:
            _settings_context.reset(self._token_settings)
    
    @classmethod
    def get_request(cls) -> Optional[Request]:
        """
        Get the current request from context.
        
        Returns:
            The current request object or None if not available.
        """
        return _request_context.get()
    
    @classmethod
    def get_settings(cls) -> Optional[Any]:
        """
        Get the current settings from context.
        
        Returns:
            The current settings object or None if not available.
        """
        return _settings_context.get()
    
    @classmethod
    def get_trace_id(cls) -> Optional[str]:
        """
        Get the current trace ID from request context.
        
        Returns:
            The current trace ID or None if not available.
        """
        request = cls.get_request()
        if request and hasattr(request, 'state'):
            # Use getattr with default None to avoid AttributeError
            return getattr(request.state, 'trace_id', None)
        return None