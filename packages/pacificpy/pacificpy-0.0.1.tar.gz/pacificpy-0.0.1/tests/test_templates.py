"""
Tests for template rendering and static file serving in PacificPy.

This module contains tests for template rendering, filters,
static file headers, and ETag behavior.
"""

import os
import tempfile
import time
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.middleware import Middleware
import jinja2

from pacificpy.templates.engine import TemplateEngine, configure_templates
from pacificpy.templates.filters import register_filters
from pacificpy.templates.static import StaticFilesMiddleware

# Test templates
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Test App{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
"""

INDEX_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Home - Test App{% endblock %}
{% block content %}
<h1>Hello, {{ name }}!</h1>
<p>Current time: {{ now | format_date }}</p>
<p>JSON data: {{ data | safe_json }}</p>
{% endblock %}
"""

# Test data
TEST_DATA = {
    "name": "World",
    "now": "2023-01-01T12:00:00",
    "data": {"key": "value", "number": 42}
}

# Test routes
async def homepage(request):
    """Test homepage route."""
    template_engine = request.app.state.template_engine
    return template_engine.render_response("index.html", TEST_DATA, request)

# Create a temporary directory for templates
template_dir = tempfile.mkdtemp()

# Write test templates to temporary directory
with open(os.path.join(template_dir, "base.html"), "w") as f:
    f.write(BASE_TEMPLATE)

with open(os.path.join(template_dir, "index.html"), "w") as f:
    f.write(INDEX_TEMPLATE)

# Configure template engine
template_engine = TemplateEngine(template_dir=template_dir)
register_filters(template_engine.env)

# Add template engine to app state
app = Starlette(
    routes=[
        Route("/", homepage),
    ]
)
app.state.template_engine = template_engine

# Test client
client = TestClient(app)

# Template rendering tests
def test_template_rendering():
    """Test basic template rendering."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Hello, World!" in response.text
    assert "Home - Test App" in response.text
    assert "2023-01-01" in response.text

def test_template_inheritance():
    """Test template inheritance."""
    response = client.get("/")
    assert response.status_code == 200
    # Check that base template content is included
    assert "<!DOCTYPE html>" in response.text
    assert "<html>" in response.text
    assert "</html>" in response.text

def test_template_filters():
    """Test template filters."""
    response = client.get("/")
    assert response.status_code == 200
    # Check that format_date filter worked
    assert "2023-01-01" in response.text
    # Check that safe_json filter worked
    assert '{"key": "value", "number": 42}' in response.text

def test_template_context():
    """Test template context variables."""
    response = client.get("/")
    assert response.status_code == 200
    # Check that context variables are rendered
    assert "World" in response.text

# Static files tests
def test_static_files_setup():
    """Test static files middleware setup."""
    # Create a temporary directory for static files
    static_dir = tempfile.mkdtemp()
    
    # Create a test static file
    test_file_path = os.path.join(static_dir, "test.css")
    with open(test_file_path, "w") as f:
        f.write("body { color: red; }")
    
    # Create app with static files middleware
    static_app = Starlette(
        routes=[],
        middleware=[
            Middleware(StaticFilesMiddleware, static_dir=static_dir)
        ]
    )
    
    static_client = TestClient(static_app)
    
    # Test serving static file
    response = static_client.get("/static/test.css")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/css"
    assert "body { color: red; }" in response.text

def test_static_files_cache_headers():
    """Test static files cache headers."""
    # Create a temporary directory for static files
    static_dir = tempfile.mkdtemp()
    
    # Create a test static file
    test_file_path = os.path.join(static_dir, "test.js")
    with open(test_file_path, "w") as f:
        f.write("console.log('test');")
    
    # Create app with static files middleware
    static_app = Starlette(
        routes=[],
        middleware=[
            Middleware(StaticFilesMiddleware, static_dir=static_dir, cache_max_age=3600)
        ]
    )
    
    static_client = TestClient(static_app)
    
    # Test serving static file with cache headers
    response = static_client.get("/static/test.js")
    assert response.status_code == 200
    assert "cache-control" in response.headers
    assert "max-age=3600" in response.headers["cache-control"]

def test_static_files_etag():
    """Test static files ETag generation."""
    # Create a temporary directory for static files
    static_dir = tempfile.mkdtemp()
    
    # Create a test static file
    test_file_path = os.path.join(static_dir, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Hello, World!")
    
    # Create app with static files middleware
    static_app = Starlette(
        routes=[],
        middleware=[
            Middleware(StaticFilesMiddleware, static_dir=static_dir, etag_enabled=True)
        ]
    )
    
    static_client = TestClient(static_app)
    
    # Test serving static file with ETag
    response = static_client.get("/static/test.txt")
    assert response.status_code == 200
    assert "etag" in response.headers
    
    # Get the ETag
    etag = response.headers["etag"]
    
    # Test If-None-Match with correct ETag (should return 304)
    response = static_client.get("/static/test.txt", headers={"if-none-match": etag})
    assert response.status_code == 304

def test_static_files_last_modified():
    """Test static files Last-Modified header."""
    # Create a temporary directory for static files
    static_dir = tempfile.mkdtemp()
    
    # Create a test static file
    test_file_path = os.path.join(static_dir, "test.html")
    with open(test_file_path, "w") as f:
        f.write("<html><body>Test</body></html>")
    
    # Get file modification time
    mtime = os.path.getmtime(test_file_path)
    last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(mtime))
    
    # Create app with static files middleware
    static_app = Starlette(
        routes=[],
        middleware=[
            Middleware(StaticFilesMiddleware, static_dir=static_dir)
        ]
    )
    
    static_client = TestClient(static_app)
    
    # Test serving static file with Last-Modified header
    response = static_client.get("/static/test.html")
    assert response.status_code == 200
    assert "last-modified" in response.headers
    assert response.headers["last-modified"] == last_modified

def test_static_files_404():
    """Test static files 404 handling."""
    # Create a temporary directory for static files
    static_dir = tempfile.mkdtemp()
    
    # Create app with static files middleware
    static_app = Starlette(
        routes=[],
        middleware=[
            Middleware(StaticFilesMiddleware, static_dir=static_dir)
        ]
    )
    
    static_client = TestClient(static_app)
    
    # Test requesting non-existent static file
    response = static_client.get("/static/nonexistent.css")
    assert response.status_code == 404

def test_static_files_security():
    """Test static files security (directory traversal prevention)."""
    # Create a temporary directory for static files
    static_dir = tempfile.mkdtemp()
    
    # Create app with static files middleware
    static_app = Starlette(
        routes=[],
        middleware=[
            Middleware(StaticFilesMiddleware, static_dir=static_dir)
        ]
    )
    
    static_client = TestClient(static_app)
    
    # Test directory traversal attempt
    response = static_client.get("/static/../etc/passwd")
    assert response.status_code == 403

# Additional template tests
def test_template_engine_configuration():
    """Test template engine configuration."""
    # Configure template engine
    engine = configure_templates(template_dir=template_dir)
    assert engine is not None
    assert engine.template_dir == template_dir

def test_template_filters_registration():
    """Test template filters registration."""
    # Create a new environment
    env = jinja2.Environment()
    
    # Register filters
    register_filters(env)
    
    # Check that filters are registered
    assert "format_date" in env.filters
    assert "safe_json" in env.filters
    assert "escape_js" in env.filters

def test_template_render_response():
    """Test template render response."""
    # Create a simple template
    template_content = "<h1>Hello, {{ name }}!</h1>"
    
    # Create template engine
    engine = TemplateEngine(template_dir=template_dir)
    
    # Add template as string (for testing)
    engine.env.loader = jinja2.DictLoader({"test.html": template_content})
    
    # Render response
    response = engine.render_response("test.html", {"name": "Test User"})
    assert isinstance(response, HTMLResponse)
    assert response.status_code == 200
    assert "Hello, Test User!" in response.body.decode()

# Cleanup
def test_cleanup():
    """Clean up temporary directories."""
    # Clean up is handled by the OS for temporary directories
    pass