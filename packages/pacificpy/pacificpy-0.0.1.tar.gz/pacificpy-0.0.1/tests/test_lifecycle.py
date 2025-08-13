import pytest
import asyncio
from pacificpy.core.app import PacificApp


# Global variables to track if handlers were called
startup_called = False
shutdown_called = False
async_startup_called = False
async_shutdown_called = False


def sync_startup_handler():
    """Synchronous startup handler."""
    global startup_called
    startup_called = True


def sync_shutdown_handler():
    """Synchronous shutdown handler."""
    global shutdown_called
    shutdown_called = True


async def async_startup_handler():
    """Asynchronous startup handler."""
    global async_startup_called
    async_startup_called = True


async def async_shutdown_handler():
    """Asynchronous shutdown handler."""
    global async_shutdown_called
    async_shutdown_called = True


def test_lifecycle_sync_handlers():
    """Test that synchronous lifecycle handlers are registered and called."""
    global startup_called, shutdown_called
    
    # Reset global variables
    startup_called = False
    shutdown_called = False
    
    # Create app and register handlers
    app = PacificApp()
    app.on_startup(sync_startup_handler)
    app.on_shutdown(sync_shutdown_handler)
    
    # Check that handlers are registered
    assert len(app.lifecycle._startup_handlers) == 1
    assert len(app.lifecycle._shutdown_handlers) == 1
    
    # Run startup handlers
    asyncio.run(app.lifecycle.run_startup_handlers())
    assert startup_called is True
    
    # Run shutdown handlers
    asyncio.run(app.lifecycle.run_shutdown_handlers())
    assert shutdown_called is True


@pytest.mark.asyncio
async def test_lifecycle_async_handlers():
    """Test that asynchronous lifecycle handlers are registered and called."""
    global async_startup_called, async_shutdown_called
    
    # Reset global variables
    async_startup_called = False
    async_shutdown_called = False
    
    # Create app and register handlers
    app = PacificApp()
    app.on_startup(async_startup_handler)
    app.on_shutdown(async_shutdown_handler)
    
    # Check that handlers are registered
    assert len(app.lifecycle._startup_handlers) == 1
    assert len(app.lifecycle._shutdown_handlers) == 1
    
    # Run startup handlers
    await app.lifecycle.run_startup_handlers()
    assert async_startup_called is True
    
    # Run shutdown handlers
    await app.lifecycle.run_shutdown_handlers()
    assert async_shutdown_called is True


def test_lifecycle_decorator_usage():
    """Test that lifecycle decorators work correctly."""
    called = False
    
    # Create app
    app = PacificApp()
    
    # Register handler using decorator
    @app.on_startup
    def decorated_startup_handler():
        nonlocal called
        called = True
    
    # Check that handler is registered
    assert len(app.lifecycle._startup_handlers) == 1
    assert app.lifecycle._startup_handlers[0] == decorated_startup_handler
    
    # Run startup handlers
    asyncio.run(app.lifecycle.run_startup_handlers())
    assert called is True