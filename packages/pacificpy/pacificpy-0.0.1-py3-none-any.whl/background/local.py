"""
Local task executor for PacificPy.

This module provides a simple in-process task executor using
ThreadPoolExecutor for synchronous tasks and async fallback
for asynchronous tasks, useful for development and testing.
"""

import asyncio
import concurrent.futures
import logging
from typing import Any, Callable, Dict, List, Optional, Union
import uuid

from .backend import BackgroundBackend

logger = logging.getLogger(__name__)

class LocalTaskExecutor(BackgroundBackend):
    """Local in-process task executor for development and testing."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the local task executor.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, concurrent.futures.Future] = {}
        self.results: Dict[str, Any] = {}
        self.statuses: Dict[str, str] = {}
        self._running = True
    
    async def enqueue(self, func: Union[Callable, str], *args, **kwargs) -> str:
        """
        Enqueue a task for execution.
        
        Args:
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Task ID
        """
        if not callable(func):
            raise ValueError("Local executor requires callable functions")
        
        task_id = str(uuid.uuid4())
        
        # Submit task to executor
        try:
            future = self.executor.submit(self._execute_task, func, *args, **kwargs)
            self.tasks[task_id] = future
            self.statuses[task_id] = "pending"
            
            # Add callback to track completion
            def task_done_callback(future):
                try:
                    result = future.result()
                    self.results[task_id] = result
                    self.statuses[task_id] = "completed"
                except Exception as e:
                    logger.error(f"Task {task_id} failed: {e}", exc_info=True)
                    self.results[task_id] = e
                    self.statuses[task_id] = "failed"
            
            future.add_done_callback(task_done_callback)
            
            # Update status to running
            self.statuses[task_id] = "running"
            
            logger.info(f"Task {task_id} enqueued")
            return task_id
        except Exception as e:
            logger.error(f"Failed to enqueue task: {e}", exc_info=True)
            raise
    
    async def get_result(self, task_id: str) -> Any:
        """
        Get the result of a task.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task result
            
        Raises:
            ValueError: If task ID is not found
            Exception: If the task failed
        """
        if task_id not in self.statuses:
            raise ValueError(f"Task {task_id} not found")
        
        # If we already have the result, return it
        if task_id in self.results:
            result = self.results[task_id]
            if isinstance(result, Exception):
                raise result
            return result
        
        # If task is still running, wait for it
        if task_id in self.tasks:
            future = self.tasks[task_id]
            try:
                # Wait for the future to complete
                result = future.result(timeout=30)  # 30 second timeout
                self.results[task_id] = result
                self.statuses[task_id] = "completed"
                return result
            except concurrent.futures.TimeoutError:
                raise asyncio.TimeoutError(f"Task {task_id} timed out")
            except Exception as e:
                self.results[task_id] = e
                self.statuses[task_id] = "failed"
                raise e
        
        raise ValueError(f"Task {task_id} not found")
    
    async def get_status(self, task_id: str) -> str:
        """
        Get the status of a task.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task status
        """
        return self.statuses.get(task_id, "unknown")
    
    def _execute_task(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a task in a worker thread.
        
        Args:
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function
        """
        try:
            logger.info(f"Executing task {func.__name__}")
            result = func(*args, **kwargs)
            logger.info(f"Task {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Task {func.__name__} failed: {e}", exc_info=True)
            raise
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: The task ID
            
        Returns:
            True if task was cancelled, False otherwise
        """
        if task_id in self.tasks:
            future = self.tasks[task_id]
            if future.cancel():
                self.statuses[task_id] = "cancelled"
                return True
        return False
    
    async def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the executor.
        
        Args:
            wait: Whether to wait for tasks to complete
        """
        self._running = False
        self.executor.shutdown(wait=wait)
        logger.info("Local task executor shutdown")

# Global local executor instance
_local_executor: Optional[LocalTaskExecutor] = None

def get_local_executor(max_workers: int = 4) -> LocalTaskExecutor:
    """
    Get a singleton instance of the local task executor.
    
    Args:
        max_workers: Maximum number of worker threads
        
    Returns:
        The local task executor instance
    """
    global _local_executor
    if _local_executor is None:
        _local_executor = LocalTaskExecutor(max_workers=max_workers)
    return _local_executor

async def execute_local_task(func: Callable, *args, **kwargs) -> str:
    """
    Execute a task using the local executor.
    
    Args:
        func: The function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Task ID
    """
    executor = get_local_executor()
    return await executor.enqueue(func, *args, **kwargs)

async def get_local_task_result(task_id: str) -> Any:
    """
    Get the result of a local task.
    
    Args:
        task_id: The task ID
        
    Returns:
        The task result
    """
    executor = get_local_executor()
    return await executor.get_result(task_id)

async def get_local_task_status(task_id: str) -> str:
    """
    Get the status of a local task.
    
    Args:
        task_id: The task ID
        
    Returns:
        The task status
    """
    executor = get_local_executor()
    return await executor.get_status(task_id)

# Example usage:
"""
# In your app setup for development:
from pacificpy.background.local import get_local_executor
from pacificpy.background.backend import configure_background_backend

# Configure local executor for development
local_executor = get_local_executor(max_workers=4)
configure_background_backend(local_executor)

# In your routes:
@app.post("/send-email")
async def send_email(request):
    # Enqueue email sending task
    task_id = await execute_local_task(send_email_task, request.json())
    return {"task_id": task_id}

@app.get("/task/{task_id}")
async def get_task_status(request):
    task_id = request.path_params["task_id"]
    status = await get_local_task_status(task_id)
    return {"task_id": task_id, "status": status}
"""