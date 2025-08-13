"""
Tortoise ORM plugin for PacificPy.

This module provides a plugin for integrating Tortoise ORM with PacificPy,
including model discovery and lifecycle hooks.
"""

import os
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager

# Try to import Tortoise ORM
try:
    from tortoise import Tortoise, connections
    from tortoise.connection import ConnectionHandler
    from tortoise.models import Model
    TORTOISE_AVAILABLE = True
except ImportError:
    TORTOISE_AVAILABLE = False

class TortoisePlugin:
    """Plugin for Tortoise ORM integration."""
    
    def __init__(
        self,
        database_url: str = None,
        modules: Dict[str, List[str]] = None,
        config: Dict[str, Any] = None,
        generate_schemas: bool = False,
    ):
        """
        Initialize the Tortoise ORM plugin.
        
        Args:
            database_url: The database URL
            modules: Modules for model discovery
            config: Tortoise configuration
            generate_schemas: Whether to generate schemas on init
        """
        if not TORTOISE_AVAILABLE:
            raise RuntimeError("Tortoise ORM is required for TortoisePlugin")
        
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.modules = modules
        self.config = config
        self.generate_schemas = generate_schemas
        
        # Build configuration if not provided
        if not self.config:
            self.config = self._build_config()
    
    def _build_config(self) -> Dict[str, Any]:
        """Build Tortoise configuration."""
        config = {
            "connections": {
                "default": self.database_url
            },
            "apps": {}
        }
        
        # Add modules for model discovery
        if self.modules:
            for app_name, module_list in self.modules.items():
                config["apps"][app_name] = {
                    "models": module_list,
                    "default_connection": "default",
                }
        else:
            # Default app configuration
            config["apps"]["models"] = {
                "models": ["__main__"],  # Default to main module
                "default_connection": "default",
            }
        
        return config
    
    async def init(self) -> None:
        """Initialize Tortoise ORM."""
        await Tortoise.init(
            config=self.config,
            generate_schemas=self.generate_schemas
        )
    
    async def close(self) -> None:
        """Close Tortoise ORM connections."""
        await connections.close_all()
    
    @asynccontextmanager
    async def get_connection(self, connection_name: str = "default"):
        """
        Get a database connection as an async context manager.
        
        Args:
            connection_name: The name of the connection to get
            
        Yields:
            A database connection
        """
        connection = connections.get(connection_name)
        try:
            yield connection
        finally:
            # Connection is automatically returned to pool
            pass
    
    async def get_db(self):
        """
        Get a database connection for dependency injection.
        
        Yields:
            A database connection
        """
        async with self.get_connection() as connection:
            yield connection
    
    def register_models(self, models: List[Union[str, type]]) -> None:
        """
        Register models with Tortoise.
        
        Args:
            models: List of model classes or module paths
        """
        # This method would be used to register models programmatically
        # In Tortoise, models are typically discovered automatically
        # but this provides a way to register them manually if needed
        pass
    
    async def generate_schemas(self) -> None:
        """Generate database schemas."""
        await Tortoise.generate_schemas()
    
    async def drop_schemas(self) -> None:
        """Drop database schemas."""
        # Note: This is a destructive operation
        await Tortoise._drop_databases()
    
    def get_dependency(self):
        """
        Get a dependency for database connections.
        
        Returns:
            A dependency for database connections
        """
        from ...di import Dependency
        return Dependency(self.get_db)

# Global Tortoise plugin instance
_tortoise_plugin: Optional[TortoisePlugin] = None

def configure_tortoise(
    database_url: str = None,
    modules: Dict[str, List[str]] = None,
    config: Dict[str, Any] = None,
    generate_schemas: bool = False,
) -> TortoisePlugin:
    """
    Configure the global Tortoise ORM plugin.
    
    Args:
        database_url: The database URL
        modules: Modules for model discovery
        config: Tortoise configuration
        generate_schemas: Whether to generate schemas on init
        
    Returns:
        The Tortoise plugin instance
    """
    global _tortoise_plugin
    _tortoise_plugin = TortoisePlugin(
        database_url=database_url,
        modules=modules,
        config=config,
        generate_schemas=generate_schemas,
    )
    return _tortoise_plugin

async def init_tortoise() -> None:
    """
    Initialize Tortoise ORM using the global plugin.
    
    Raises:
        RuntimeError: If Tortoise plugin is not configured
    """
    if not _tortoise_plugin:
        raise RuntimeError("Tortoise plugin not configured")
    
    await _tortoise_plugin.init()

async def close_tortoise() -> None:
    """
    Close Tortoise ORM connections using the global plugin.
    
    Raises:
        RuntimeError: If Tortoise plugin is not configured
    """
    if not _tortoise_plugin:
        raise RuntimeError("Tortoise plugin not configured")
    
    await _tortoise_plugin.close()

async def get_db():
    """
    Get a database connection using the global plugin.
    
    Yields:
        A database connection
        
    Raises:
        RuntimeError: If Tortoise plugin is not configured
    """
    if not _tortoise_plugin:
        raise RuntimeError("Tortoise plugin not configured")
    
    async for connection in _tortoise_plugin.get_db():
        yield connection

# Example usage:
"""
# In your app setup:
configure_tortoise(
    database_url="sqlite://db.sqlite3",
    modules={"models": ["app.models"]},
    generate_schemas=True
)

# Initialize Tortoise
await init_tortoise()

# In your models:
from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100)

# In your routes:
@app.get("/users")
async def get_users(db = Depends(get_db)):
    users = await User.all()
    return [user.__dict__ for user in users]
"""