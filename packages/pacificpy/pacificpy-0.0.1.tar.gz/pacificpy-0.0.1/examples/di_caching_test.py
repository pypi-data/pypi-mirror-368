"""
Test to verify dependency caching works correctly
"""
import asyncio
from pacificpy.di import Depends, DependencyResolver, DependencyCache

# Counter to track how many times a dependency is created
db_client_creation_count = 0

class DatabaseClient:
    def __init__(self):
        global db_client_creation_count
        db_client_creation_count += 1
        self.id = db_client_creation_count
        print(f"Created DatabaseClient #{self.id}")
    
    async def get_user(self, user_id: int):
        return {"id": user_id, "name": f"User {user_id}"}

class AuthService:
    def __init__(self, db_client: DatabaseClient = Depends(DatabaseClient)):
        self.db_client = db_client
    
    async def authenticate(self, token: str):
        # Use the db_client to authenticate
        user = await self.db_client.get_user(1)
        if token == "valid_token":
            return {"user_id": user["id"], "username": "testuser"}
        return None

async def get_current_user(auth_service: AuthService = Depends(AuthService)):
    token = "valid_token"
    user = await auth_service.authenticate(token)
    return user

async def handler_with_multiple_deps(
    user1 = Depends(get_current_user),
    user2 = Depends(get_current_user),
    db_client: DatabaseClient = Depends(DatabaseClient)
):
    """Handler that depends on the same dependency multiple times."""
    return {
        "user1": user1,
        "user2": user2,
        "db_client_id": db_client.id
    }

async def main():
    global db_client_creation_count
    db_client_creation_count = 0  # Reset counter
    
    # Create resolver and mock request
    resolver = DependencyResolver()
    
    class MockRequest:
        def __init__(self):
            self.state = {}
    
    request = MockRequest()
    cache = DependencyCache(request.state)
    
    # Call the handler
    dependencies = await resolver.resolve_dependencies(handler_with_multiple_deps, cache)
    result = await handler_with_multiple_deps(**dependencies)
    
    print("Result:", result)
    
    # Verify that the DatabaseClient was only created once (cached)
    print(f"DatabaseClient was created {db_client_creation_count} time(s)")
    
    if db_client_creation_count == 1:
        print("✅ Caching works correctly - DatabaseClient was reused!")
    else:
        print("❌ Caching failed - DatabaseClient was created multiple times")

if __name__ == "__main__":
    asyncio.run(main())