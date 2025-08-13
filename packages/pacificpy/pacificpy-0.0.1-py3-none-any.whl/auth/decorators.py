"""
Authentication decorators for PacificPy.

This module provides decorators for protecting endpoints with
authentication and role-based access control.
"""

from typing import Callable, List, Union
from functools import wraps
from starlette.requests import Request
from ..errors.http import Unauthorized, Forbidden
from .middleware import get_current_user

def requires_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for an endpoint.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Get current user
        user = await get_current_user(request)
        
        # Check if user is authenticated
        if not user:
            raise Unauthorized("Authentication required")
        
        # Add user to kwargs for access in the handler
        kwargs["current_user"] = user
        
        # Call the original function
        return await func(request, *args, **kwargs)
    
    return wrapper

def requires_roles(
    roles: Union[str, List[str]],
    require_all: bool = False
) -> Callable:
    """
    Decorator to require specific roles for an endpoint.
    
    Args:
        roles: Required role(s)
        require_all: Whether all roles are required (True) or any role (False)
        
    Returns:
        The decorator function
    """
    # Normalize roles to a list
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get current user
            user = await get_current_user(request)
            
            # Check if user is authenticated
            if not user:
                raise Unauthorized("Authentication required")
            
            # Get user roles
            user_roles = user.get("roles", [])
            
            # Check if user has required roles
            if require_all:
                # All roles required
                if not all(role in user_roles for role in roles):
                    raise Forbidden("Insufficient permissions")
            else:
                # Any role required
                if not any(role in user_roles for role in roles):
                    raise Forbidden("Insufficient permissions")
            
            # Add user to kwargs for access in the handler
            kwargs["current_user"] = user
            
            # Call the original function
            return await func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator

def requires_permission(
    permissions: Union[str, List[str]],
    require_all: bool = False
) -> Callable:
    """
    Decorator to require specific permissions for an endpoint.
    
    Args:
        permissions: Required permission(s)
        require_all: Whether all permissions are required (True) or any permission (False)
        
    Returns:
        The decorator function
    """
    # Normalize permissions to a list
    if isinstance(permissions, str):
        permissions = [permissions]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get current user
            user = await get_current_user(request)
            
            # Check if user is authenticated
            if not user:
                raise Unauthorized("Authentication required")
            
            # Get user permissions
            user_permissions = user.get("permissions", [])
            
            # Check if user has required permissions
            if require_all:
                # All permissions required
                if not all(perm in user_permissions for perm in permissions):
                    raise Forbidden("Insufficient permissions")
            else:
                # Any permission required
                if not any(perm in user_permissions for perm in permissions):
                    raise Forbidden("Insufficient permissions")
            
            # Add user to kwargs for access in the handler
            kwargs["current_user"] = user
            
            # Call the original function
            return await func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator

# Convenience aliases
login_required = requires_auth
role_required = requires_roles
permission_required = requires_permission