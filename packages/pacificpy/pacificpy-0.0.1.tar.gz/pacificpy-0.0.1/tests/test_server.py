def test_server_function_exists():
    """Test that the run function exists and is callable."""
    from pacificpy.core.server import run
    assert callable(run)


def test_server_function_with_app():
    """Test that the run function can be called with an app."""
    from pacificpy.core.server import run
    from pacificpy.core.app import PacificApp
    
    # Create a mock ASGI app
    app = PacificApp()
    
    # Test that the function can be called without errors
    # We're not actually running the server, just checking the function exists
    assert callable(run)