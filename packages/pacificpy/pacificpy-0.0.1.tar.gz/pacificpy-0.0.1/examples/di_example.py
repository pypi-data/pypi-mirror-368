"""
Example usage of PacificPy's Dependency Injection system
"""
import asyncio
from pacificpy.di import Depends, DependencyResolver, DependencyCache, HandlerBinder, LifecycleManager

# Example services
class DatabaseClient:
    def __init__(self):
        self.connection = None
    
    async def startup(self):
        print("Connecting to database...")
        # Simulate connection
        await asyncio.sleep(0.1)
        self.connection = "db_connection"
        print("Database connected!")
    
    async def shutdown(self):
        print("Closing database connection...")
        # Simulate disconnection
        await asyncio.sleep(0.1)
        self.connection = None
        print("Database disconnected!")
    
    async def get_user(self, user_id: int):
        # Simulate database query
        await asyncio.sleep(0.01)
        return {"id": user_id, "name": f"User {user_id}"}

class AuthService:
    def __init__(self, db_client: DatabaseClient = Depends(DatabaseClient)):
        self.db_client = db_client
    
    async def authenticate(self, token: str):
        # Simulate authentication
        await asyncio.sleep(0.01)
        if token == "valid_token":
            return {"user_id": 1, "username": "testuser"}
        return None

# Example dependencies
async def get_current_user(auth_service: AuthService = Depends(AuthService)):
    token = "valid_token"  # In a real app, this would come from headers
    user = await auth_service.authenticate(token)
    if not user:
        raise Exception("Invalid token")
    return user

# Simplified example handler
async def user_endpoint(
    current_user = Depends(get_current_user)
):
    return {
        "current_user": current_user
    }

# Example usage
async def main():
    # Create lifecycle manager
    lifecycle = LifecycleManager()
    
    # Register services
    db_client = DatabaseClient()
    auth_service = AuthService(db_client)
    
    lifecycle.register(db_client)
    lifecycle.register(auth_service)
    
    # Run startup
    await lifecycle.run_startup()
    
    # Create resolver and binder
    resolver = DependencyResolver()
    binder = HandlerBinder(resolver)
    
    # Create a mock request
    class MockRequest:
        def __init__(self):
            self.state = {}
    
    request = MockRequest()
    cache = DependencyCache(request.state)
    
    # Call the handler
    result = await binder.bind_and_call(
        handler=user_endpoint,
        path_params={},
        query_params={},
        body=None,
        cache=cache
    )
    
    print("Result:", result)
    
    # Run shutdown
    await lifecycle.run_shutdown()

if __name__ == "__main__":
    asyncio.run(main())