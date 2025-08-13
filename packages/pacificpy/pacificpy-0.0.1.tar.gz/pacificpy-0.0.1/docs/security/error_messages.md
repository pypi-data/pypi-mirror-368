# Security Policy: Error Message Handling

This document outlines the principles and practices for handling error messages in PacificPy to prevent information leakage and maintain security by default.

## Principles

1. **Security by Default**: Error messages should never expose sensitive information
2. **Minimal Disclosure**: Only provide necessary information to users
3. **Separation of Concerns**: Detailed error information for developers should be logged separately
4. **Environment Awareness**: More detailed errors in development, sanitized in production

## Rules for Error Messages

### 1. Generic Error Responses

All error responses to clients should be generic and not reveal implementation details:

```
# Good
{"detail": "Internal server error", "trace_id": "abc123"}

# Bad
{"detail": "Database connection failed: Access denied for user 'root'@'localhost'"}
```

### 2. Validation Errors

Validation errors can be more specific but should not reveal system internals:

```
# Good
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ],
  "trace_id": "abc123"
}

# Bad
{
  "detail": "ValueError: Invalid email format in function validate_user_data at line 42"
}
```

### 3. Forbidden/Unauthorized Errors

Do not reveal whether a resource exists:

```
# Good (for both cases)
{"detail": "Unauthorized", "trace_id": "abc123"}

# Bad (reveals resource existence)
{"detail": "User with ID 123 not found"}
```

## Sensitive Information to Never Include

- Database connection strings
- API keys or secrets
- File paths or system information
- Stack traces in production
- Internal IP addresses or hostnames
- Session tokens or cookies
- Personal identification information (PII)

## Logging Practices

### 1. Structured Logging

Use structured logging with appropriate log levels:

```python
# Good
logger.error("Authentication failed for user %s", user_id, extra={
    "trace_id": trace_id,
    "ip_address": request.client.host
})

# Bad
logger.error(f"Auth failed for user {user_id} from {request.client.host}")
```

### 2. Scrubbing Sensitive Data

Always scrub sensitive data before logging:

```python
from pacificpy.errors.scrub import scrub_exception_data

# Scrub sensitive data from exception context
scrubbed_data = scrub_exception_data(exception_context)
logger.error("Error occurred", extra=scrubbed_data)
```

## Environment-Specific Configuration

### Development Environment

- Detailed error messages with stack traces
- Debug information enabled
- Verbose logging

### Production Environment

- Generic error messages
- Stack traces disabled in responses
- Minimal logging verbosity
- Structured logging for monitoring

## Implementation Checklist

- [ ] All HTTP exceptions use generic messages in production
- [ ] Validation errors are properly formatted but not overly detailed
- [ ] Stack traces are only included in development/debug mode
- [ ] Sensitive data is scrubbed from logs
- [ ] Error responses include trace IDs for correlation
- [ ] Environment-specific error handling is implemented
- [ ] Custom exception handlers follow security guidelines