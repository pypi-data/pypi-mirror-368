# PacificPy Dependency Injection

## Quickstart

This guide will show you how to use PacificPy's dependency injection system with a simple example.

### 1. Basic Service

First, let's create a simple service:

```python
# services.py
import asyncio

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
    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client
    
    async def authenticate(self, token: str):
        # Simulate authentication
        await asyncio.sleep(0.01)
        if token == "valid_token":
            return {"user_id": 1, "username": "testuser"}
        return None
```

### 2. Using Dependencies in Handlers

Now let's create a handler that uses these services:

```python
# handlers.py
from pacificpy.di import Depends
from .services import DatabaseClient, AuthService

async def get_current_user(auth_service: AuthService = Depends(AuthService)):
    token = "valid_token"  # In a real app, this would come from headers
    user = await auth_service.authenticate(token)
    if not user:
        raise Exception("Invalid token")
    return user

async def get_user(user_id: int, db_client: DatabaseClient = Depends(DatabaseClient)):
    return await db_client.get_user(user_id)

async def user_endpoint(
    user_id: int,
    current_user = Depends(get_current_user),
    user = Depends(get_user)
):
    return {
        "current_user": current_user,
        "requested_user": user
    }
```

### 3. Override Dependencies for Testing

For testing, you can override dependencies:

```python
# test_handlers.py
import asyncio
from pacificpy.di import override_dependencies
from .handlers import user_endpoint
from .services import DatabaseClient, AuthService

class MockDatabaseClient:
    async def get_user(self, user_id: int):
        return {"id": user_id, "name": f"Mock User {user_id}", "mock": True}

class MockAuthService:
    async def authenticate(self, token: str):
        return {"user_id": 999, "username": "mockuser"}

async def test_user_endpoint():
    # Override dependencies with mocks
    overrides = {
        DatabaseClient: MockDatabaseClient,
        AuthService: MockAuthService
    }
    
    with override_dependencies(overrides):
        result = await user_endpoint(user_id=1)
        print(result)
        # Output: {
        #     "current_user": {"user_id": 999, "username": "mockuser"}, 
        #     "requested_user": {"id": 1, "name": "Mock User 1", "mock": True}
        # }

# Run the test
asyncio.run(test_user_endpoint())
```

### 4. Running the Application

To run the application with lifecycle management:

```python
# main.py
import asyncio
from pacificpy.di import LifecycleManager
from .services import DatabaseClient, AuthService

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
    
    # Your application would run here
    print("Application is running...")
    
    # Run shutdown
    await lifecycle.run_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

This example demonstrates:
- Defining services with startup/shutdown methods
- Using `Depends()` to inject dependencies into handlers
- Overriding dependencies for testing
- Managing the lifecycle of dependencies