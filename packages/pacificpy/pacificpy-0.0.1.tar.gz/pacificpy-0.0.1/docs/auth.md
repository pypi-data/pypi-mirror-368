# Authentication Patterns in PacificPy

This guide covers the three main authentication patterns supported by PacificPy:
session-based authentication, JWT token authentication, and OAuth integration.

## 1. Session-Based Authentication

Session-based authentication stores user state on the server and uses cookies to
maintain the session between requests.

### Implementation

```python
from pacificpy.sessions.cookie import CookieSessionBackend
from pacificpy.auth.middleware import AuthMiddleware

# Configure session backend
session_backend = CookieSessionBackend(
    secret_key="your-secret-key",
    cookie_name="session",
    max_age=14 * 24 * 60 * 60,  # 14 days
)

# Add session middleware
app.add_middleware(SessionMiddleware, backend=session_backend)

# Add auth middleware
app.add_middleware(AuthMiddleware, session_backend=session_backend)

# Login endpoint
@app.post("/login")
async def login(request):
    # Validate credentials (simplified)
    username = request.json().get("username")
    password = request.json().get("password")
    
    if validate_credentials(username, password):
        # Get user data
        user = get_user(username)
        
        # Store user in session
        request.state.session["user"] = user
        
        return {"message": "Login successful"}
    
    raise Unauthorized("Invalid credentials")

# Protected endpoint
@app.get("/profile")
@requires_auth
async def profile(request, current_user):
    return {"user": current_user}
```

### Advantages

- Simple to implement
- Built-in CSRF protection
- Automatic session management
- Good for traditional web applications

### Disadvantages

- Server-side state management
- Not ideal for stateless architectures
- Scaling challenges with multiple servers

## 2. JWT Token Authentication

JWT authentication is stateless and works well for APIs and microservices.

### Implementation

```python
from pacificpy.auth.jwt import configure_jwt, create_access_token, verify_token
from pacificpy.auth.middleware import AuthMiddleware

# Configure JWT
configure_jwt(
    secret_key="your-jwt-secret-key",
    expires_in=3600,  # 1 hour
    issuer="your-app-name",
)

# Add auth middleware
app.add_middleware(AuthMiddleware, secret_key="your-jwt-secret-key")

# Login endpoint
@app.post("/login")
async def login(request):
    # Validate credentials (simplified)
    username = request.json().get("username")
    password = request.json().get("password")
    
    if validate_credentials(username, password):
        # Get user data
        user = get_user(username)
        
        # Create access token
        token = create_access_token({"user": user})
        
        return {"access_token": token, "token_type": "bearer"}
    
    raise Unauthorized("Invalid credentials")

# Protected endpoint
@app.get("/profile")
@requires_auth
async def profile(request, current_user):
    return {"user": current_user}

# Token refresh endpoint
@app.post("/refresh")
async def refresh(request):
    # Get token from request
    token = get_token_from_request(request)
    
    # Refresh token
    new_token = refresh_token(token)
    
    return {"access_token": new_token, "token_type": "bearer"}
```

### Advantages

- Stateless authentication
- Works well with APIs and microservices
- Easy to scale horizontally
- Self-contained tokens

### Disadvantages

- No built-in revocation mechanism
- Token size can be large
- Security considerations with long-lived tokens

## 3. OAuth Integration

OAuth integration allows users to authenticate using third-party providers.

### Implementation

```python
from pacificpy.auth.integrations.authlib_adapter import create_authlib_adapter

# Create Authlib adapter
auth = create_authlib_adapter(app)

# Register OAuth providers
auth.register_provider(
    name="google",
    client_id="your-google-client-id",
    client_secret="your-google-client-secret",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
)

# Register OAuth routes
for path, handler, methods in auth.get_oauth_routes():
    app.add_route(path, handler, methods=methods)

# OAuth login endpoint
@app.get("/auth/{provider}/login")
async def oauth_login(request):
    provider = request.path_params["provider"]
    return await auth.login_with_provider(request, provider)

# OAuth callback endpoint
@app.get("/auth/{provider}/callback")
async def oauth_callback(request):
    provider = request.path_params["provider"]
    result = await auth.handle_callback(request, provider)
    
    # Create session or JWT token for the user
    user = result["user"]
    token = create_access_token({"user": user})
    
    return {"access_token": token, "token_type": "bearer"}
```

### Advantages

- Leverages existing identity providers
- Reduces password fatigue for users
- Provides rich user information
- Standardized protocols

### Disadvantages

- Dependency on third-party providers
- Complex implementation
- Potential for vendor lock-in

## Security Recommendations

### General

1. **Use HTTPS**: Always use HTTPS in production
2. **Secure Secrets**: Store secrets securely, never in code
3. **Input Validation**: Validate all inputs
4. **Rate Limiting**: Implement rate limiting for auth endpoints
5. **Logging**: Log authentication events for monitoring

### Session-Based

1. **Secure Cookies**: Use HttpOnly, Secure, and SameSite attributes
2. **Session Timeout**: Implement session timeout and renewal
3. **CSRF Protection**: Always use CSRF protection for state-changing operations
4. **Session Storage**: Use secure session storage with encryption

### JWT

1. **Short Expiration**: Use short expiration times for access tokens
2. **Refresh Tokens**: Implement refresh tokens for long-lived sessions
3. **Token Revocation**: Implement token revocation for sensitive operations
4. **Secure Storage**: Store tokens securely on the client-side
5. **Algorithm Security**: Use secure algorithms (HS256, RS256)

### OAuth

1. **Provider Security**: Choose reputable OAuth providers
2. **Scope Minimization**: Request minimal necessary scopes
3. **State Parameter**: Always use the state parameter for CSRF protection
4. **Token Storage**: Store OAuth tokens securely
5. **Regular Audits**: Regularly audit OAuth provider integrations

## Choosing the Right Pattern

### Use Session-Based Authentication When:

- Building traditional web applications
- Need built-in CSRF protection
- Want simple implementation
- Server-side state is acceptable

### Use JWT Authentication When:

- Building APIs or microservices
- Need stateless authentication
- Scaling horizontally
- Mobile app integration

### Use OAuth When:

- Want to leverage existing identity providers
- Building consumer-facing applications
- Need social login options
- Want to reduce password management burden

## Example Implementation

Here's a complete example combining all three patterns:

```python
from pacificpy import PacificPy
from pacificpy.sessions.cookie import CookieSessionBackend
from pacificpy.auth.middleware import AuthMiddleware
from pacificpy.auth.jwt import configure_jwt
from pacificpy.auth.integrations.authlib_adapter import create_authlib_adapter

# Create app
app = PacificPy()

# Configure session backend
session_backend = CookieSessionBackend(secret_key="your-secret-key")

# Configure JWT
configure_jwt(secret_key="your-jwt-secret-key")

# Create Authlib adapter
auth = create_authlib_adapter(app)
auth.register_provider(
    name="google",
    client_id="your-google-client-id",
    client_secret="your-google-client-secret",
)

# Add middleware
app.add_middleware(SessionMiddleware, backend=session_backend)
app.add_middleware(AuthMiddleware, 
                  secret_key="your-jwt-secret-key",
                  session_backend=session_backend)

# Add OAuth routes
for path, handler, methods in auth.get_oauth_routes():
    app.add_route(path, handler, methods=methods)

# Endpoints for all auth methods
@app.post("/login")
async def login(request):
    # Session-based login
    pass

@app.post("/api/login")
async def api_login(request):
    # JWT-based login
    pass

@app.get("/auth/{provider}/login")
async def oauth_login(request):
    # OAuth login
    pass
```

This guide provides a comprehensive overview of authentication patterns in PacificPy.
Choose the pattern that best fits your application's needs and security requirements.