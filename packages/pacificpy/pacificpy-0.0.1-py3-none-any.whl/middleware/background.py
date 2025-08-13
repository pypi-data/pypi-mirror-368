from typing import Callable, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
from starlette.background import BackgroundTasks


class BackgroundTaskMiddleware(BaseHTTPMiddleware):
    """
    Middleware to manage background tasks.
    """
    
    async def dispatch(
        self, 
        request: StarletteRequest, 
        call_next: Callable[[StarletteRequest], Any]
    ) -> StarletteResponse:
        """
        Process the request and manage background tasks.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or endpoint handler.
            
        Returns:
            The response from the next middleware or endpoint handler.
        """
        # Import BackgroundTaskManager here to avoid circular imports
        from ..core.background import BackgroundTaskManager
        
        # Add background task manager to request state
        if not hasattr(request, 'state'):
            from starlette.datastructures import State
            request.state = State()
        
        request.state.background_task_manager = BackgroundTaskManager()
        
        # Call the next middleware or endpoint handler
        response = await call_next(request)
        
        # Execute background tasks after response is sent
        background_manager = getattr(request.state, 'background_task_manager', None)
        if background_manager and len(background_manager) > 0:
            # Create a Starlette BackgroundTasks object
            background_tasks = BackgroundTasks()
            
            # Add a task to execute all background tasks from our manager
            async def execute_all_background_tasks():
                await background_manager.execute_all()
            
            background_tasks.add_task(execute_all_background_tasks)
            
            # Add background tasks to response
            if hasattr(response, 'background'):
                if response.background is None:
                    response.background = background_tasks
                else:
                    # If response already has background tasks, combine them
                    if hasattr(response.background, 'tasks'):
                        background_tasks.tasks.extend(response.background.tasks)
                    response.background = background_tasks
        
        return response