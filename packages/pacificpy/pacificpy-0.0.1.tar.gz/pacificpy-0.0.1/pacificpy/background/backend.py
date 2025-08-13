"""
Background task backend abstraction for PacificPy.

This module provides an abstract interface for background task backends
and adapters for Celery and ARQ.
"""

import abc
import asyncio
from typing import Any, Callable, Dict, Optional, Union
from concurrent.futures import ThreadPoolExecutor

# Try to import Celery
try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

# Try to import ARQ
try:
    from arq import create_pool
    from arq.connections import RedisSettings
    ARQ_AVAILABLE = True
except ImportError:
    ARQ_AVAILABLE = False

class BackgroundBackend(abc.ABC):
    """Abstract base class for background task backends."""
    
    @abc.abstractmethod
    async def enqueue(self, func: Union[Callable, str], *args, **kwargs) -> str:
        """
        Enqueue a task for background execution.
        
        Args:
            func: The function to execute (or task name for remote workers)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Task ID
        """
        pass
    
    @abc.abstractmethod
    async def get_result(self, task_id: str) -> Any:
        """
        Get the result of a background task.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task result
        """
        pass
    
    @abc.abstractmethod
    async def get_status(self, task_id: str) -> str:
        """
        Get the status of a background task.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task status (e.g., "pending", "running", "completed", "failed")
        """
        pass

class LocalBackgroundBackend(BackgroundBackend):
    """Local background task backend using ThreadPoolExecutor."""
    
    def __init__(self, max_workers: int = 10):
        """
        Initialize the local background backend.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = {}  # task_id -> future
        self.results = {}  # task_id -> result
        self.statuses = {}  # task_id -> status
    
    async def enqueue(self, func: Union[Callable, str], *args, **kwargs) -> str:
        """
        Enqueue a task for background execution.
        
        Args:
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Task ID
        """
        import uuid
        task_id = str(uuid.uuid4())
        
        # Submit task to executor
        if callable(func):
            future = self.executor.submit(func, *args, **kwargs)
        else:
            raise ValueError("Local backend requires callable functions")
        
        # Store task reference
        self.tasks[task_id] = future
        self.statuses[task_id] = "pending"
        
        # Add callback to track completion
        def task_done_callback(future):
            try:
                result = future.result()
                self.results[task_id] = result
                self.statuses[task_id] = "completed"
            except Exception as e:
                self.results[task_id] = e
                self.statuses[task_id] = "failed"
        
        future.add_done_callback(task_done_callback)
        
        # Update status to running
        self.statuses[task_id] = "running"
        
        return task_id
    
    async def get_result(self, task_id: str) -> Any:
        """
        Get the result of a background task.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task result
        """
        if task_id in self.results:
            result = self.results[task_id]
            # If result is an exception, raise it
            if isinstance(result, Exception):
                raise result
            return result
        
        # If task is still running, wait for it
        if task_id in self.tasks:
            future = self.tasks[task_id]
            try:
                result = await asyncio.get_event_loop().run_in_executor(None, future.result)
                self.results[task_id] = result
                self.statuses[task_id] = "completed"
                return result
            except Exception as e:
                self.results[task_id] = e
                self.statuses[task_id] = "failed"
                raise e
        
        raise ValueError(f"Task {task_id} not found")
    
    async def get_status(self, task_id: str) -> str:
        """
        Get the status of a background task.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task status
        """
        return self.statuses.get(task_id, "unknown")

class CeleryBackgroundBackend(BackgroundBackend):
    """Celery background task backend adapter."""
    
    def __init__(self, celery_app: Celery = None, broker_url: str = None):
        """
        Initialize the Celery background backend.
        
        Args:
            celery_app: A Celery app instance
            broker_url: The broker URL (if creating a new app)
        """
        if not CELERY_AVAILABLE:
            raise RuntimeError("Celery is required for CeleryBackgroundBackend")
        
        if celery_app:
            self.celery = celery_app
        elif broker_url:
            self.celery = Celery(broker=broker_url)
        else:
            raise ValueError("Either celery_app or broker_url must be provided")
    
    async def enqueue(self, func: Union[Callable, str], *args, **kwargs) -> str:
        """
        Enqueue a task for background execution.
        
        Args:
            func: The function to execute (or task name)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Task ID
        """
        if callable(func):
            # Register function with Celery if it's not already
            if not hasattr(func, '__name__'):
                raise ValueError("Callable must have a __name__ attribute")
            
            # Create Celery task
            task = self.celery.task(func)
            result = task.delay(*args, **kwargs)
        else:
            # Assume func is a task name
            result = self.celery.send_task(func, args=args, kwargs=kwargs)
        
        return result.id
    
    async def get_result(self, task_id: str) -> Any:
        """
        Get the result of a background task.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task result
        """
        result = self.celery.AsyncResult(task_id)
        if result.ready():
            if result.failed():
                raise result.result
            return result.result
        else:
            raise asyncio.TimeoutError("Task not completed yet")
    
    async def get_status(self, task_id: str) -> str:
        """
        Get the status of a background task.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task status
        """
        result = self.celery.AsyncResult(task_id)
        return result.state.lower()

class ARQBackgroundBackend(BackgroundBackend):
    """ARQ background task backend adapter (stub)."""
    
    def __init__(self, redis_settings: RedisSettings = None, redis_url: str = None):
        """
        Initialize the ARQ background backend.
        
        Args:
            redis_settings: ARQ Redis settings
            redis_url: Redis URL (if not using RedisSettings)
        """
        if not ARQ_AVAILABLE:
            raise RuntimeError("ARQ is required for ARQBackgroundBackend")
        
        self.redis_settings = redis_settings or RedisSettings()
        if redis_url:
            # Parse redis_url into RedisSettings
            pass  # Simplified for this stub
        
        self.pool = None
    
    async def connect(self) -> None:
        """Connect to Redis."""
        if not self.pool:
            self.pool = await create_pool(self.redis_settings)
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.pool:
            await self.pool.aclose()
            self.pool = None
    
    async def enqueue(self, func: Union[Callable, str], *args, **kwargs) -> str:
        """
        Enqueue a task for background execution.
        
        Args:
            func: The function to execute (or task name)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Task ID
        """
        if not self.pool:
            await self.connect()
        
        # In a real implementation, this would enqueue the task with ARQ
        # For this stub, we'll just simulate it
        import uuid
        task_id = str(uuid.uuid4())
        return task_id
    
    async def get_result(self, task_id: str) -> Any:
        """
        Get the result of a background task.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task result
        """
        # In a real implementation, this would get the result from Redis
        # For this stub, we'll just raise an exception
        raise NotImplementedError("ARQ result retrieval not implemented in stub")
    
    async def get_status(self, task_id: str) -> str:
        """
        Get the status of a background task.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task status
        """
        # In a real implementation, this would get the status from Redis
        # For this stub, we'll just return a default status
        return "pending"

# Global background backend instance
_background_backend: Optional[BackgroundBackend] = None

def configure_background_backend(backend: BackgroundBackend) -> None:
    """
    Configure the global background task backend.
    
    Args:
        backend: The background task backend to use
    """
    global _background_backend
    _background_backend = backend

async def enqueue_task(func: Union[Callable, str], *args, **kwargs) -> str:
    """
    Enqueue a task using the global background backend.
    
    Args:
        func: The function to execute (or task name)
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Task ID
        
    Raises:
        RuntimeError: If background backend is not configured
    """
    if not _background_backend:
        raise RuntimeError("Background backend not configured")
    
    return await _background_backend.enqueue(func, *args, **kwargs)

async def get_task_result(task_id: str) -> Any:
    """
    Get the result of a background task using the global backend.
    
    Args:
        task_id: The task ID
        
    Returns:
        The task result
        
    Raises:
        RuntimeError: If background backend is not configured
    """
    if not _background_backend:
        raise RuntimeError("Background backend not configured")
    
    return await _background_backend.get_result(task_id)

async def get_task_status(task_id: str) -> str:
    """
    Get the status of a background task using the global backend.
    
    Args:
        task_id: The task ID
        
    Returns:
        The task status
        
    Raises:
        RuntimeError: If background backend is not configured
    """
    if not _background_backend:
        raise RuntimeError("Background backend not configured")
    
    return await _background_backend.get_status(task_id)