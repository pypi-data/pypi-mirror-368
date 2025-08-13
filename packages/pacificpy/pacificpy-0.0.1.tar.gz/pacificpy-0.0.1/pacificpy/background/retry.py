"""
Retry policy helpers for background tasks in PacificPy.

This module provides retry decorators with exponential backoff, jitter,
and max attempts, pluggable into various backends.
"""

import asyncio
import functools
import random
import time
from typing import Any, Callable, Dict, Optional, Type, Union
import logging

logger = logging.getLogger(__name__)

class RetryPolicy:
    """Retry policy configuration."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        min_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_on_exceptions: tuple = (Exception,),
    ):
        """
        Initialize a retry policy.
        
        Args:
            max_attempts: Maximum number of attempts (0 = infinite)
            min_delay: Minimum delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add jitter to delays
            retry_on_exceptions: Tuple of exceptions to retry on
        """
        self.max_attempts = max_attempts
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_on_exceptions = retry_on_exceptions

def retry(
    policy: RetryPolicy = None,
    max_attempts: int = 3,
    min_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_on_exceptions: tuple = (Exception,),
):
    """
    Decorator to retry a function with exponential backoff and jitter.
    
    Args:
        policy: Retry policy to use (if provided, other args are ignored)
        max_attempts: Maximum number of attempts (0 = infinite)
        min_delay: Minimum delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add jitter to delays
        retry_on_exceptions: Tuple of exceptions to retry on
        
    Returns:
        The decorated function
    """
    if policy is None:
        policy = RetryPolicy(
            max_attempts=max_attempts,
            min_delay=min_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            retry_on_exceptions=retry_on_exceptions,
        )
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _retry_async(func, policy, *args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _retry_sync(func, policy, *args, **kwargs)
        
        # Check if function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

async def _retry_async(func: Callable, policy: RetryPolicy, *args, **kwargs) -> Any:
    """
    Retry an async function.
    
    Args:
        func: The function to retry
        policy: The retry policy
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        The result of the function
    """
    last_exception = None
    
    for attempt in range(policy.max_attempts or 999999):
        try:
            return await func(*args, **kwargs)
        except policy.retry_on_exceptions as e:
            last_exception = e
            
            # Check if we should retry
            if policy.max_attempts > 0 and attempt >= policy.max_attempts - 1:
                logger.error(f"Function {func.__name__} failed after {attempt + 1} attempts: {e}")
                raise e
            
            # Calculate delay
            delay = _calculate_delay(policy, attempt)
            
            logger.warning(
                f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                f"Retrying in {delay:.2f} seconds..."
            )
            
            # Wait before retrying
            await asyncio.sleep(delay)
    
    # This should never be reached if max_attempts > 0
    if last_exception:
        raise last_exception

def _retry_sync(func: Callable, policy: RetryPolicy, *args, **kwargs) -> Any:
    """
    Retry a sync function.
    
    Args:
        func: The function to retry
        policy: The retry policy
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        The result of the function
    """
    last_exception = None
    
    for attempt in range(policy.max_attempts or 999999):
        try:
            return func(*args, **kwargs)
        except policy.retry_on_exceptions as e:
            last_exception = e
            
            # Check if we should retry
            if policy.max_attempts > 0 and attempt >= policy.max_attempts - 1:
                logger.error(f"Function {func.__name__} failed after {attempt + 1} attempts: {e}")
                raise e
            
            # Calculate delay
            delay = _calculate_delay(policy, attempt)
            
            logger.warning(
                f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                f"Retrying in {delay:.2f} seconds..."
            )
            
            # Wait before retrying
            time.sleep(delay)
    
    # This should never be reached if max_attempts > 0
    if last_exception:
        raise last_exception

def _calculate_delay(policy: RetryPolicy, attempt: int) -> float:
    """
    Calculate delay with exponential backoff and jitter.
    
    Args:
        policy: The retry policy
        attempt: The current attempt number (0-indexed)
        
    Returns:
        The delay in seconds
    """
    # Calculate exponential delay
    delay = policy.min_delay * (policy.exponential_base ** attempt)
    
    # Cap at max_delay
    delay = min(delay, policy.max_delay)
    
    # Add jitter if enabled
    if policy.jitter:
        jitter_amount = delay * 0.1  # 10% jitter
        delay += random.uniform(-jitter_amount, jitter_amount)
    
    # Ensure delay is not negative
    delay = max(delay, 0)
    
    return delay

# Predefined retry policies
RETRY_POLICY_DEFAULT = RetryPolicy(
    max_attempts=3,
    min_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
)

RETRY_POLICY_AGGRESSIVE = RetryPolicy(
    max_attempts=5,
    min_delay=0.5,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True,
)

RETRY_POLICY_CONSERVATIVE = RetryPolicy(
    max_attempts=3,
    min_delay=5.0,
    max_delay=300.0,
    exponential_base=2.0,
    jitter=True,
)

# Exception-specific retry policies
RETRY_POLICY_NETWORK = RetryPolicy(
    max_attempts=5,
    min_delay=1.0,
    max_delay=120.0,
    exponential_base=2.0,
    jitter=True,
    retry_on_exceptions=(ConnectionError, TimeoutError),
)

RETRY_POLICY_DATABASE = RetryPolicy(
    max_attempts=3,
    min_delay=2.0,
    max_delay=60.0,
    exponential_base=3.0,
    jitter=True,
    retry_on_exceptions=(ConnectionError, TimeoutError),
)

# Retry decorators with predefined policies
def retry_default(func: Callable) -> Callable:
    """Retry with default policy."""
    return retry(policy=RETRY_POLICY_DEFAULT)(func)

def retry_aggressive(func: Callable) -> Callable:
    """Retry with aggressive policy."""
    return retry(policy=RETRY_POLICY_AGGRESSIVE)(func)

def retry_conservative(func: Callable) -> Callable:
    """Retry with conservative policy."""
    return retry(policy=RETRY_POLICY_CONSERVATIVE)(func)

def retry_network(func: Callable) -> Callable:
    """Retry for network-related exceptions."""
    return retry(policy=RETRY_POLICY_NETWORK)(func)

def retry_database(func: Callable) -> Callable:
    """Retry for database-related exceptions."""
    return retry(policy=RETRY_POLICY_DATABASE)(func)

# Context manager for retries
class retry_context:
    """Context manager for retrying operations."""
    
    def __init__(self, policy: RetryPolicy = None, **kwargs):
        """
        Initialize retry context.
        
        Args:
            policy: Retry policy to use
            **kwargs: Arguments for RetryPolicy if policy not provided
        """
        if policy is None:
            policy = RetryPolicy(**kwargs)
        self.policy = policy
        self.attempt = 0
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # No exception, success
            return True
        
        if not issubclass(exc_type, self.policy.retry_on_exceptions):
            # Exception not in retry list
            return False
        
        # Check if we should retry
        if self.policy.max_attempts > 0 and self.attempt >= self.policy.max_attempts - 1:
            # Max attempts reached
            return False
        
        # Retry
        self.attempt += 1
        delay = _calculate_delay(self.policy, self.attempt - 1)
        
        logger.warning(
            f"Attempt {self.attempt} failed: {exc_val}. "
            f"Retrying in {delay:.2f} seconds..."
        )
        
        # Sleep before retry
        time.sleep(delay)
        return True

# Example usage:
"""
# Basic retry with default policy
@retry_default
def unreliable_function():
    # Function that sometimes fails
    pass

# Custom retry policy
@retry(max_attempts=5, min_delay=2.0, max_delay=60.0)
def custom_retry_function():
    pass

# Retry with specific exceptions
@retry(retry_on_exceptions=(ValueError, TypeError))
def type_sensitive_function():
    pass

# Using context manager
def manual_retry_example():
    policy = RetryPolicy(max_attempts=3, min_delay=1.0)
    
    with retry_context(policy) as retry_ctx:
        while True:
            try:
                # Some operation
                result = perform_operation()
                return result
            except Exception as e:
                if not retry_ctx.__exit__(type(e), e, e.__traceback__):
                    raise
                retry_ctx.__enter__()  # Re-enter for next attempt
"""