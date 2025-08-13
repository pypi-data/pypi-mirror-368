"""
Health checks for background task system in PacificPy.

This module provides health check endpoints and hooks for monitoring
the availability of task backends and queue status.
"""

from typing import Dict, Any, Optional
from starlette.responses import JSONResponse

from .backend import BackgroundBackend
from .local import get_local_executor

# Global background backend reference
_background_backend: Optional[BackgroundBackend] = None

def configure_health_checks(backend: BackgroundBackend = None) -> None:
    """
    Configure the background task backend for health checks.
    
    Args:
        backend: The background task backend to use
    """
    global _background_backend
    _background_backend = backend

async def background_health_check() -> Dict[str, Any]:
    """
    Perform a health check on the background task system.
    
    Returns:
        Health check results
    """
    backend = _background_backend or get_local_executor()
    
    try:
        # Check if backend is responsive
        if hasattr(backend, 'health_check'):
            # Use backend-specific health check
            backend_healthy = await backend.health_check()
        else:
            # Generic health check - try to get status of a non-existent task
            try:
                await backend.get_status("health-check")
                backend_healthy = True
            except Exception:
                # If we get an exception other than "task not found", backend might be unhealthy
                # For most backends, getting status of non-existent task should not raise exception
                backend_healthy = True
        
        # Get queue information if available
        queue_info = {}
        if hasattr(backend, 'get_queue_info'):
            queue_info = await backend.get_queue_info()
        elif hasattr(backend, 'queue_length'):
            try:
                queue_info["length"] = await backend.queue_length()
            except Exception:
                queue_info["length"] = "unknown"
        
        return {
            "status": "healthy" if backend_healthy else "unhealthy",
            "backend": type(backend).__name__,
            "queue": queue_info,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "backend": type(backend).__name__,
            "error": str(e),
        }

async def health_check_endpoint(request) -> JSONResponse:
    """
    Health check endpoint for background task system.
    
    Args:
        request: The request object
        
    Returns:
        JSON response with health check results
    """
    health_data = await background_health_check()
    status_code = 200 if health_data["status"] == "healthy" else 503
    return JSONResponse(health_data, status_code=status_code)

# Extend LocalTaskExecutor with health check methods
from .local import LocalTaskExecutor

def _add_health_check_methods():
    """Add health check methods to LocalTaskExecutor."""
    
    async def health_check(self) -> bool:
        """Check if the executor is healthy."""
        return self._running
    
    async def get_queue_info(self) -> Dict[str, Any]:
        """Get information about the task queue."""
        pending_tasks = sum(1 for status in self.statuses.values() if status in ["pending", "running"])
        completed_tasks = sum(1 for status in self.statuses.values() if status == "completed")
        failed_tasks = sum(1 for status in self.statuses.values() if status == "failed")
        
        return {
            "pending": pending_tasks,
            "completed": completed_tasks,
            "failed": failed_tasks,
            "total": len(self.tasks),
        }
    
    async def queue_length(self) -> int:
        """Get the current queue length."""
        return sum(1 for status in self.statuses.values() if status in ["pending", "running"])
    
    # Add methods to LocalTaskExecutor
    LocalTaskExecutor.health_check = health_check
    LocalTaskExecutor.get_queue_info = get_queue_info
    LocalTaskExecutor.queue_length = queue_length

# Apply the health check methods
_add_health_check_methods()

# Example integration with main health check system
async def integrate_with_app_health(app) -> None:
    """
    Integrate background task health checks with the main application health check.
    
    Args:
        app: The PacificPy application
    """
    # Add background health check to app's health checks
    if hasattr(app, 'health_checks'):
        app.health_checks['background'] = background_health_check
    else:
        app.health_checks = {'background': background_health_check}
    
    # Add health check endpoint
    app.add_route("/health/background", health_check_endpoint, methods=["GET"])

# Utility functions for manual health checking
def get_background_backend() -> BackgroundBackend:
    """
    Get the current background task backend.
    
    Returns:
        The background task backend
    """
    return _background_backend or get_local_executor()

async def is_background_healthy() -> bool:
    """
    Check if the background task system is healthy.
    
    Returns:
        True if healthy, False otherwise
    """
    health_data = await background_health_check()
    return health_data["status"] == "healthy"

# Example usage:
"""
# In your app setup:
from pacificpy.background.health import configure_health_checks, integrate_with_app_health

# Configure health checks
configure_health_checks()

# Integrate with app health checks
await integrate_with_app_health(app)

# The health check will be available at /health/background
# And integrated with the main /health endpoint if your app supports it
"""