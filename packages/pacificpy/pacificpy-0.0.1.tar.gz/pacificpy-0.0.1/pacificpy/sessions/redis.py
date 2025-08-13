"""
Redis-based session backend for PacificPy.

This module provides a Redis-based session backend with TTL support
and connection pooling for stateless scaling.
"""

import json
import uuid
from typing import Dict, Any, Optional
from starlette.requests import Request
from starlette.responses import Response

# Try to import aioredis for async support
try:
    import aioredis
    AIREDIS_AVAILABLE = True
except ImportError:
    AIREDIS_AVAILABLE = False

# Try to import redis for sync support
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .base import SessionBackend

class RedisSessionBackend(SessionBackend):
    """Redis-based session backend with TTL support."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        prefix: str = "session:",
        ttl: int = 14 * 24 * 60 * 60,  # 14 days
        cookie_name: str = "session_id",
        https_only: bool = True,
        same_site: str = "lax",
        domain: str = None,
    ):
        """
        Initialize the Redis session backend.
        
        Args:
            redis_url: The Redis connection URL
            prefix: Prefix for session keys in Redis
            ttl: Time-to-live for sessions in seconds
            cookie_name: The name of the session ID cookie
            https_only: Whether the cookie should only be sent over HTTPS
            same_site: SameSite attribute for the cookie
            domain: Domain attribute for the cookie
        """
        self.redis_url = redis_url
        self.prefix = prefix
        self.ttl = ttl
        self.cookie_name = cookie_name
        self.https_only = https_only
        self.same_site = same_site
        self.domain = domain
        
        # Initialize Redis connection
        if AIREDIS_AVAILABLE:
            self.redis = aioredis.from_url(redis_url)
        elif REDIS_AVAILABLE:
            self.redis = redis.from_url(redis_url)
        else:
            raise RuntimeError("Either aioredis or redis package is required for RedisSessionBackend")
    
    async def load(self, request: Request) -> Dict[str, Any]:
        """
        Load session data from Redis.
        
        Args:
            request: The incoming request
            
        Returns:
            A dictionary containing the session data
        """
        # Get session ID from cookie
        session_id = request.cookies.get(self.cookie_name)
        
        # If no session ID, return empty session
        if not session_id:
            return {}
        
        try:
            # Get session data from Redis
            key = f"{self.prefix}{session_id}"
            
            if AIREDIS_AVAILABLE and hasattr(self.redis, 'get'):
                # Async version
                session_data = await self.redis.get(key)
            elif REDIS_AVAILABLE:
                # Sync version
                session_data = self.redis.get(key)
            else:
                return {}
            
            # If no data, return empty session
            if not session_data:
                return {}
            
            # Parse session data
            return json.loads(session_data)
        except Exception:
            # If any error occurs, return empty session
            return {}
    
    async def save(self, response: Response, session: Dict[str, Any]) -> None:
        """
        Save session data to Redis.
        
        Args:
            response: The response to attach session ID cookie to
            session: The session data to save
        """
        # Generate session ID if not already set
        session_id = response.cookies.get(self.cookie_name)
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Save session data to Redis
            key = f"{self.prefix}{session_id}"
            session_data = json.dumps(session)
            
            if AIREDIS_AVAILABLE and hasattr(self.redis, 'setex'):
                # Async version
                await self.redis.setex(key, self.ttl, session_data)
            elif REDIS_AVAILABLE:
                # Sync version
                self.redis.setex(key, self.ttl, session_data)
            
            # Set session ID cookie
            cookie_attrs = [
                f"{self.cookie_name}={session_id}",
                f"Max-Age={self.ttl}",
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
        except Exception:
            # If we can't save the session, continue without it
            pass
    
    async def clear(self, response: Response) -> None:
        """
        Clear session data from Redis.
        
        Args:
            response: The response to clear session ID cookie from
        """
        # Get session ID from cookie
        session_id = response.cookies.get(self.cookie_name)
        
        # If no session ID, nothing to clear
        if not session_id:
            return
        
        try:
            # Delete session data from Redis
            key = f"{self.prefix}{session_id}"
            
            if AIREDIS_AVAILABLE and hasattr(self.redis, 'delete'):
                # Async version
                await self.redis.delete(key)
            elif REDIS_AVAILABLE:
                # Sync version
                self.redis.delete(key)
            
            # Clear session ID cookie
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
        except Exception:
            # If we can't clear the session, continue
            pass

# Sync version for compatibility
class SyncRedisSessionBackend(SessionBackend):
    """Synchronous Redis-based session backend."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        prefix: str = "session:",
        ttl: int = 14 * 24 * 60 * 60,  # 14 days
        cookie_name: str = "session_id",
        https_only: bool = True,
        same_site: str = "lax",
        domain: str = None,
    ):
        """
        Initialize the synchronous Redis session backend.
        
        Args:
            redis_url: The Redis connection URL
            prefix: Prefix for session keys in Redis
            ttl: Time-to-live for sessions in seconds
            cookie_name: The name of the session ID cookie
            https_only: Whether the cookie should only be sent over HTTPS
            same_site: SameSite attribute for the cookie
            domain: Domain attribute for the cookie
        """
        if not REDIS_AVAILABLE:
            raise RuntimeError("redis package is required for SyncRedisSessionBackend")
        
        self.redis_url = redis_url
        self.prefix = prefix
        self.ttl = ttl
        self.cookie_name = cookie_name
        self.https_only = https_only
        self.same_site = same_site
        self.domain = domain
        
        # Initialize Redis connection
        self.redis = redis.from_url(redis_url)
    
    async def load(self, request: Request) -> Dict[str, Any]:
        """Load session data from Redis (sync version)."""
        # Get session ID from cookie
        session_id = request.cookies.get(self.cookie_name)
        
        # If no session ID, return empty session
        if not session_id:
            return {}
        
        try:
            # Get session data from Redis
            key = f"{self.prefix}{session_id}"
            session_data = self.redis.get(key)
            
            # If no data, return empty session
            if not session_data:
                return {}
            
            # Parse session data
            return json.loads(session_data)
        except Exception:
            # If any error occurs, return empty session
            return {}
    
    async def save(self, response: Response, session: Dict[str, Any]) -> None:
        """Save session data to Redis (sync version)."""
        # Generate session ID if not already set
        session_id = response.cookies.get(self.cookie_name)
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Save session data to Redis
            key = f"{self.prefix}{session_id}"
            session_data = json.dumps(session)
            self.redis.setex(key, self.ttl, session_data)
            
            # Set session ID cookie
            cookie_attrs = [
                f"{self.cookie_name}={session_id}",
                f"Max-Age={self.ttl}",
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
        except Exception:
            # If we can't save the session, continue without it
            pass
    
    async def clear(self, response: Response) -> None:
        """Clear session data from Redis (sync version)."""
        # Get session ID from cookie
        session_id = response.cookies.get(self.cookie_name)
        
        # If no session ID, nothing to clear
        if not session_id:
            return
        
        try:
            # Delete session data from Redis
            key = f"{self.prefix}{session_id}"
            self.redis.delete(key)
            
            # Clear session ID cookie
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
        except Exception:
            # If we can't clear the session, continue
            pass