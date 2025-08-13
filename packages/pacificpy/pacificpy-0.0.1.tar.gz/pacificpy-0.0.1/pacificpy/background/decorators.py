"""
Background task decorators for PacificPy.

This module provides a @background decorator to mark functions
for asynchronous execution through the background task backend.
"""

import asyncio
import functools
from typing import Any, Callable, Optional, Union

from .backend import BackgroundBackend
from .local import get_local_executor

# Global background backend reference
_background_backend: Optional[BackgroundBackend] = None

def configure_background_tasks(backend: BackgroundBackend) -> None:
    """
    Configure the background task backend.
    
    Args:
        backend: The background task backend to use
    """
    global _background_backend
    _background_backend = backend

class BackgroundTask:
    """Wrapper for background tasks."""
    
    def __init__(self, func: Callable, backend: Optional[BackgroundBackend] = None):
        """
        Initialize a background task.
        
        Args:
            func: The function to execute in the background
            backend: The background task backend to use
        """
        self.func = func
        self.backend = backend or _background_backend or get_local_executor()
        self.task_id: Optional[str] = None
    
    async def delay(self, *args, **kwargs) -> str:
        """
        Enqueue the task for background execution.
        
        Args:
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Task ID
        """
        self.task_id = await self.backend.enqueue(self.func, *args, **kwargs)
        return self.task_id
    
    async def get_result(self) -> Any:
        """
        Get the result of the task.
        
        Returns:
            The task result
            
        Raises:
            ValueError: If task hasn't been enqueued yet
        """
        if not self.task_id:
            raise ValueError("Task hasn't been enqueued yet")
        
        return await self.backend.get_result(self.task_id)
    
    async def get_status(self) -> str:
        """
        Get the status of the task.
        
        Returns:
            The task status
            
        Raises:
            ValueError: If task hasn't been enqueued yet
        """
        if not self.task_id:
            raise ValueError("Task hasn't been enqueued yet")
        
        return await self.backend.get_status(self.task_id)
    
    def __call__(self, *args, **kwargs) -> Any:
        """
        Execute the task synchronously.
        
        Args:
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function
        """
        return self.func(*args, **kwargs)

def background(func: Callable = None, *, backend: BackgroundBackend = None) -> Union[Callable, BackgroundTask]:
    """
    Decorator to mark a function for background execution.
    
    Args:
        func: The function to decorate
        backend: The background task backend to use
        
    Returns:
        A BackgroundTask wrapper or decorator
        
    Example:
        @background
        def send_email(to, subject, body):
            # Send email implementation
            pass
        
        # In a handler:
        task_id = await send_email.delay("user@example.com", "Hello", "World")
        
        # Or call synchronously:
        send_email("user@example.com", "Hello", "World")
    """
    def decorator(func: Callable) -> BackgroundTask:
        # Create background task wrapper
        task = BackgroundTask(func, backend)
        
        # Add delay method for async execution
        task.delay = task.delay
        
        # Add get_result and get_status methods
        task.get_result = task.get_result
        task.get_status = task.get_status
        
        # Preserve function metadata
        functools.update_wrapper(task, func)
        
        return task
    
    # If func is provided, it means the decorator is being used without arguments
    if func is not None:
        return decorator(func)
    
    # If func is not provided, it means the decorator is being used with arguments
    return decorator

# Convenience functions for direct task execution
async def enqueue_task(func: Callable, *args, **kwargs) -> str:
    """
    Enqueue a task for background execution.
    
    Args:
        func: The function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Task ID
    """
    backend = _background_backend or get_local_executor()
    return await backend.enqueue(func, *args, **kwargs)

async def get_task_result(task_id: str) -> Any:
    """
    Get the result of a background task.
    
    Args:
        task_id: The task ID
        
    Returns:
        The task result
    """
    backend = _background_backend or get_local_executor()
    return await backend.get_result(task_id)

async def get_task_status(task_id: str) -> str:
    """
    Get the status of a background task.
    
    Args:
        task_id: The task ID
        
    Returns:
        The task status
    """
    backend = _background_backend or get_local_executor()
    return await backend.get_status(task_id)

# Example usage:
"""
# Define a background task
@background
def send_email(to: str, subject: str, body: str):
    # Simulate sending email
    import time
    time.sleep(2)  # Simulate network delay
    print(f"Email sent to {to}: {subject}")
    return {"status": "sent", "to": to, "subject": subject}

# In a route handler:
@app.post("/send-notification")
async def send_notification(request):
    data = await request.json()
    
    # Enqueue the task for background execution
    task_id = await send_email.delay(
        data["to"], 
        data["subject"], 
        data["body"]
    )
    
    return {"task_id": task_id, "message": "Email queued for sending"}

# Check task status:
@app.get("/task/{task_id}")
async def check_task_status(request):
    task_id = request.path_params["task_id"]
    status = await get_task_status(task_id)
    return {"task_id": task_id, "status": status}

# Get task result:
@app.get("/task/{task_id}/result")
async def get_task_result_endpoint(request):
    task_id = request.path_params["task_id"]
    try:
        result = await get_task_result(task_id)
        return {"task_id": task_id, "result": result}
    except Exception as e:
        return {"task_id": task_id, "error": str(e)}

# Synchronous execution:
@app.post("/send-immediate")
async def send_immediate(request):
    data = await request.json()
    
    # Execute synchronously
    result = send_email(
        data["to"], 
        data["subject"], 
        data["body"]
    )
    
    return {"result": result}
"""