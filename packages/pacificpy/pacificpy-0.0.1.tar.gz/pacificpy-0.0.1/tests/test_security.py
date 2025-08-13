"""
Integration tests for security middleware chain.

This module contains tests for the security middleware chain,
including CORS, CSRF, CSP, and HSTS middleware in the correct order.
"""

import pytest
import secrets
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware

from pacificpy.security.cors import CORSMiddleware
from pacificpy.security.csrf import CSRFMiddleware
from pacificpy.security.csp import CSPMiddleware
from pacificpy.security.defaults import SecurityMiddleware
from pacificpy.security.headers import HeaderSanitizerMiddleware

# Test routes
async def homepage(request):
    """Test homepage route."""
    return HTMLResponse("<html><body><h1>Homepage</h1></body></html>")

async def api_endpoint(request):
    """Test API endpoint."""
    return JSONResponse({"message": "success"})

async def form_endpoint(request):
    """Test form endpoint."""
    if request.method == "POST":
        return JSONResponse({"message": "form submitted"})
    return HTMLResponse("""
    <html>
    <body>
        <form method="post">
            <input type="hidden" name="csrf_token" value="test">
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """)

# Test middleware chain
middleware = [
    Middleware(HeaderSanitizerMiddleware),
    Middleware(SecurityMiddleware),
    Middleware(CORSMiddleware, allow_origins=["https://example.com"]),
    Middleware(CSRFMiddleware, secret_key=secrets.token_urlsafe(32)),
    Middleware(CSPMiddleware),
]

# Test app
app = Starlette(
    routes=[
        Route("/", homepage),
        Route("/api", api_endpoint),
        Route("/form", form_endpoint, methods=["GET", "POST"]),
    ],
    middleware=middleware
)

# Test client
client = TestClient(app)

# Tests
def test_hsts_header():
    """Test that HSTS header is set correctly."""
    response = client.get("/", headers={"X-Forwarded-Proto": "https"})
    assert response.status_code == 200
    assert "strict-transport-security" in response.headers
    assert "max-age=31536000" in response.headers["strict-transport-security"]

def test_x_frame_options_header():
    """Test that X-Frame-Options header is set correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "x-frame-options" in response.headers
    assert response.headers["x-frame-options"] == "DENY"

def test_x_content_type_options_header():
    """Test that X-Content-Type-Options header is set correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "x-content-type-options" in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"

def test_csp_header():
    """Test that CSP header is set correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "content-security-policy" in response.headers

def test_csrf_protection_safe_method():
    """Test CSRF protection for safe methods (GET)."""
    response = client.get("/form")
    assert response.status_code == 200
    # Should set CSRF cookie
    assert "set-cookie" in response.headers
    assert "csrftoken=" in response.headers["set-cookie"]

def test_csrf_protection_unsafe_method():
    """Test CSRF protection for unsafe methods (POST)."""
    # First, get the CSRF token
    response = client.get("/form")
    assert response.status_code == 200
    
    # Extract CSRF token from cookies
    cookies = response.cookies
    csrf_token = cookies.get("csrftoken")
    assert csrf_token is not None
    
    # Try to POST without CSRF header (should fail)
    response = client.post("/form")
    assert response.status_code == 403
    
    # POST with CSRF header (should succeed)
    response = client.post("/form", headers={"X-CSRFToken": csrf_token})
    assert response.status_code == 200

def test_cors_headers():
    """Test that CORS headers are set correctly."""
    response = client.get("/api", headers={"Origin": "https://example.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "https://example.com"

def test_header_sanitization():
    """Test that sensitive headers are removed."""
    response = client.get("/")
    assert response.status_code == 200
    # Check that sensitive headers are not present
    assert "server" not in response.headers
    assert "x-powered-by" not in response.headers

def test_middleware_order():
    """Test that middleware is applied in the correct order."""
    response = client.get("/", headers={"X-Forwarded-Proto": "https"})
    assert response.status_code == 200
    
    # Check that all security headers are present
    headers = response.headers
    assert "strict-transport-security" in headers
    assert "x-frame-options" in headers
    assert "x-content-type-options" in headers
    assert "content-security-policy" in headers
    assert "set-cookie" in headers  # CSRF cookie

def test_preflight_request():
    """Test CORS preflight request handling."""
    response = client.options("/api", headers={
        "Origin": "https://example.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers

def test_exempt_path():
    """Test that exempt paths work correctly."""
    # Create a new app with exempt paths
    exempt_middleware = [
        Middleware(HeaderSanitizerMiddleware),
        Middleware(SecurityMiddleware),
        Middleware(CORSMiddleware, allow_origins=["https://example.com"]),
        Middleware(CSRFMiddleware, secret_key=secrets.token_urlsafe(32), exempt_paths={"/health"}),
        Middleware(CSPMiddleware),
    ]
    
    exempt_app = Starlette(
        routes=[
            Route("/health", lambda r: JSONResponse({"status": "ok"})),
        ],
        middleware=exempt_middleware
    )
    
    exempt_client = TestClient(exempt_app)
    
    # Health endpoint should not require CSRF
    response = exempt_client.post("/health")
    assert response.status_code == 200