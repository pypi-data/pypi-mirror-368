"""
Test factories for generating Pydantic models.

This module provides factory classes for creating test data models
such as users and authentication tokens.
"""

import random
import string
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

# Base models for testing
class User(BaseModel):
    """Test user model."""
    id: int
    username: str
    email: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuthToken(BaseModel):
    """Test authentication token model."""
    token: str
    user_id: int
    expires_at: datetime
    scopes: list[str] = []

# Factory classes
class UserFactory:
    """Factory for creating test User instances."""
    
    @staticmethod
    def create(
        id: Optional[int] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        is_active: bool = True
    ) -> User:
        """Create a test User instance."""
        return User(
            id=id or random.randint(1, 1000000),
            username=username or f"user_{random.randint(1, 1000000)}",
            email=email or f"user_{random.randint(1, 1000000)}@example.com",
            is_active=is_active
        )
    
    @staticmethod
    def create_batch(count: int, **kwargs) -> list[User]:
        """Create a batch of test User instances."""
        return [UserFactory.create(**kwargs) for _ in range(count)]

class AuthTokenFactory:
    """Factory for creating test AuthToken instances."""
    
    @staticmethod
    def create(
        token: Optional[str] = None,
        user_id: Optional[int] = None,
        expires_at: Optional[datetime] = None,
        scopes: Optional[list[str]] = None
    ) -> AuthToken:
        """Create a test AuthToken instance."""
        return AuthToken(
            token=token or ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            user_id=user_id or random.randint(1, 1000000),
            expires_at=expires_at or (datetime.utcnow() + timedelta(hours=1)),
            scopes=scopes or []
        )
    
    @staticmethod
    def create_batch(count: int, **kwargs) -> list[AuthToken]:
        """Create a batch of test AuthToken instances."""
        return [AuthTokenFactory.create(**kwargs) for _ in range(count)]

# Convenience functions
def create_user(**kwargs) -> User:
    """Create a test User instance."""
    return UserFactory.create(**kwargs)

def create_auth_token(**kwargs) -> AuthToken:
    """Create a test AuthToken instance."""
    return AuthTokenFactory.create(**kwargs)