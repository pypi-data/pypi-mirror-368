"""
Redis client helper for PacificPy.

This module provides a wrapper for aioredis/redis with connection pooling,
health checks, and retry policies.
"""

import asyncio
import time
from typing import Any, Optional, Dict, Union
from contextlib import asynccontextmanager

# Try to import aioredis for async support
try:
    import aioredis
    AIREDIS_AVAILABLE = True
except ImportError:
    AIREDIS_AVAILABLE = False

# Try to import redis for sync support
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class RedisClient:
    """Redis client wrapper with connection pooling and health checks."""
    
    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        max_connections: int = 10,
        health_check_interval: int = 30,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ):
        """
        Initialize the Redis client.
        
        Args:
            url: The Redis connection URL
            max_connections: Maximum number of connections in the pool
            health_check_interval: Health check interval in seconds
            retry_attempts: Number of retry attempts for failed operations
            retry_delay: Delay between retry attempts in seconds
            **kwargs: Additional arguments for Redis connection
        """
        self.url = url
        self.max_connections = max_connections
        self.health_check_interval = health_check_interval
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.kwargs = kwargs
        
        # Connection pool
        self.pool: Optional[Union[aioredis.ConnectionPool, redis.ConnectionPool]] = None
        
        # Redis client
        self.client: Optional[Union[aioredis.Redis, redis.Redis]] = None
        
        # Health check task
        self._health_check_task: Optional[asyncio.Task] = None
        self._last_health_check: float = 0.0
        self._healthy: bool = True
    
    async def connect(self) -> None:
        """Connect to Redis and initialize the connection pool."""
        if AIREDIS_AVAILABLE:
            # Async connection
            self.pool = aioredis.ConnectionPool.from_url(
                self.url,
                max_connections=self.max_connections,
                **self.kwargs
            )
            self.client = aioredis.Redis(connection_pool=self.pool)
        elif REDIS_AVAILABLE:
            # Sync connection
            self.pool = redis.ConnectionPool.from_url(
                self.url,
                max_connections=self.max_connections,
                **self.kwargs
            )
            self.client = redis.Redis(connection_pool=self.pool)
        else:
            raise RuntimeError("Either aioredis or redis package is required")
        
        # Start health check
        self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def disconnect(self) -> None:
        """Disconnect from Redis and close the connection pool."""
        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Close connections
        if self.client:
            if AIREDIS_AVAILABLE and isinstance(self.client, aioredis.Redis):
                await self.client.close()
            elif REDIS_AVAILABLE and isinstance(self.client, redis.Redis):
                self.client.close()
    
    async def _health_check_loop(self) -> None:
        """Run health checks in a loop."""
        while True:
            try:
                await self._health_check()
                self._healthy = True
            except Exception:
                self._healthy = False
            
            await asyncio.sleep(self.health_check_interval)
    
    async def _health_check(self) -> None:
        """Perform a health check."""
        if not self.client:
            raise RuntimeError("Redis client not initialized")
        
        # Ping the Redis server
        if AIREDIS_AVAILABLE and isinstance(self.client, aioredis.Redis):
            await self.client.ping()
        elif REDIS_AVAILABLE and isinstance(self.client, redis.Redis):
            self.client.ping()
        
        self._last_health_check = time.time()
    
    def is_healthy(self) -> bool:
        """Check if Redis is healthy."""
        return self._healthy
    
    async def execute(self, command: str, *args, **kwargs) -> Any:
        """
        Execute a Redis command with retry logic.
        
        Args:
            command: The Redis command to execute
            *args: Arguments for the command
            **kwargs: Keyword arguments for the command
            
        Returns:
            The result of the command
            
        Raises:
            Exception: If the command fails after all retries
        """
        if not self.client:
            raise RuntimeError("Redis client not initialized")
        
        # Check health
        if not self.is_healthy():
            raise RuntimeError("Redis is not healthy")
        
        # Retry logic
        for attempt in range(self.retry_attempts):
            try:
                if AIREDIS_AVAILABLE and isinstance(self.client, aioredis.Redis):
                    # Async execution
                    return await getattr(self.client, command)(*args, **kwargs)
                elif REDIS_AVAILABLE and isinstance(self.client, redis.Redis):
                    # Sync execution
                    return getattr(self.client, command)(*args, **kwargs)
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    # Last attempt, re-raise the exception
                    raise e
                
                # Wait before retrying
                await asyncio.sleep(self.retry_delay)
        
        # This should never be reached
        raise RuntimeError("Unexpected error in execute method")
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get a Redis connection as an async context manager.
        
        Yields:
            A Redis connection
        """
        if not self.client:
            raise RuntimeError("Redis client not initialized")
        
        # Check health
        if not self.is_healthy():
            raise RuntimeError("Redis is not healthy")
        
        # For aioredis, we can use the client directly
        # For redis, we would need to manage connections differently
        try:
            yield self.client
        finally:
            # Connection is automatically returned to pool
            pass
    
    async def get_db(self):
        """
        Get a Redis connection for dependency injection.
        
        Yields:
            A Redis connection
        """
        async with self.get_connection() as connection:
            yield connection
    
    # Common Redis operations
    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        return await self.execute("get", key)
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set a value in Redis."""
        return await self.execute("set", key, value, ex=ex)
    
    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis."""
        return await self.execute("delete", *keys)
    
    async def exists(self, *keys: str) -> int:
        """Check if keys exist in Redis."""
        return await self.execute("exists", *keys)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set a key's expiration time."""
        return await self.execute("expire", key, seconds)
    
    async def ttl(self, key: str) -> int:
        """Get a key's time to live."""
        return await self.execute("ttl", key)

# Global Redis client instance
_redis_client: Optional[RedisClient] = None

def configure_redis(
    url: str = "redis://localhost:6379/0",
    max_connections: int = 10,
    health_check_interval: int = 30,
    retry_attempts: int = 3,
    retry_delay: float = 1.0,
    **kwargs
) -> RedisClient:
    """
    Configure the global Redis client.
    
    Args:
        url: The Redis connection URL
        max_connections: Maximum number of connections in the pool
        health_check_interval: Health check interval in seconds
        retry_attempts: Number of retry attempts for failed operations
        retry_delay: Delay between retry attempts in seconds
        **kwargs: Additional arguments for Redis connection
        
    Returns:
        The Redis client instance
    """
    global _redis_client
    _redis_client = RedisClient(
        url=url,
        max_connections=max_connections,
        health_check_interval=health_check_interval,
        retry_attempts=retry_attempts,
        retry_delay=retry_delay,
        **kwargs
    )
    return _redis_client

async def init_redis() -> None:
    """
    Initialize the Redis client using the global instance.
    
    Raises:
        RuntimeError: If Redis client is not configured
    """
    if not _redis_client:
        raise RuntimeError("Redis client not configured")
    
    await _redis_client.connect()

async def close_redis() -> None:
    """
    Close the Redis client using the global instance.
    
    Raises:
        RuntimeError: If Redis client is not configured
    """
    if not _redis_client:
        raise RuntimeError("Redis client not configured")
    
    await _redis_client.disconnect()

async def get_db():
    """
    Get a Redis connection using the global client.
    
    Yields:
        A Redis connection
        
    Raises:
        RuntimeError: If Redis client is not configured
    """
    if not _redis_client:
        raise RuntimeError("Redis client not configured")
    
    async for connection in _redis_client.get_db():
        yield connection

# Example usage:
"""
# In your app setup:
configure_redis(
    url="redis://localhost:6379/0",
    max_connections=20,
    health_check_interval=60
)

# Initialize Redis
await init_redis()

# In your routes:
@app.get("/cache/{key}")
async def get_cache(key: str, redis = Depends(get_db)):
    value = await redis.get(key)
    return {"key": key, "value": value}

@app.post("/cache/{key}")
async def set_cache(key: str, value: str, redis = Depends(get_db)):
    await redis.set(key, value, ex=3600)  # Expire in 1 hour
    return {"key": key, "value": value}
"""