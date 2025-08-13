"""
Remember-me / long-lived tokens for PacificPy.

This module provides support for long-lived tokens with
revocation lists stored in Redis.
"""

import secrets
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..errors.http import Unauthorized

# Try to import redis for revocation list storage
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class RememberMeManager:
    """Manager for remember-me / long-lived tokens."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        prefix: str = "remember_token:",
        ttl: int = 30 * 24 * 60 * 60,  # 30 days
    ):
        """
        Initialize the remember-me manager.
        
        Args:
            redis_url: The Redis connection URL
            prefix: Prefix for token keys in Redis
            ttl: Time-to-live for tokens in seconds
        """
        if not REDIS_AVAILABLE:
            raise RuntimeError("redis package is required for RememberMeManager")
        
        self.prefix = prefix
        self.ttl = ttl
        self.redis = redis.from_url(redis_url)
    
    def create_remember_token(self, user_id: str, user_data: Dict[str, Any] = None) -> str:
        """
        Create a remember-me token for a user.
        
        Args:
            user_id: The user ID
            user_data: Additional user data to store with the token
            
        Returns:
            The remember-me token
        """
        # Generate a secure random token
        token = secrets.token_urlsafe(32)
        
        # Create token data
        token_data = {
            "user_id": user_id,
            "created_at": time.time(),
        }
        
        # Add user data if provided
        if user_data:
            token_data.update(user_data)
        
        # Store token in Redis with TTL
        key = f"{self.prefix}{token}"
        self.redis.setex(key, self.ttl, str(token_data))
        
        return token
    
    def verify_remember_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a remember-me token.
        
        Args:
            token: The remember-me token to verify
            
        Returns:
            The token data
            
        Raises:
            Unauthorized: If the token is invalid or revoked
        """
        # Check if token is revoked
        if self.is_token_revoked(token):
            raise Unauthorized("Token has been revoked")
        
        # Get token data from Redis
        key = f"{self.prefix}{token}"
        token_data = self.redis.get(key)
        
        # Check if token exists
        if not token_data:
            raise Unauthorized("Invalid token")
        
        # Parse token data
        try:
            # In a real implementation, you'd use a proper serialization format
            # This is a simplified example
            return eval(token_data)
        except Exception:
            raise Unauthorized("Invalid token data")
    
    def revoke_token(self, token: str) -> None:
        """
        Revoke a remember-me token.
        
        Args:
            token: The token to revoke
        """
        # Add token to revocation list
        revoke_key = f"{self.prefix}revoked:{token}"
        self.redis.setex(revoke_key, self.ttl, "1")
        
        # Delete the token
        key = f"{self.prefix}{token}"
        self.redis.delete(key)
    
    def is_token_revoked(self, token: str) -> bool:
        """
        Check if a token has been revoked.
        
        Args:
            token: The token to check
            
        Returns:
            True if the token is revoked, False otherwise
        """
        revoke_key = f"{self.prefix}revoked:{token}"
        return self.redis.exists(revoke_key) > 0
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens from Redis.
        
        Returns:
            The number of tokens cleaned up
        """
        # This is handled automatically by Redis TTL
        # but we can implement additional cleanup logic here if needed
        return 0

# Global remember-me manager
_remember_manager: Optional[RememberMeManager] = None

def configure_remember_me(
    redis_url: str = "redis://localhost:6379/0",
    prefix: str = "remember_token:",
    ttl: int = 30 * 24 * 60 * 60,  # 30 days
) -> RememberMeManager:
    """
    Configure the global remember-me manager.
    
    Args:
        redis_url: The Redis connection URL
        prefix: Prefix for token keys in Redis
        ttl: Time-to-live for tokens in seconds
        
    Returns:
        The remember-me manager instance
    """
    global _remember_manager
    _remember_manager = RememberMeManager(
        redis_url=redis_url,
        prefix=prefix,
        ttl=ttl,
    )
    return _remember_manager

def create_remember_token(user_id: str, user_data: Dict[str, Any] = None) -> str:
    """
    Create a remember-me token using the global manager.
    
    Args:
        user_id: The user ID
        user_data: Additional user data to store with the token
        
    Returns:
        The remember-me token
        
    Raises:
        RuntimeError: If remember-me manager is not configured
    """
    if not _remember_manager:
        raise RuntimeError("Remember-me manager not configured")
    
    return _remember_manager.create_remember_token(user_id, user_data)

def verify_remember_token(token: str) -> Dict[str, Any]:
    """
    Verify a remember-me token using the global manager.
    
    Args:
        token: The remember-me token to verify
        
    Returns:
        The token data
        
    Raises:
        Unauthorized: If the token is invalid or revoked
        RuntimeError: If remember-me manager is not configured
    """
    if not _remember_manager:
        raise RuntimeError("Remember-me manager not configured")
    
    return _remember_manager.verify_remember_token(token)

def revoke_token(token: str) -> None:
    """
    Revoke a remember-me token using the global manager.
    
    Args:
        token: The token to revoke
        
    Raises:
        RuntimeError: If remember-me manager is not configured
    """
    if not _remember_manager:
        raise RuntimeError("Remember-me manager not configured")
    
    _remember_manager.revoke_token(token)