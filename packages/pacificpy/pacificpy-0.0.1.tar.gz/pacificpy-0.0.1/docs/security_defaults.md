# Security-by-Default Settings

This document outlines the security settings that are enabled by default in PacificPy to ensure applications are secure out of the box.

## Default Security Settings

### 1. HTTP Security Headers

- **Strict-Transport-Security (HSTS)**: Enforced for all HTTPS responses
  - Max age: 1 year
  - Includes subdomains
  - Preload ready

- **X-Frame-Options**: Set to `DENY` to prevent clickjacking

- **X-Content-Type-Options**: Set to `nosniff` to prevent MIME type sniffing

- **Referrer-Policy**: Set to `strict-origin-when-cross-origin`

### 2. Content Security Policy (CSP)

- **Default Policy**: Restrictive policy allowing only same-origin resources
- **Script/Style Nonces**: Automatically generated for inline scripts and styles
- **Report Only Mode**: Disabled by default (enforced policy)

### 3. Cross-Site Request Forgery (CSRF) Protection

- **Token Generation**: Secure random tokens
- **Token Storage**: HTTP-only, SameSite cookies
- **Validation**: Required for all non-safe HTTP methods
- **AJAX Support**: Header-based token validation

### 4. Cross-Origin Resource Sharing (CORS)

- **Default Origins**: Empty list (no origins allowed)
- **Default Methods**: Standard HTTP methods
- **Default Headers**: Empty list
- **Credentials**: Disabled by default

### 5. Rate Limiting

- **Default Limit**: 100 requests per minute
- **Key Generation**: Based on client IP and request path
- **Backend**: In-memory storage
- **Exempt Paths**: `/health`, `/metrics`

### 6. Secure Cookies

- **HttpOnly**: Enabled for session cookies
- **Secure**: Enabled for HTTPS connections
- **SameSite**: Set to `Lax` for session cookies
- **Path**: Set to `/` for session cookies

### 7. Request Validation

- **Strict Mode**: Enabled by default
- **Extra Fields**: Forbidden in strict mode
- **Type Conversion**: Automatic with validation

### 8. Error Handling

- **Information Leakage**: Prevented in production
- **Stack Traces**: Hidden in production
- **Trace IDs**: Included for correlation
- **Logging**: Structured with sensitive data scrubbing

## Configuration Options

All default security settings can be customized through application configuration:

```python
app = PacificPy(
    hsts_max_age=31536000,
    csrf_enabled=True,
    cors_origins=[],
    rate_limit=100,
    # ... other security settings
)
```

## Security Checklist

- [x] HSTS enabled by default
- [x] XSS protection headers set
- [x] CSP with nonce generation
- [x] CSRF protection enabled
- [x] Secure CORS defaults
- [x] Rate limiting applied
- [x] Secure cookie settings
- [x] Strict request validation
- [x] Sanitized error responses
- [x] Sensitive data scrubbing in logs