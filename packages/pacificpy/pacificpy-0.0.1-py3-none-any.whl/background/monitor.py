"""
Task monitoring for PacificPy.

This module provides a simple task status storage and monitoring endpoint.
"""

import time
import uuid
from typing import Any, Dict, Optional
from starlette.responses import JSONResponse

# Try to import redis for persistent storage
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class TaskMonitor:
    """Simple task status monitor."""
    
    def __init__(self, redis_url: str = None, prefix: str = "task:"):
        """
        Initialize the task monitor.
        
        Args:
            redis_url: Redis URL for persistent storage (optional)
            prefix: Prefix for Redis keys
        """
        self.prefix = prefix
        self.redis_client = None
        
        # In-memory storage for when Redis is not available
        self.in_memory_storage: Dict[str, Dict[str, Any]] = {}
        
        # Initialize Redis if URL is provided
        if redis_url and REDIS_AVAILABLE:
            self.redis_client = redis.from_url(redis_url)
        elif redis_url:
            raise RuntimeError("redis package is required for Redis storage")
    
    def record_task_start(self, task_id: str, task_name: str = None) -> None:
        """
        Record the start of a task.
        
        Args:
            task_id: The task ID
            task_name: The name of the task (optional)
        """
        task_data = {
            "id": task_id,
            "name": task_name or "unknown",
            "status": "started",
            "started_at": time.time(),
            "updated_at": time.time(),
        }
        
        if self.redis_client:
            # Store in Redis
            key = f"{self.prefix}{task_id}"
            self.redis_client.setex(key, 86400, str(task_data))  # Expire in 24 hours
        else:
            # Store in memory
            self.in_memory_storage[task_id] = task_data
    
    def update_task_status(self, task_id: str, status: str, result: Any = None) -> None:
        """
        Update the status of a task.
        
        Args:
            task_id: The task ID
            status: The new status
            result: The task result (optional)
        """
        task_data = {
            "id": task_id,
            "status": status,
            "updated_at": time.time(),
        }
        
        if result is not None:
            task_data["result"] = result
        
        if self.redis_client:
            # Update in Redis
            key = f"{self.prefix}{task_id}"
            existing_data = self.redis_client.get(key)
            if existing_data:
                # Merge with existing data
                import ast
                existing_data = ast.literal_eval(existing_data.decode())
                existing_data.update(task_data)
                task_data = existing_data
            
            self.redis_client.setex(key, 86400, str(task_data))  # Expire in 24 hours
        else:
            # Update in memory
            if task_id in self.in_memory_storage:
                self.in_memory_storage[task_id].update(task_data)
            else:
                self.in_memory_storage[task_id] = task_data
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a task.
        
        Args:
            task_id: The task ID
            
        Returns:
            Task status data or None if not found
        """
        if self.redis_client:
            # Get from Redis
            key = f"{self.prefix}{task_id}"
            task_data = self.redis_client.get(key)
            if task_data:
                import ast
                return ast.literal_eval(task_data.decode())
            return None
        else:
            # Get from memory
            return self.in_memory_storage.get(task_id)
    
    def get_all_tasks(self, limit: int = 100) -> Dict[str, Dict[str, Any]]:
        """
        Get all tasks (limited for performance).
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            Dictionary of task statuses
        """
        if self.redis_client:
            # Get from Redis (limited)
            keys = self.redis_client.keys(f"{self.prefix}*")[:limit]
            tasks = {}
            for key in keys:
                task_data = self.redis_client.get(key)
                if task_data:
                    import ast
                    task_dict = ast.literal_eval(task_data.decode())
                    task_id = key.decode().replace(self.prefix, "")
                    tasks[task_id] = task_dict
            return tasks
        else:
            # Get from memory (limited)
            task_ids = list(self.in_memory_storage.keys())[-limit:]
            return {task_id: self.in_memory_storage[task_id] for task_id in task_ids}

# Global task monitor instance
_task_monitor: Optional[TaskMonitor] = None

def configure_task_monitor(redis_url: str = None) -> TaskMonitor:
    """
    Configure the global task monitor.
    
    Args:
        redis_url: Redis URL for persistent storage (optional)
        
    Returns:
        The task monitor instance
    """
    global _task_monitor
    _task_monitor = TaskMonitor(redis_url=redis_url)
    return _task_monitor

def get_task_monitor() -> TaskMonitor:
    """
    Get the global task monitor instance.
    
    Returns:
        The task monitor instance
    """
    global _task_monitor
    if _task_monitor is None:
        _task_monitor = TaskMonitor()
    return _task_monitor

def record_task_start(task_id: str, task_name: str = None) -> None:
    """
    Record the start of a task.
    
    Args:
        task_id: The task ID
        task_name: The name of the task (optional)
    """
    monitor = get_task_monitor()
    monitor.record_task_start(task_id, task_name)

def update_task_status(task_id: str, status: str, result: Any = None) -> None:
    """
    Update the status of a task.
    
    Args:
        task_id: The task ID
        status: The new status
        result: The task result (optional)
    """
    monitor = get_task_monitor()
    monitor.update_task_status(task_id, status, result)

def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the status of a task.
    
    Args:
        task_id: The task ID
        
    Returns:
        Task status data or None if not found
    """
    monitor = get_task_monitor()
    return monitor.get_task_status(task_id)

# Monitoring endpoints
async def tasks_list_endpoint(request):
    """
    Endpoint to list all tasks.
    
    Args:
        request: The request object
        
    Returns:
        JSON response with task list
    """
    monitor = get_task_monitor()
    tasks = monitor.get_all_tasks()
    
    # Format tasks for response
    formatted_tasks = []
    for task_id, task_data in tasks.items():
        formatted_task = {
            "id": task_id,
            "name": task_data.get("name", "unknown"),
            "status": task_data.get("status", "unknown"),
            "started_at": task_data.get("started_at"),
            "updated_at": task_data.get("updated_at"),
        }
        formatted_tasks.append(formatted_task)
    
    return JSONResponse({"tasks": formatted_tasks})

async def task_detail_endpoint(request):
    """
    Endpoint to get details of a specific task.
    
    Args:
        request: The request object
        
    Returns:
        JSON response with task details
    """
    task_id = request.path_params["task_id"]
    monitor = get_task_monitor()
    task_data = monitor.get_task_status(task_id)
    
    if task_data is None:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    
    return JSONResponse(task_data)

# Example usage:
"""
# In your app setup:
from pacificpy.background.monitor import configure_task_monitor

# Configure task monitor
configure_task_monitor(redis_url="redis://localhost:6379/0")

# In your background tasks:
from pacificpy.background.monitor import record_task_start, update_task_status

@background
def my_task(param1, param2):
    task_id = str(uuid.uuid4())  # Or get from context
    record_task_start(task_id, "my_task")
    
    try:
        # Do work
        result = do_some_work(param1, param2)
        update_task_status(task_id, "completed", result)
        return result
    except Exception as e:
        update_task_status(task_id, "failed", str(e))
        raise

# Add monitoring endpoints to your app:
app.add_route("/tasks", tasks_list_endpoint, methods=["GET"])
app.add_route("/tasks/{task_id}", task_detail_endpoint, methods=["GET"])
"""