"""
Cookie-based session backend for PacificPy.

This module provides a secure cookie-based session backend that
stores session data in encrypted cookies using the application's SECRET_KEY.
"""

import json
import time
from typing import Dict, Any
from starlette.requests import Request
from starlette.responses import Response
import itsdangerous

from .base import SessionBackend, Session

class CookieSessionBackend(SessionBackend):
    """Cookie-based session backend with encryption."""
    
    def __init__(
        self,
        secret_key: str,
        cookie_name: str = "session",
        max_age: int = 14 * 24 * 60 * 60,  # 14 days
        same_site: str = "lax",
        https_only: bool = True,
        domain: str = None,
    ):
        """
        Initialize the cookie session backend.
        
        Args:
            secret_key: The secret key for signing/encrypting cookies
            cookie_name: The name of the session cookie
            max_age: Maximum age of the cookie in seconds
            same_site: SameSite attribute for the cookie
            https_only: Whether the cookie should only be sent over HTTPS
            domain: Domain attribute for the cookie
        """
        self.secret_key = secret_key
        self.cookie_name = cookie_name
        self.max_age = max_age
        self.same_site = same_site
        self.https_only = https_only
        self.domain = domain
        
        # Create signer for cookie data
        self.signer = itsdangerous.TimestampSigner(secret_key)
        self.serializer = itsdangerous.URLSafeTimedSerializer(secret_key)
    
    async def load(self, request: Request) -> Dict[str, Any]:
        """
        Load session data from the cookie.
        
        Args:
            request: The incoming request
            
        Returns:
            A dictionary containing the session data
        """
        # Get session cookie
        session_cookie = request.cookies.get(self.cookie_name)
        
        # If no cookie, return empty session
        if not session_cookie:
            return {}
        
        try:
            # Decode and verify the cookie
            data = self.serializer.loads(session_cookie, max_age=self.max_age)
            
            # Ensure we have a dict
            if not isinstance(data, dict):
                return {}
            
            return data
        except (itsdangerous.BadSignature, itsdangerous.SignatureExpired):
            # If cookie is invalid or expired, return empty session
            return {}
        except Exception:
            # If any other error occurs, return empty session
            return {}
    
    async def save(self, response: Response, session: Dict[str, Any]) -> None:
        """
        Save session data to the cookie.
        
        Args:
            response: The response to attach session data to
            session: The session data to save
        """
        # If session is empty, don't set cookie
        if not session:
            return
        
        try:
            # Serialize and sign the session data
            session_data = self.serializer.dumps(session)
            
            # Create cookie attributes
            cookie_attrs = [
                f"{self.cookie_name}={session_data}",
                f"Max-Age={self.max_age}",
                "HttpOnly",  # Always set HttpOnly for security
                f"SameSite={self.same_site}",
            ]
            
            # Add secure flag if HTTPS only
            if self.https_only:
                cookie_attrs.append("Secure")
            
            # Add path
            cookie_attrs.append("Path=/")
            
            # Add domain if specified
            if self.domain:
                cookie_attrs.append(f"Domain={self.domain}")
            
            # Set the cookie
            cookie_value = "; ".join(cookie_attrs)
            
            # Add to response headers
            if "set-cookie" in response.headers:
                response.headers["set-cookie"] = f"{response.headers['set-cookie']}, {cookie_value}"
            else:
                response.headers["set-cookie"] = cookie_value
        except Exception:
            # If we can't save the session, continue without it
            pass
    
    async def clear(self, response: Response) -> None:
        """
        Clear session data from the cookie.
        
        Args:
            response: The response to clear session data from
        """
        # Create cookie with expiration in the past
        cookie_attrs = [
            f"{self.cookie_name}=",
            "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
            "Max-Age=0",
            "HttpOnly",
            f"SameSite={self.same_site}",
        ]
        
        # Add secure flag if HTTPS only
        if self.https_only:
            cookie_attrs.append("Secure")
        
        # Add path
        cookie_attrs.append("Path=/")
        
        # Add domain if specified
        if self.domain:
            cookie_attrs.append(f"Domain={self.domain}")
        
        # Set the cookie
        cookie_value = "; ".join(cookie_attrs)
        
        # Add to response headers
        if "set-cookie" in response.headers:
            response.headers["set-cookie"] = f"{response.headers['set-cookie']}, {cookie_value}"
        else:
            response.headers["set-cookie"] = cookie_value

# Session middleware
class SessionMiddleware:
    """ASGI middleware for session handling."""
    
    def __init__(self, app, backend: SessionBackend):
        """
        Initialize the session middleware.
        
        Args:
            app: The ASGI application
            backend: The session backend to use
        """
        self.app = app
        self.backend = backend
    
    async def __call__(self, scope, receive, send):
        """
        Process the request and handle sessions.
        
        Args:
            scope: The ASGI scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope)
        
        # Load session data
        session_data = await self.backend.load(request)
        session = Session(session_data)
        
        # Store session in request state
        scope["state"] = getattr(scope, "state", {})
        scope["state"]["session"] = session
        
        # Create a wrapper for the send function to save session
        async def send_with_session(message):
            if message["type"] == "http.response.start":
                # Save session if it was modified
                if session.modified:
                    await self.backend.save(Response(None), session.data)
                elif not session.data:
                    # Clear session if it's empty
                    await self.backend.clear(Response(None))
            
            await send(message)
        
        # Call the next middleware/app
        await self.app(scope, receive, send_with_session)