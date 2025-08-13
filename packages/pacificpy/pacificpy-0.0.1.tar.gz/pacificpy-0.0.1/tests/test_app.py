import pytest
from starlette.routing import Route, Router
from starlette.responses import JSONResponse

from pacificpy.core.app import PacificApp


def ping_handler(request):
    return JSONResponse({"message": "pong"})


def test_pacific_app_ping():
    # Create a router with a ping route
    ping_router = Router([
        Route("/ping", ping_handler, methods=["GET"])
    ])
    
    # Create the PacificApp and mount the router
    app = PacificApp()
    app.mount_router(ping_router)
    
    # Test using ASGI scope
    import asyncio
    from starlette.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/ping")
    
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}