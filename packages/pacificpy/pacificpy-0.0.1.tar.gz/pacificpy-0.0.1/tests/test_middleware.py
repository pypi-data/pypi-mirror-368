import pytest
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from pacificpy.core.middleware import MiddlewareManager


class TestMiddleware1(BaseHTTPMiddleware):
    """Test middleware 1."""
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        return response


class TestMiddleware2(BaseHTTPMiddleware):
    """Test middleware 2."""
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        return response


class TestMiddleware3(BaseHTTPMiddleware):
    """Test middleware 3."""
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        return response


def test_middleware_manager_add_middleware():
    """Test that middleware manager can add middleware."""
    manager = MiddlewareManager()
    
    # Add middlewares with different priorities
    manager.add_middleware(TestMiddleware1, priority=100)
    manager.add_middleware(TestMiddleware2, priority=50)
    manager.add_middleware(TestMiddleware3, priority=200)
    
    # Get middlewares
    middlewares = manager.get_middlewares()
    
    # Check that we have 3 middlewares
    assert len(middlewares) == 3
    
    # Check that middlewares are instances of Middleware
    for middleware in middlewares:
        assert isinstance(middleware, Middleware)


def test_middleware_manager_priority_order():
    """Test that middleware manager respects priority order."""
    manager = MiddlewareManager()
    
    # Add middlewares with different priorities
    manager.add_middleware(TestMiddleware1, priority=100)  # Should be second
    manager.add_middleware(TestMiddleware2, priority=50)   # Should be first
    manager.add_middleware(TestMiddleware3, priority=200)  # Should be third
    
    # Get middlewares
    middlewares = manager.get_middlewares()
    
    # Check that middlewares are in correct order (priority 50, 100, 200)
    assert middlewares[0].cls == TestMiddleware2
    assert middlewares[1].cls == TestMiddleware1
    assert middlewares[2].cls == TestMiddleware3


def test_middleware_manager_condition():
    """Test that middleware manager respects conditions."""
    manager = MiddlewareManager()
    
    # Add middleware with condition that returns True
    manager.add_middleware(
        TestMiddleware1, 
        priority=100, 
        condition=lambda: True
    )
    
    # Add middleware with condition that returns False
    manager.add_middleware(
        TestMiddleware2, 
        priority=50, 
        condition=lambda: False
    )
    
    # Get middlewares
    middlewares = manager.get_middlewares()
    
    # Check that only one middleware was added (the one with True condition)
    assert len(middlewares) == 1
    assert middlewares[0].cls == TestMiddleware1


def test_middleware_manager_clear():
    """Test that middleware manager can clear middlewares."""
    manager = MiddlewareManager()
    
    # Add some middlewares
    manager.add_middleware(TestMiddleware1, priority=100)
    manager.add_middleware(TestMiddleware2, priority=50)
    
    # Check that we have 2 middlewares
    assert len(manager.get_middlewares()) == 2
    
    # Clear middlewares
    manager.clear()
    
    # Check that we have 0 middlewares
    assert len(manager.get_middlewares()) == 0


def test_middleware_manager_middleware_instance():
    """Test that middleware manager can handle Middleware instances."""
    manager = MiddlewareManager()
    
    # Add Middleware instance
    middleware_instance = Middleware(TestMiddleware1)
    manager.add_middleware(middleware_instance, priority=100)
    
    # Get middlewares
    middlewares = manager.get_middlewares()
    
    # Check that we have 1 middleware
    assert len(middlewares) == 1
    assert middlewares[0] == middleware_instance