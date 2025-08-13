# Caching Guide for PacificPy

This guide covers caching patterns and cache invalidation strategies in PacificPy.

## Overview

PacificPy provides a comprehensive caching system with support for multiple backends, ETags, and automatic cache invalidation.

## Cache Decorator

The `@cache` decorator is the primary way to cache endpoint responses.

### Basic Usage

```python
from pacificpy.cache.decorators import cache

@app.get("/users")
@cache(ttl=300)  # Cache for 5 minutes
async def get_users(request):
    users = await fetch_users_from_database()
    return users
```

### Configuring Cache Backend

```python
from pacificpy.cache.decorators import configure_cache
from pacificpy.cache.backends.memory import get_memory_cache
from pacificpy.cache.backends.redis import configure_redis_cache

# Memory cache (default)
memory_cache = get_memory_cache(max_size=1000, default_ttl=600)
configure_cache(backend=memory_cache)

# Redis cache
redis_cache = configure_redis_cache(
    url="redis://localhost:6379/0",
    prefix="myapp:",
    default_ttl=600
)
configure_cache(backend=redis_cache)
```

### Custom Cache Keys

```python
@app.get("/users")
@cache(ttl=300, key_func=lambda request: f"users:{request.query_params.get('page', 1)}")
async def get_users(request):
    page = request.query_params.get("page", 1)
    users = await fetch_users_page(page)
    return users
```

## ETag Support

ETags provide a way to validate cached content without transferring it.

### Automatic ETags

```python
from pacificpy.cache.etag import ETagMiddleware

# Add ETag middleware to app
app.add_middleware(ETagMiddleware)

@app.get("/resource")
async def get_resource(request):
    resource = await fetch_resource()
    return resource
```

### Manual ETags

```python
from pacificpy.cache.etag import etag

@app.get("/users/{id}")
@etag(key_func=lambda request: f"user:{request.path_params['id']}")
async def get_user(request):
    user = await fetch_user(request.path_params["id"])
    return user
```

## Cache Invalidation

### Automatic Invalidation

Cache is automatically invalidated when content changes:

```python
@app.post("/users")
async def create_user(request):
    user = await create_user_in_database(request.json())
    
    # Cache is automatically invalidated for GET /users
    return user
```

### Manual Invalidation

```python
from pacificpy.cache.decorators import invalidate_cache, invalidate_cache_key

@app.put("/users/{id}")
async def update_user(request):
    user = await update_user_in_database(request.path_params["id"], request.json())
    
    # Manually invalidate cache
    await invalidate_cache_key(f"user:{request.path_params['id']}")
    
    return user

@app.delete("/users/{id}")
async def delete_user(request):
    await delete_user_from_database(request.path_params["id"])
    
    # Invalidate multiple cache keys
    await invalidate_cache_key(f"user:{request.path_params['id']}")
    await invalidate_cache_key("users_list")
    
    return {"status": "deleted"}
```

## Cache Patterns

### 1. Write-Through Caching

```python
@app.get("/users/{id}")
@cache(ttl=300)
async def get_user(request):
    user = await fetch_user_from_cache_or_db(request.path_params["id"])
    return user

async def fetch_user_from_cache_or_db(user_id):
    # Try cache first
    cached = await cache_backend.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    user = await fetch_user_from_database(user_id)
    
    # Store in cache
    await cache_backend.set(f"user:{user_id}", json.dumps(user), ttl=300)
    
    return user
```

### 2. Write-Behind Caching

```python
@app.put("/users/{id}")
async def update_user(request):
    # Update database
    user = await update_user_in_database(request.path_params["id"], request.json())
    
    # Update cache asynchronously
    asyncio.create_task(
        cache_backend.set(f"user:{request.path_params['id']}", json.dumps(user), ttl=300)
    )
    
    return user
```

### 3. Cache-Aside Pattern

```python
@app.get("/expensive-operation")
async def expensive_operation(request):
    cache_key = "expensive_result"
    
    # Try cache first
    cached = await cache_backend.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Perform expensive operation
    result = await perform_expensive_operation()
    
    # Cache result
    await cache_backend.set(cache_key, json.dumps(result), ttl=600)
    
    return result
```

## Cache Statistics

Monitor cache performance with built-in statistics:

```python
from pacificpy.cache.backends.memory import get_memory_cache

# Get cache statistics
@app.get("/cache-stats")
async def cache_stats(request):
    memory_cache = get_memory_cache()
    stats = memory_cache.get_stats()
    return stats

# Reset statistics
@app.post("/cache-stats/reset")
async def reset_cache_stats(request):
    memory_cache = get_memory_cache()
    memory_cache.reset_stats()
    return {"status": "reset"}
```

## Best Practices

### 1. Cache Key Design

- Use consistent, descriptive cache keys
- Include relevant parameters in cache keys
- Avoid caching sensitive data

```python
# Good cache key
cache_key = f"user:{user_id}:profile"

# Better cache key with versioning
cache_key = f"user:{user_id}:profile:v2"
```

### 2. TTL Strategy

- Set appropriate TTL for different types of data
- Use shorter TTL for frequently changing data
- Use longer TTL for static data

```python
# Short TTL for user sessions
@cache(ttl=300)  # 5 minutes
async def get_user_session(request):
    pass

# Long TTL for static content
@cache(ttl=86400)  # 24 hours
async def get_static_content(request):
    pass
```

### 3. Cache Invalidation

- Invalidate cache when data changes
- Use pattern-based invalidation for related data
- Consider lazy invalidation for non-critical data

```python
# Invalidate all user-related cache
async def invalidate_user_cache(user_id):
    await invalidate_cache_key(f"user:{user_id}")
    await invalidate_cache_key(f"user:{user_id}:profile")
    await invalidate_cache_key("users_list")
```

### 4. Memory Management

- Set appropriate cache size limits
- Monitor cache hit rates
- Use compression for large values

```python
# Configure memory cache with size limit
memory_cache = get_memory_cache(max_size=10000)
```

### 5. Error Handling

- Handle cache failures gracefully
- Don't let cache issues break application functionality
- Log cache errors for monitoring

```python
try:
    cached = await cache_backend.get(cache_key)
except Exception as e:
    # Log error but continue
    logger.error(f"Cache error: {e}")
    cached = None
```

## Security Considerations

### 1. Cache Poisoning

- Validate cache keys
- Sanitize user input used in cache keys
- Use secure random keys for sensitive data

```python
# Validate cache key
if not re.match(r"^[a-zA-Z0-9:_-]+$", cache_key):
    raise HTTPException(400, "Invalid cache key")
```

### 2. Sensitive Data

- Don't cache sensitive user data
- Encrypt cached sensitive data
- Use separate cache namespaces for sensitive data

```python
# Don't cache sensitive data
@app.get("/user/{id}/sensitive")
async def get_sensitive_user_data(request):
    # Don't use @cache decorator
    user = await fetch_sensitive_user_data(request.path_params["id"])
    return user
```

## Example Implementation

Here's a complete example of caching in a PacificPy application:

```python
from pacificpy import PacificPy
from pacificpy.cache.decorators import configure_cache, cache
from pacificpy.cache.backends.redis import configure_redis_cache
from pacificpy.cache.etag import ETagMiddleware

# Create app
app = PacificPy()

# Configure cache
redis_cache = configure_redis_cache(
    url="redis://localhost:6379/0",
    prefix="myapp:",
    default_ttl=600
)
configure_cache(backend=redis_cache)

# Add ETag middleware
app.add_middleware(ETagMiddleware)

# Cached endpoints
@app.get("/users")
@cache(ttl=300)
async def get_users(request):
    users = await fetch_users_from_database()
    return users

@app.get("/users/{id}")
@cache(ttl=600)
async def get_user(request):
    user = await fetch_user_from_database(request.path_params["id"])
    return user

@app.post("/users")
async def create_user(request):
    user = await create_user_in_database(request.json())
    
    # Invalidate cache
    await invalidate_cache_key("users_list")
    
    return user

@app.put("/users/{id}")
async def update_user(request):
    user = await update_user_in_database(request.path_params["id"], request.json())
    
    # Invalidate cache
    await invalidate_cache_key(f"user:{request.path_params['id']}")
    await invalidate_cache_key("users_list")
    
    return user

if __name__ == "__main__":
    app.run()
```

This guide provides a comprehensive overview of caching in PacificPy with practical examples and best practices. Follow these patterns to build efficient, scalable applications with effective caching strategies.