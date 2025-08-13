# Security Code Review Checklist

This checklist should be used during code reviews to identify potential security vulnerabilities in pull requests.

## Input Validation & Sanitization

- [ ] **XSS Prevention**
  - [ ] All user input is properly escaped before rendering in HTML
  - [ ] Context-aware escaping is used (HTML, JavaScript, CSS, URL)
  - [ ] Safe JSON serialization is used for data in HTML/JS contexts
  - [ ] CSP nonces are properly implemented for inline scripts/styles

- [ ] **SQL Injection**
  - [ ] Parameterized queries are used for all database operations
  - [ ] ORM/Query Builder is used instead of raw SQL when possible
  - [ ] Dynamic table/column names are properly validated
  - [ ] User input is never directly concatenated into SQL strings

- [ ] **Command Injection**
  - [ ] Shell commands are executed using safe APIs, not string concatenation
  - [ ] User input is properly sanitized before use in system commands
  - [ ] Shell metacharacters are escaped or rejected

## Authentication & Authorization

- [ ] **Authentication**
  - [ ] Strong password policies are enforced
  - [ ] Secure password hashing (bcrypt, Argon2) is used
  - [ ] Multi-factor authentication is implemented where appropriate
  - [ ] Session tokens are securely generated and stored

- [ ] **Authorization**
  - [ ] Role-based access control (RBAC) is properly implemented
  - [ ] Privilege escalation checks are in place
  - [ ] Ownership validation is performed for user resources
  - [ ] API endpoints are properly protected with auth decorators

- [ ] **Session Management**
  - [ ] Secure session cookies (HttpOnly, Secure, SameSite)
  - [ ] Session timeout and renewal mechanisms
  - [ ] Concurrent session limits
  - [ ] Proper session invalidation on logout

## Data Protection

- [ ] **Sensitive Data Handling**
  - [ ] PII and sensitive data are encrypted at rest
  - [ ] Data minimization principles are followed
  - [ ] Secure key management practices
  - [ ] Data retention and deletion policies

- [ ] **Secrets Management**
  - [ ] No hardcoded secrets in code
  - [ ] Environment variables used for configuration
  - [ ] Secrets are encrypted in transit and at rest
  - [ ] API keys and tokens are rotated regularly

## Error Handling & Logging

- [ ] **Error Messages**
  - [ ] No sensitive information leaked in error responses
  - [ ] Generic error messages in production
  - [ ] Detailed logging for developers (separate from user messages)
  - [ ] Trace IDs included for correlation

- [ ] **Logging**
  - [ ] Sensitive data is scrubbed from logs
  - [ ] Log injection prevention (CRLF, special characters)
  - [ ] Appropriate log levels used (no debug info in production)
  - [ ] Log storage and retention policies

## Security Headers & Configuration

- [ ] **HTTP Security Headers**
  - [ ] HSTS, X-Frame-Options, X-Content-Type-Options set
  - [ ] Content Security Policy properly configured
  - [ ] Referrer Policy set appropriately
  - [ ] Server information headers removed

- [ ] **Secure Configuration**
  - [ ] Security-by-default settings
  - [ ] TLS/SSL properly configured
  - [ ] Secure cookie settings
  - [ ] CORS policies are restrictive

## Input Handling

- [ ] **File Uploads**
  - [ ] File type validation (content-type and extension)
  - [ ] File size limits enforced
  - [ ] Malware scanning for uploaded files
  - [ ] Secure storage of uploaded files

- [ ] **Rate Limiting**
  - [ ] Appropriate rate limits for APIs
  - [ ] Brute force protection
  - [ ] DDoS mitigation strategies
  - [ ] Fair usage policies

## Cryptography

- [ ] **Cryptographic Practices**
  - [ ] Strong, up-to-date cryptographic algorithms
  - [ ] Proper key generation and management
  - [ ] Secure random number generation
  - [ ] Certificate validation for TLS connections

## Third-Party Dependencies

- [ ] **Dependency Security**
  - [ ] All dependencies are from trusted sources
  - [ ] Regular dependency vulnerability scanning
  - [ ] Outdated dependencies are updated
  - [ ] SBOM (Software Bill of Materials) maintained

## Additional Checks

- [ ] **CSRF Protection**
  - [ ] Tokens are properly validated for state-changing operations
  - [ ] SameSite cookie attributes set
  - [ ] Double-submit cookie pattern or synchronized tokens

- [ ] **Clickjacking Protection**
  - [ ] X-Frame-Options header set
  - [ ] Content Security Policy frame-ancestors directive

- [ ] **Unsafe Code Practices**
  - [ ] No use of eval() or similar dangerous functions
  - [ ] No client-side only validation
  - [ ] Proper input validation on server side