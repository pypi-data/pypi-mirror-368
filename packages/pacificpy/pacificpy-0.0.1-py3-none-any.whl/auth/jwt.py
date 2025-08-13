"""
JWT helpers for PacificPy.

This module provides utilities for creating and verifying JWT tokens
with secure defaults and support for key rotation.
"""

import jwt
import time
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from ..errors.http import Unauthorized

class JWTManager:
    """Manager for JWT token creation and verification."""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        expires_in: int = 3600,  # 1 hour
        issuer: str = None,
        audience: str = None,
    ):
        """
        Initialize the JWT manager.
        
        Args:
            secret_key: The secret key for signing tokens
            algorithm: The algorithm to use for signing
            expires_in: Default expiration time in seconds
            issuer: The issuer claim
            audience: The audience claim
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expires_in = expires_in
        self.issuer = issuer
        self.audience = audience
        self._key_rotation_callbacks = []
    
    def create_access_token(
        self,
        payload: Dict[str, Any],
        expires_in: int = None,
        issuer: str = None,
        audience: str = None,
    ) -> str:
        """
        Create an access token.
        
        Args:
            payload: The payload to include in the token
            expires_in: Expiration time in seconds (overrides default)
            issuer: The issuer claim (overrides default)
            audience: The audience claim (overrides default)
            
        Returns:
            The JWT token
        """
        # Set expiration time
        exp = datetime.utcnow() + timedelta(seconds=expires_in or self.expires_in)
        
        # Create token payload
        token_payload = {
            "exp": exp,
            "iat": datetime.utcnow(),
        }
        
        # Add issuer if specified
        if issuer or self.issuer:
            token_payload["iss"] = issuer or self.issuer
        
        # Add audience if specified
        if audience or self.audience:
            token_payload["aud"] = audience or self.audience
        
        # Add custom payload
        token_payload.update(payload)
        
        # Create and sign token
        token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(
        self,
        token: str,
        issuer: str = None,
        audience: str = None,
    ) -> Dict[str, Any]:
        """
        Verify a token and return its payload.
        
        Args:
            token: The JWT token to verify
            issuer: The expected issuer claim
            audience: The expected audience claim
            
        Returns:
            The token payload
            
        Raises:
            Unauthorized: If the token is invalid or expired
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=issuer or self.issuer,
                audience=audience or self.audience,
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise Unauthorized("Token has expired")
        except jwt.InvalidTokenError:
            raise Unauthorized("Invalid token")
        except Exception:
            raise Unauthorized("Token verification failed")
    
    def refresh_token(
        self,
        token: str,
        expires_in: int = None,
        issuer: str = None,
        audience: str = None,
    ) -> str:
        """
        Refresh a token, creating a new one with updated expiration.
        
        Args:
            token: The token to refresh
            expires_in: New expiration time in seconds
            issuer: The issuer claim
            audience: The audience claim
            
        Returns:
            A new JWT token
        """
        # Verify the existing token
        payload = self.verify_token(token, issuer, audience)
        
        # Remove claims that should not be carried over
        refresh_payload = {
            k: v for k, v in payload.items()
            if k not in ["exp", "iat", "iss", "aud"]
        }
        
        # Create new token with refreshed expiration
        return self.create_access_token(
            refresh_payload,
            expires_in=expires_in,
            issuer=issuer,
            audience=audience,
        )
    
    def add_key_rotation_callback(self, callback: callable) -> None:
        """
        Add a callback for key rotation events.
        
        Args:
            callback: The callback function
        """
        self._key_rotation_callbacks.append(callback)
    
    def rotate_key(self, new_secret_key: str) -> None:
        """
        Rotate the secret key.
        
        Args:
            new_secret_key: The new secret key
        """
        old_secret_key = self.secret_key
        self.secret_key = new_secret_key
        
        # Notify callbacks
        for callback in self._key_rotation_callbacks:
            try:
                callback(old_secret_key, new_secret_key)
            except Exception:
                # Don't let callback errors break key rotation
                pass

# Global JWT manager
_jwt_manager: Optional[JWTManager] = None

def configure_jwt(
    secret_key: str,
    algorithm: str = "HS256",
    expires_in: int = 3600,
    issuer: str = None,
    audience: str = None,
) -> JWTManager:
    """
    Configure the global JWT manager.
    
    Args:
        secret_key: The secret key for signing tokens
        algorithm: The algorithm to use for signing
        expires_in: Default expiration time in seconds
        issuer: The issuer claim
        audience: The audience claim
        
    Returns:
        The JWT manager instance
    """
    global _jwt_manager
    _jwt_manager = JWTManager(
        secret_key=secret_key,
        algorithm=algorithm,
        expires_in=expires_in,
        issuer=issuer,
        audience=audience,
    )
    return _jwt_manager

def create_access_token(
    payload: Dict[str, Any],
    expires_in: int = None,
    issuer: str = None,
    audience: str = None,
) -> str:
    """
    Create an access token using the global JWT manager.
    
    Args:
        payload: The payload to include in the token
        expires_in: Expiration time in seconds (overrides default)
        issuer: The issuer claim
        audience: The audience claim
        
    Returns:
        The JWT token
        
    Raises:
        RuntimeError: If JWT manager is not configured
    """
    if not _jwt_manager:
        raise RuntimeError("JWT manager not configured")
    
    return _jwt_manager.create_access_token(
        payload,
        expires_in=expires_in,
        issuer=issuer,
        audience=audience,
    )

def verify_token(
    token: str,
    issuer: str = None,
    audience: str = None,
) -> Dict[str, Any]:
    """
    Verify a token using the global JWT manager.
    
    Args:
        token: The JWT token to verify
        issuer: The expected issuer claim
        audience: The expected audience claim
        
    Returns:
        The token payload
        
    Raises:
        Unauthorized: If the token is invalid or expired
        RuntimeError: If JWT manager is not configured
    """
    if not _jwt_manager:
        raise RuntimeError("JWT manager not configured")
    
    return _jwt_manager.verify_token(
        token,
        issuer=issuer,
        audience=audience,
    )

def refresh_token(
    token: str,
    expires_in: int = None,
    issuer: str = None,
    audience: str = None,
) -> str:
    """
    Refresh a token using the global JWT manager.
    
    Args:
        token: The token to refresh
        expires_in: New expiration time in seconds
        issuer: The issuer claim
        audience: The audience claim
        
    Returns:
        A new JWT token
        
    Raises:
        Unauthorized: If the token is invalid or expired
        RuntimeError: If JWT manager is not configured
    """
    if not _jwt_manager:
        raise RuntimeError("JWT manager not configured")
    
    return _jwt_manager.refresh_token(
        token,
        expires_in=expires_in,
        issuer=issuer,
        audience=audience,
    )

# Helper for getting token from request
def get_token_from_request(request) -> Optional[str]:
    """
    Extract JWT token from request Authorization header.
    
    Args:
        request: The request object
        
    Returns:
        The JWT token or None if not found
    """
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]  # Remove "Bearer " prefix
    return None