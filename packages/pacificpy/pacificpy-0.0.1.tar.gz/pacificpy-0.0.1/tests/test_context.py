import pytest
from starlette.requests import Request
from starlette.datastructures import State

from pacificpy.core.context import RequestContext


def test_request_context_manager():
    """Test that request context manager works correctly."""
    # Create a mock request
    class MockRequest:
        def __init__(self):
            self.state = State()
            self.state.trace_id = "test-trace-id"
    
    request = MockRequest()
    settings = {"test": "settings"}
    
    # Initially context should be empty
    assert RequestContext.get_request() is None
    assert RequestContext.get_settings() is None
    assert RequestContext.get_trace_id() is None
    
    # Enter context
    with RequestContext(request, settings):
        # Inside context we should have access to request and settings
        assert RequestContext.get_request() is request
        assert RequestContext.get_settings() is settings
        assert RequestContext.get_trace_id() == "test-trace-id"
    
    # After exiting context, it should be empty again
    assert RequestContext.get_request() is None
    assert RequestContext.get_settings() is None
    assert RequestContext.get_trace_id() is None


def test_request_context_manager_without_settings():
    """Test that request context manager works without settings."""
    # Create a mock request
    class MockRequest:
        def __init__(self):
            self.state = State()
            self.state.trace_id = "test-trace-id"
    
    request = MockRequest()
    
    # Initially context should be empty
    assert RequestContext.get_request() is None
    assert RequestContext.get_settings() is None
    assert RequestContext.get_trace_id() is None
    
    # Enter context without settings
    with RequestContext(request):
        # Inside context we should have access to request
        assert RequestContext.get_request() is request
        assert RequestContext.get_settings() is None
        assert RequestContext.get_trace_id() == "test-trace-id"
    
    # After exiting context, it should be empty again
    assert RequestContext.get_request() is None
    assert RequestContext.get_settings() is None
    assert RequestContext.get_trace_id() is None


def test_request_context_manager_without_trace_id():
    """Test that request context manager works when trace_id is not available."""
    # Create a mock request without trace_id
    class MockRequest:
        def __init__(self):
            self.state = State()
    
    request = MockRequest()
    
    # Initially context should be empty
    assert RequestContext.get_request() is None
    assert RequestContext.get_settings() is None
    assert RequestContext.get_trace_id() is None
    
    # Enter context
    with RequestContext(request):
        # Inside context we should have access to request
        assert RequestContext.get_request() is request
        assert RequestContext.get_settings() is None
        assert RequestContext.get_trace_id() is None
    
    # After exiting context, it should be empty again
    assert RequestContext.get_request() is None
    assert RequestContext.get_settings() is None
    assert RequestContext.get_trace_id() is None


def test_nested_request_context():
    """Test that nested request contexts work correctly."""
    # Create mock requests
    class MockRequest:
        def __init__(self, trace_id):
            self.state = State()
            self.state.trace_id = trace_id
    
    request1 = MockRequest("trace-id-1")
    request2 = MockRequest("trace-id-2")
    
    # Enter first context
    with RequestContext(request1):
        assert RequestContext.get_request() is request1
        assert RequestContext.get_trace_id() == "trace-id-1"
        
        # Enter nested context
        with RequestContext(request2):
            assert RequestContext.get_request() is request2
            assert RequestContext.get_trace_id() == "trace-id-2"
        
        # Back to first context
        assert RequestContext.get_request() is request1
        assert RequestContext.get_trace_id() == "trace-id-1"
    
    # After exiting all contexts, it should be empty
    assert RequestContext.get_request() is None
    assert RequestContext.get_trace_id() is None