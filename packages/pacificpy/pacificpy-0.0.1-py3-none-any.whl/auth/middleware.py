"""
Authentication middleware for PacificPy.

This module provides middleware for extracting session/token data
and populating request.state.user with the current user.
"""

from typing import Optional, Dict, Any
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
from starlette.responses import Response
import jwt

class AuthMiddleware:
    """ASGI middleware for authentication."""
    
    def __init__(
        self,
        app: ASGIApp,
        secret_key: str = None,
        algorithm: str = "HS256",
        session_backend = None,
        exempt_paths: set = frozenset(),
        exempt_predicates: list = None,
    ):
        """
        Initialize the authentication middleware.
        
        Args:
            app: The ASGI application
            secret_key: Secret key for JWT verification
            algorithm: JWT algorithm
            session_backend: Session backend for session-based auth
            exempt_paths: Paths that are exempt from authentication
            exempt_predicates: Functions that determine if a request is exempt
        """
        self.app = app
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.session_backend = session_backend
        self.exempt_paths = exempt_paths
        self.exempt_predicates = exempt_predicates or []
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and handle authentication.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope)
        
        # Check if request is exempt
        if self._is_exempt(request):
            await self.app(scope, receive, send)
            return
        
        # Extract user from request
        user = await self._get_user(request)
        
        # Store user in request state
        scope["state"] = getattr(scope, "state", {})
        scope["state"]["user"] = user
        
        # Continue with the request
        await self.app(scope, receive, send)
    
    def _is_exempt(self, request: Request) -> bool:
        """
        Check if a request is exempt from authentication.
        
        Args:
            request: The request to check
            
        Returns:
            True if the request is exempt, False otherwise
        """
        # Check exempt paths
        if request.url.path in self.exempt_paths:
            return True
        
        # Check exempt predicates
        for predicate in self.exempt_predicates:
            if predicate(request):
                return True
        
        return False
    
    async def _get_user(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Extract user from request based on auth method.
        
        Args:
            request: The request
            
        Returns:
            User data or None if not authenticated
        """
        # Try to get user from Authorization header (JWT)
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            return await self._get_user_from_jwt(token)
        
        # Try to get user from session
        if self.session_backend:
            session_data = await self.session_backend.load(request)
            if session_data and "user" in session_data:
                return session_data["user"]
        
        # Try to get user from session cookie (if using CookieSessionBackend)
        session_cookie = request.cookies.get("session")
        if session_cookie and self.secret_key:
            try:
                # This is a simplified approach - in a real app, you'd use
                # the actual session backend to decode the cookie
                pass
            except Exception:
                pass
        
        # No user found
        return None
    
    async def _get_user_from_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user from JWT token.
        
        Args:
            token: The JWT token
            
        Returns:
            User data or None if token is invalid
        """
        if not self.secret_key:
            return None
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("user")
        except jwt.InvalidTokenError:
            # Invalid token
            return None
        except Exception:
            # Other error
            return None

# Helper functions
async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get the current user from request state.
    
    Args:
        request: The request
        
    Returns:
        User data or None if not authenticated
    """
    return getattr(request.state, "user", None)

async def get_current_user_id(request: Request) -> Optional[str]:
    """
    Get the current user ID from request state.
    
    Args:
        request: The request
        
    Returns:
        User ID or None if not authenticated
    """
    user = await get_current_user(request)
    if user:
        return user.get("id")
    return None

async def require_auth(request: Request) -> Dict[str, Any]:
    """
    Require authentication and return user data.
    
    Args:
        request: The request
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user is not authenticated
    """
    from ...errors.http import Unauthorized
    
    user = await get_current_user(request)
    if not user:
        raise Unauthorized("Authentication required")
    return user

# Default auth middleware
def default_auth_middleware(
    app: ASGIApp,
    secret_key: str = None,
    session_backend = None,
) -> AuthMiddleware:
    """
    Create an auth middleware with default settings.
    
    Args:
        app: The ASGI application
        secret_key: Secret key for JWT verification
        session_backend: Session backend for session-based auth
        
    Returns:
        An AuthMiddleware instance
    """
    return AuthMiddleware(
        app,
        secret_key=secret_key,
        session_backend=session_backend,
        exempt_paths={"/", "/health", "/login", "/auth"},
    )