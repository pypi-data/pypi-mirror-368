from typing import Any, Optional, Union
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
from starlette.datastructures import State
import json
import uuid


class Request(StarletteRequest):
    """
    Thin wrapper around Starlette Request with additional fields and helpers.
    """
    
    def __init__(self, scope, receive):
        """
        Initialize the Request.
        
        Args:
            scope: The ASGI scope.
            receive: The receive channel.
        """
        super().__init__(scope, receive)
        
        # Initialize state if not present
        if not hasattr(self, 'state'):
            self.state = State()
        
        # Initialize trace_id if not present
        if not hasattr(self.state, 'trace_id'):
            self.state.trace_id = str(uuid.uuid4())
        
        # Initialize user as None (auth placeholder)
        if not hasattr(self.state, 'user'):
            self.state.user = None
    
    async def json(self) -> Any:
        """
        Parse the request body as JSON.
        
        Returns:
            The parsed JSON data.
        """
        return await super().json()
    
    async def text_body(self) -> str:
        """
        Read the request body as text.
        
        Returns:
            The request body as text.
        """
        body = await super().body()
        return body.decode('utf-8')


class Response(StarletteResponse):
    """
    Thin wrapper around Starlette Response with additional helpers.
    """
    
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
        background=None,
    ):
        """
        Initialize the Response.
        
        Args:
            content: The response content.
            status_code: The HTTP status code.
            headers: Optional response headers.
            media_type: The media type of the response.
            background: Background tasks to run after the response is sent.
        """
        # Handle JSON content automatically
        if isinstance(content, (dict, list)):
            content = json.dumps(content)
            if media_type is None:
                media_type = "application/json"
        
        super().__init__(content, status_code, headers, media_type, background)
    
    @classmethod
    def json(
        cls,
        content: Any,
        status_code: int = 200,
        headers: Optional[dict] = None,
        background=None,
    ) -> "Response":
        """
        Create a JSON response.
        
        Args:
            content: The JSON-serializable content.
            status_code: The HTTP status code.
            headers: Optional response headers.
            background: Background tasks to run after the response is sent.
            
        Returns:
            A Response instance with JSON content.
        """
        return cls(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type="application/json",
            background=background,
        )
    
    @classmethod
    def text(
        cls,
        content: str,
        status_code: int = 200,
        headers: Optional[dict] = None,
        background=None,
    ) -> "Response":
        """
        Create a text response.
        
        Args:
            content: The text content.
            status_code: The HTTP status code.
            headers: Optional response headers.
            background: Background tasks to run after the response is sent.
            
        Returns:
            A Response instance with text content.
        """
        return cls(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type="text/plain",
            background=background,
        )