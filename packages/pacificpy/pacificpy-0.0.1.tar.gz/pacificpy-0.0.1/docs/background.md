# Background Tasks Guide for PacificPy

This guide covers background task patterns and scaling considerations in PacificPy.

## Overview

PacificPy provides a flexible background task system with support for multiple backends including local execution, Celery, and ARQ.

## When to Use Background Tasks

### 1. Long-Running Operations

```python
# Send emails asynchronously
@background
def send_email(to: str, subject: str, body: str):
    # Email sending logic
    pass

@app.post("/notifications")
async def send_notification(request):
    data = await request.json()
    await send_email.delay(data["to"], data["subject"], data["body"])
    return {"status": "Email queued"}
```

### 2. External API Calls

```python
# Process payments without blocking the request
@background
def process_payment(payment_data: dict):
    # External payment API call
    pass
```

### 3. Data Processing

```python
# Generate reports in the background
@background
def generate_report(user_id: int, report_type: str):
    # Report generation logic
    pass
```

## Backend Selection

### Local Executor (Development)

```python
from pacificpy.background.local import get_local_executor
from pacificpy.background.decorators import configure_background_tasks

# Use local executor for development
local_executor = get_local_executor(max_workers=4)
configure_background_tasks(local_executor)
```

### Celery (Production)

```python
from celery import Celery
from pacificpy.background.backend import CeleryBackgroundBackend

# Configure Celery
celery_app = Celery('myapp', broker='redis://localhost:6379/0')
celery_backend = CeleryBackgroundBackend(celery_app=celery_app)
configure_background_tasks(celery_backend)
```

### ARQ (Async-First)

```python
from arq.connections import RedisSettings
from pacificpy.background.backend import ARQBackgroundBackend

# Configure ARQ
arq_backend = ARQBackgroundBackend(
    redis_settings=RedisSettings(host='localhost', port=6379)
)
configure_background_tasks(arq_backend)
```

## Task Design Patterns

### 1. Idempotency

Design tasks to be idempotent so they can be safely retried:

```python
@background
def update_user_profile(user_id: int, profile_data: dict):
    # Check if update was already applied
    if is_profile_updated(user_id, profile_data):
        return {"status": "already_updated"}
    
    # Apply update
    result = apply_profile_update(user_id, profile_data)
    return result
```

### 2. Retry Logic

Implement retry logic for transient failures:

```python
import time
import random

@background
def process_with_retry(data: dict, max_retries: int = 3):
    for attempt in range(max_retries + 1):
        try:
            return process_data(data)
        except TransientError as e:
            if attempt == max_retries:
                raise e
            
            # Exponential backoff
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

### 3. Task Chaining

Chain tasks for complex workflows:

```python
@background
def step_one(data: dict):
    result = process_step_one(data)
    # Enqueue next step
    step_two.delay(result)
    return result

@background
def step_two(data: dict):
    result = process_step_two(data)
    # Enqueue final step
    step_three.delay(result)
    return result

@background
def step_three(data: dict):
    return process_step_three(data)
```

## Error Handling

### Graceful Error Handling

```python
import logging

logger = logging.getLogger(__name__)

@background
def robust_task(data: dict):
    try:
        result = process_data(data)
        return result
    except Exception as e:
        logger.error(f"Task failed: {e}", exc_info=True)
        # Store error for debugging
        store_error(data, str(e))
        # Re-raise for retry logic
        raise
```

### Dead Letter Queue

Handle tasks that fail repeatedly:

```python
@background
def dlq_task(data: dict, retry_count: int = 0):
    max_retries = 5
    
    try:
        return process_data(data)
    except Exception as e:
        if retry_count >= max_retries:
            # Move to dead letter queue
            send_to_dlq(data, str(e))
            return {"status": "moved_to_dlq"}
        
        # Re-raise for retry
        raise
```

## Monitoring and Observability

### Task Monitoring

```python
from pacificpy.background.monitor import record_task_start, update_task_status

@background
def monitored_task(data: dict):
    task_id = str(uuid.uuid4())  # Or get from context
    record_task_start(task_id, "monitored_task")
    
    try:
        result = process_data(data)
        update_task_status(task_id, "completed", result)
        return result
    except Exception as e:
        update_task_status(task_id, "failed", str(e))
        raise
```

### Metrics Collection

```python
import time

@background
def timed_task(data: dict):
    start_time = time.time()
    
    try:
        result = process_data(data)
        duration = time.time() - start_time
        # Record metrics
        record_metric("task_duration", duration)
        return result
    except Exception as e:
        duration = time.time() - start_time
        record_metric("task_failure_duration", duration)
        raise
```

## Scaling Considerations

### 1. Worker Scaling

Scale workers based on task load:

```python
# Celery worker scaling
# celery -A myapp worker --concurrency=10

# ARQ worker scaling
# arq myapp.WorkerSettings --workers 4
```

### 2. Queue Management

Monitor queue lengths and processing rates:

```python
# Monitor queue length
def get_queue_length():
    # Implementation depends on backend
    pass

# Alert on queue backlog
def check_queue_backlog():
    if get_queue_length() > 1000:
        send_alert("High queue backlog detected")
```

### 3. Resource Management

Control resource usage per worker:

```python
# Limit memory usage
@background
def memory_efficient_task(data: list):
    # Process data in chunks
    for chunk in chunk_list(data, 100):
        process_chunk(chunk)
```

## Best Practices

### 1. Task Size

Keep tasks small and focused:

```python
# Good: Small, focused tasks
@background
def send_notification(user_id: int, message: str):
    pass

# Avoid: Large, complex tasks
@background
def do_everything(user_data: dict):
    # This is too broad
    pass
```

### 2. Data Serialization

Use efficient data serialization:

```python
# Use JSON for simple data
@background
def process_simple_data(data: dict):
    pass

# Use pickle for complex objects (be careful)
@background
def process_complex_data(data: object):
    # Only if necessary
    pass
```

### 3. Timeout Management

Set appropriate timeouts:

```python
# Celery task with timeout
@app.task(soft_time_limit=30, time_limit=60)
def long_running_task():
    pass
```

### 4. Security

Avoid processing sensitive data in background tasks:

```python
# Store sensitive data separately
@background
def process_user_data(user_id: int):
    # Fetch sensitive data inside task
    user_data = fetch_user_data(user_id)
    process_data(user_data)
```

## Example Implementation

Here's a complete example of background tasks in a PacificPy application:

```python
from pacificpy import PacificPy
from pacificpy.background.local import get_local_executor
from pacificpy.background.decorators import background, configure_background_tasks
from pacificpy.background.monitor import configure_task_monitor

# Create app
app = PacificPy()

# Configure background tasks
local_executor = get_local_executor(max_workers=4)
configure_background_tasks(local_executor)

# Configure task monitoring
configure_task_monitor()

# Background tasks
@background
def send_welcome_email(user_id: int):
    # Simulate email sending
    import time
    time.sleep(2)
    print(f"Welcome email sent to user {user_id}")
    return {"status": "sent", "user_id": user_id}

@background
def process_user_upload(file_path: str):
    # Simulate file processing
    import time
    time.sleep(5)
    print(f"File processed: {file_path}")
    return {"status": "processed", "file_path": file_path}

# Routes
@app.post("/users")
async def create_user(request):
    data = await request.json()
    user_id = create_user_in_database(data)
    
    # Send welcome email in background
    await send_welcome_email.delay(user_id)
    
    return {"user_id": user_id, "message": "User created"}

@app.post("/uploads")
async def upload_file(request):
    data = await request.json()
    file_path = data["file_path"]
    
    # Process file in background
    await process_user_upload.delay(file_path)
    
    return {"message": "File upload received"}

if __name__ == "__main__":
    app.run()
```

This guide provides a comprehensive overview of background task patterns and scaling considerations in PacificPy. Follow these practices to build robust, scalable applications with efficient background processing.