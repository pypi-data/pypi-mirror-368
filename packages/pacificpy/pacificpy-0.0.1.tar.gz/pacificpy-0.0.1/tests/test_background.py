"""
Integration tests for background tasks in PacificPy.

This module contains tests for enqueueing, executing, and monitoring background tasks.
"""

import asyncio
import time
import pytest
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pacificpy.background.local import LocalTaskExecutor, get_local_executor
from pacificpy.background.decorators import background, configure_background_tasks
from pacificpy.background.monitor import (
    TaskMonitor, 
    configure_task_monitor, 
    record_task_start, 
    update_task_status, 
    get_task_status
)

# Test tasks
def simple_task(x: int, y: int) -> int:
    """A simple task that adds two numbers."""
    return x + y

def task_with_delay(seconds: int) -> str:
    """A task that simulates work with a delay."""
    time.sleep(seconds)
    return f"Task completed after {seconds} seconds"

def failing_task() -> None:
    """A task that raises an exception."""
    raise ValueError("This task always fails")

# Test routes
async def enqueue_simple_task(request):
    """Route to enqueue a simple task."""
    data = await request.json()
    x = data.get("x", 0)
    y = data.get("y", 0)
    
    task_id = await execute_simple_task.delay(x, y)
    return JSONResponse({"task_id": task_id})

async def enqueue_delayed_task(request):
    """Route to enqueue a delayed task."""
    data = await request.json()
    seconds = data.get("seconds", 1)
    
    task_id = await execute_delayed_task.delay(seconds)
    return JSONResponse({"task_id": task_id})

async def enqueue_failing_task(request):
    """Route to enqueue a failing task."""
    task_id = await execute_failing_task.delay()
    return JSONResponse({"task_id": task_id})

async def get_task_status_route(request):
    """Route to get task status."""
    task_id = request.path_params["task_id"]
    monitor = get_task_monitor()
    status_data = monitor.get_task_status(task_id)
    
    if status_data is None:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    
    return JSONResponse(status_data)

# Background task decorators
@background
def execute_simple_task(x: int, y: int) -> int:
    """Execute a simple task in the background."""
    return simple_task(x, y)

@background
def execute_delayed_task(seconds: int) -> str:
    """Execute a delayed task in the background."""
    return task_with_delay(seconds)

@background
def execute_failing_task() -> None:
    """Execute a failing task in the background."""
    return failing_task()

# Test app
app = Starlette(
    routes=[
        Route("/tasks/simple", enqueue_simple_task, methods=["POST"]),
        Route("/tasks/delayed", enqueue_delayed_task, methods=["POST"]),
        Route("/tasks/failing", enqueue_failing_task, methods=["POST"]),
        Route("/tasks/{task_id}/status", get_task_status_route, methods=["GET"]),
    ]
)

# Configure background tasks for testing
local_executor = get_local_executor(max_workers=2)
configure_background_tasks(local_executor)

# Configure task monitor for testing
configure_task_monitor()

# Add monitor to app state
app.state.task_monitor = get_task_monitor()

# Test client
client = TestClient(app)

# Tests
def test_local_task_executor_enqueue():
    """Test enqueueing tasks with local executor."""
    executor = LocalTaskExecutor(max_workers=2)
    
    # Enqueue a simple task
    task_id = executor._loop.run_until_complete(
        executor.enqueue(simple_task, 2, 3)
    )
    assert isinstance(task_id, str)
    assert len(task_id) > 0

def test_local_task_executor_execute():
    """Test executing tasks with local executor."""
    executor = LocalTaskExecutor(max_workers=2)
    
    # Enqueue a task
    task_id = executor._loop.run_until_complete(
        executor.enqueue(simple_task, 5, 7)
    )
    
    # Wait for task to complete and get result
    result = executor._loop.run_until_complete(
        executor.get_result(task_id)
    )
    assert result == 12

def test_local_task_executor_status():
    """Test task status with local executor."""
    executor = LocalTaskExecutor(max_workers=2)
    
    # Enqueue a task
    task_id = executor._loop.run_until_complete(
        executor.enqueue(simple_task, 1, 1)
    )
    
    # Check status
    status = executor._loop.run_until_complete(
        executor.get_status(task_id)
    )
    assert status in ["pending", "running", "completed"]

def test_background_decorator_delay():
    """Test the background decorator's delay method."""
    # Enqueue a task using the decorator
    task_id = execute_simple_task.delay(3, 4)._coro.send(None)
    
    # In a real async environment, we'd await this
    # For testing, we'll just check that it returns a task ID
    assert isinstance(task_id, str)

def test_background_decorator_sync_call():
    """Test calling a background task synchronously."""
    # Call the task synchronously
    result = execute_simple_task(6, 8)
    assert result == 14

def test_task_monitoring():
    """Test task monitoring functionality."""
    monitor = TaskMonitor()
    
    # Record task start
    task_id = "test_task_123"
    monitor.record_task_start(task_id, "test_task")
    
    # Check task status
    status = monitor.get_task_status(task_id)
    assert status is not None
    assert status["id"] == task_id
    assert status["name"] == "test_task"
    assert status["status"] == "started"

def test_task_monitoring_update():
    """Test updating task status in monitor."""
    monitor = TaskMonitor()
    
    # Record task start
    task_id = "test_task_456"
    monitor.record_task_start(task_id, "update_test")
    
    # Update task status
    monitor.update_task_status(task_id, "completed", {"result": "success"})
    
    # Check updated status
    status = monitor.get_task_status(task_id)
    assert status is not None
    assert status["status"] == "completed"
    assert status["result"] == {"result": "success"}

# Integration tests with HTTP client
def test_enqueue_simple_task():
    """Test enqueuing a simple task via HTTP."""
    response = client.post("/tasks/simple", json={"x": 10, "y": 5})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert isinstance(data["task_id"], str)

def test_enqueue_delayed_task():
    """Test enqueuing a delayed task via HTTP."""
    response = client.post("/tasks/delayed", json={"seconds": 1})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data

def test_enqueue_failing_task():
    """Test enqueuing a failing task via HTTP."""
    response = client.post("/tasks/failing", json={})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data

def test_get_task_status():
    """Test getting task status via HTTP."""
    # First, enqueue a task
    response = client.post("/tasks/simple", json={"x": 1, "y": 2})
    assert response.status_code == 200
    task_data = response.json()
    task_id = task_data["task_id"]
    
    # Then, get the task status
    response = client.get(f"/tasks/{task_id}/status")
    assert response.status_code == 200
    status_data = response.json()
    assert "id" in status_data
    assert status_data["id"] == task_id

def test_get_nonexistent_task_status():
    """Test getting status of a nonexistent task."""
    response = client.get("/tasks/nonexistent_task/status")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data

# Async tests
@pytest.mark.asyncio
async def test_async_task_execution():
    """Test async task execution."""
    executor = get_local_executor()
    
    # Enqueue a task
    task_id = await executor.enqueue(simple_task, 7, 8)
    
    # Get result
    result = await executor.get_result(task_id)
    assert result == 15

@pytest.mark.asyncio
async def test_async_task_status():
    """Test async task status."""
    executor = get_local_executor()
    
    # Enqueue a task
    task_id = await executor.enqueue(simple_task, 9, 10)
    
    # Get status
    status = await executor.get_status(task_id)
    assert status in ["pending", "running", "completed"]

# Performance tests
def test_concurrent_task_execution():
    """Test concurrent task execution."""
    executor = LocalTaskExecutor(max_workers=4)
    
    # Enqueue multiple tasks
    task_ids = []
    for i in range(10):
        task_id = executor._loop.run_until_complete(
            executor.enqueue(simple_task, i, i * 2)
        )
        task_ids.append(task_id)
    
    # Get results for all tasks
    results = []
    for task_id in task_ids:
        result = executor._loop.run_until_complete(
            executor.get_result(task_id)
        )
        results.append(result)
    
    # Verify results
    expected_results = [i + i * 2 for i in range(10)]
    assert results == expected_results

# Cleanup
def test_cleanup():
    """Clean up after tests."""
    # Clean up is handled automatically by the executor shutdown
    pass