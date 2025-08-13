"""
TodoApp with Background Tasks Example

This example shows how to use background tasks in a Todo application
to send email notifications when tasks are created.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request

# Import PacificPy background task components
from pacificpy.background.decorators import background, configure_background_tasks
from pacificpy.background.local import get_local_executor
from pacificpy.background.monitor import configure_task_monitor, record_task_start, update_task_status
from pacificpy.background.health import configure_health_checks, integrate_with_app_health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class TodoCreate(BaseModel):
    """Model for creating a todo item."""
    title: str
    description: Optional[str] = None
    priority: int = 1

class Todo(BaseModel):
    """Model for a todo item."""
    id: int
    title: str
    description: Optional[str] = None
    priority: int
    completed: bool = False
    created_at: float = Field(default_factory=time.time)

class User(BaseModel):
    """Model for a user."""
    id: int
    email: str
    name: str

# In-memory storage
todos: Dict[int, Todo] = {}
users: Dict[int, User] = {}
next_todo_id = 1

# Sample users
users[1] = User(id=1, email="user@example.com", name="John Doe")
users[2] = User(id=2, email="admin@example.com", name="Jane Admin")

# Background tasks
@background
def send_notification_email(user_id: int, todo_title: str):
    """
    Send a notification email when a todo is created.
    
    Args:
        user_id: The ID of the user to notify
        todo_title: The title of the created todo
    """
    # Simulate task ID for monitoring
    import uuid
    task_id = str(uuid.uuid4())
    record_task_start(task_id, "send_notification_email")
    
    try:
        # Get user
        user = users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Simulate email sending with delay
        logger.info(f"Sending email to {user.email} about new todo: {todo_title}")
        time.sleep(3)  # Simulate network delay
        
        # Simulate email sending
        email_content = f"""
        Subject: New Todo Created
        
        Hello {user.name},
        
        A new todo item has been created:
        Title: {todo_title}
        
        Best regards,
        TodoApp Team
        """
        
        logger.info(f"Email sent to {user.email}")
        update_task_status(task_id, "completed", {"status": "sent", "to": user.email})
        
        return {"status": "sent", "to": user.email}
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        update_task_status(task_id, "failed", {"error": str(e)})
        raise

# API endpoints
async def create_todo(request: Request) -> JSONResponse:
    """
    Create a new todo item.
    
    Args:
        request: The HTTP request
        
    Returns:
        JSON response with the created todo
    """
    global next_todo_id
    
    # Parse request data
    data = await request.json()
    todo_data = TodoCreate(**data)
    
    # Get user from request (in a real app, this would come from auth)
    user_id = int(request.query_params.get("user_id", 1))
    
    # Create todo
    todo = Todo(
        id=next_todo_id,
        title=todo_data.title,
        description=todo_data.description,
        priority=todo_data.priority
    )
    
    todos[next_todo_id] = todo
    next_todo_id += 1
    
    # Send notification email in background
    try:
        task_id = await send_notification_email.delay(user_id, todo.title)
        logger.info(f"Queued email notification task: {task_id}")
    except Exception as e:
        logger.error(f"Failed to queue email notification: {e}")
    
    return JSONResponse(todo.dict(), status_code=201)

async def get_todos(request: Request) -> JSONResponse:
    """
    Get all todo items.
    
    Args:
        request: The HTTP request
        
    Returns:
        JSON response with all todos
    """
    return JSONResponse([todo.dict() for todo in todos.values()])

async def get_todo(request: Request) -> JSONResponse:
    """
    Get a specific todo item.
    
    Args:
        request: The HTTP request
        
    Returns:
        JSON response with the todo
    """
    todo_id = int(request.path_params["todo_id"])
    todo = todos.get(todo_id)
    
    if not todo:
        return JSONResponse({"error": "Todo not found"}, status_code=404)
    
    return JSONResponse(todo.dict())

async def update_todo(request: Request) -> JSONResponse:
    """
    Update a todo item.
    
    Args:
        request: The HTTP request
        
    Returns:
        JSON response with the updated todo
    """
    todo_id = int(request.path_params["todo_id"])
    todo = todos.get(todo_id)
    
    if not todo:
        return JSONResponse({"error": "Todo not found"}, status_code=404)
    
    # Parse request data
    data = await request.json()
    
    # Update todo fields
    if "title" in data:
        todo.title = data["title"]
    if "description" in data:
        todo.description = data.get("description")
    if "priority" in data:
        todo.priority = data["priority"]
    if "completed" in data:
        todo.completed = data["completed"]
    
    return JSONResponse(todo.dict())

async def delete_todo(request: Request) -> JSONResponse:
    """
    Delete a todo item.
    
    Args:
        request: The HTTP request
        
    Returns:
        JSON response confirming deletion
    """
    todo_id = int(request.path_params["todo_id"])
    
    if todo_id not in todos:
        return JSONResponse({"error": "Todo not found"}, status_code=404)
    
    del todos[todo_id]
    return JSONResponse({"message": "Todo deleted"})

# Health check endpoint
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})

# Create app
app = Starlette(
    routes=[
        Route("/todos", create_todo, methods=["POST"]),
        Route("/todos", get_todos, methods=["GET"]),
        Route("/todos/{todo_id:int}", get_todo, methods=["GET"]),
        Route("/todos/{todo_id:int}", update_todo, methods=["PUT"]),
        Route("/todos/{todo_id:int}", delete_todo, methods=["DELETE"]),
        Route("/health", health_check, methods=["GET"]),
    ]
)

# Configure background tasks
local_executor = get_local_executor(max_workers=4)
configure_background_tasks(local_executor)

# Configure task monitoring
configure_task_monitor()

# Configure health checks
configure_health_checks()

# Integrate background health checks
asyncio.create_task(integrate_with_app_health(app))

# Example usage instructions
def main():
    """
    Main function to run the TodoApp example.
    
    To run this example:
    
    1. Start the server:
       uvicorn examples.todo.background_example:app --reload
    
    2. Create a todo with email notification:
       curl -X POST "http://localhost:8000/todos?user_id=1" \\
            -H "Content-Type: application/json" \\
            -d '{"title": "Buy groceries", "description": "Milk, bread, eggs", "priority": 2}'
    
    3. List all todos:
       curl -X GET "http://localhost:8000/todos"
    
    4. Check health:
       curl -X GET "http://localhost:8000/health"
    
    The background task will send an email notification 3 seconds after
    creating a todo item. Check the console logs to see the email being sent.
    """
    print("TodoApp with Background Tasks Example")
    print("=" * 40)
    print()
    print("To run this example:")
    print()
    print("1. Start the server:")
    print("   uvicorn examples.todo.background_example:app --reload")
    print()
    print("2. Create a todo with email notification:")
    print('   curl -X POST "http://localhost:8000/todos?user_id=1" \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"title": "Buy groceries", "description": "Milk, bread, eggs", "priority": 2}\'')
    print()
    print("3. List all todos:")
    print('   curl -X GET "http://localhost:8000/todos"')
    print()
    print("4. Check health:")
    print('   curl -X GET "http://localhost:8000/health"')
    print()
    print("The background task will send an email notification 3 seconds after")
    print("creating a todo item. Check the console logs to see the email being sent.")

if __name__ == "__main__":
    main()