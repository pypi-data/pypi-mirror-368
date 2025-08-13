from typing import Any, Callable, List, Tuple, Union
import asyncio
import inspect
from concurrent.futures import ThreadPoolExecutor


class BackgroundTaskManager:
    """
    Manager for background tasks that execute after response is sent.
    """
    
    def __init__(self) -> None:
        """Initialize the background task manager."""
        self._tasks: List[Tuple[Callable, Tuple[Any, ...], dict]] = []
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    def add(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Add a background task to be executed after response is sent.
        
        Args:
            func: The function to execute.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        """
        self._tasks.append((func, args, kwargs))
    
    async def execute_all(self) -> None:
        """
        Execute all background tasks.
        """
        if not self._tasks:
            return
        
        # Execute all tasks concurrently
        tasks = []
        for func, args, kwargs in self._tasks:
            if inspect.iscoroutinefunction(func):
                # For async functions, create a task
                task = asyncio.create_task(func(*args, **kwargs))
                tasks.append(task)
            else:
                # For sync functions, run in thread pool
                # We need to create a wrapper function to handle kwargs
                def sync_wrapper(f, args, kwargs):
                    return f(*args, **kwargs)
                
                loop = asyncio.get_event_loop()
                task = loop.run_in_executor(self._executor, sync_wrapper, func, args, kwargs)
                tasks.append(task)
        
        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Clear tasks
        self._tasks.clear()
    
    def clear(self) -> None:
        """Clear all pending tasks."""
        self._tasks.clear()
    
    def __len__(self) -> int:
        """Return the number of pending tasks."""
        return len(self._tasks)
    
    def __bool__(self) -> bool:
        """Return True if there are pending tasks."""
        return bool(self._tasks)