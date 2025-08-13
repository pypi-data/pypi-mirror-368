import time
import asyncio
from starlette.routing import Route, Router
from starlette.background import BackgroundTasks

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings
from pacificpy.core.http import Request, Response
from pacificpy.core.background import BackgroundTaskManager


# Global variable to track background task execution
background_task_executed = False
background_task_data = None


def background_task(data):
    """Background task that simulates work."""
    global background_task_executed, background_task_data
    print(f"Background task started with data: {data}")
    
    # Simulate some work
    time.sleep(2)
    
    background_task_executed = True
    background_task_data = data
    print("Background task completed")


async def async_background_task(data):
    """Async background task that simulates work."""
    global background_task_executed, background_task_data
    print(f"Async background task started with data: {data}")
    
    # Simulate some work
    await asyncio.sleep(2)
    
    background_task_executed = True
    background_task_data = data
    print("Async background task completed")


async def handler_with_background_task(request: Request) -> Response:
    """Handler that adds a background task."""
    global background_task_executed, background_task_data
    
    # Reset global variables
    background_task_executed = False
    background_task_data = None
    
    # Create background task manager
    background_manager = BackgroundTaskManager()
    
    # Add a background task
    background_manager.add(background_task, "test-data")
    
    # Create a response with background tasks
    async def execute_background_tasks():
        await background_manager.execute_all()
    
    # Create background tasks for Starlette
    background_tasks = BackgroundTasks()
    background_tasks.add_task(execute_background_tasks)
    
    return Response.json({
        "message": "Response sent"
    }, background=background_tasks)


async def handler_with_background_task_manager(request: Request) -> Response:
    """Handler that demonstrates using BackgroundTaskManager directly."""
    global background_task_executed, background_task_data
    
    # Reset global variables
    background_task_executed = False
    background_task_data = None
    
    # Create background task manager
    background_manager = BackgroundTaskManager()
    
    # Add background tasks
    background_manager.add(background_task, "test-data")
    background_manager.add(async_background_task, "async-test-data")
    
    # Execute tasks immediately for demonstration
    await background_manager.execute_all()
    
    return Response.json({
        "message": "Response sent",
        "background_task_executed": background_task_executed,
        "background_task_data": background_task_data
    })


async def check_background_task_status(request: Request) -> Response:
    """Handler that checks background task status."""
    global background_task_executed, background_task_data
    
    return Response.json({
        "background_task_executed": background_task_executed,
        "background_task_data": background_task_data
    })


if __name__ == "__main__":
    # Create router with test routes
    api_router = Router([
        Route("/background-task", handler_with_background_task, methods=["GET"]),
        Route("/background-task-manager", handler_with_background_task_manager, methods=["GET"]),
        Route("/check-status", check_background_task_status, methods=["GET"]),
    ])
    
    # Create the PacificApp
    app = PacificApp()
    
    # Mount router
    app.mount_router(api_router)
    
    # Create settings
    settings = Settings.from_env()
    
    # Run the app with PacificPy server using settings
    run(
        app, 
        host=settings.host, 
        port=settings.port,
        use_uvloop=True,
        reload=settings.debug
    )