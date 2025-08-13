"""
Authlib adapter for PacificPy.

This module provides an adapter for integrating with Authlib,
enabling OAuth2 client/provider functionality with a simple API.
"""

from typing import Dict, Any, Optional, Callable
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
import secrets

# Try to import authlib
try:
    from authlib.integrations.starlette_client import OAuth
    from authlib.integrations.base_client import BaseOAuth
    AUTHLIB_AVAILABLE = True
except ImportError:
    AUTHLIB_AVAILABLE = False

class AuthlibAdapter:
    """Adapter for Authlib integration."""
    
    def __init__(self, app=None, oauth: BaseOAuth = None):
        """
        Initialize the Authlib adapter.
        
        Args:
            app: The Starlette application
            oauth: An Authlib OAuth instance
        """
        if not AUTHLIB_AVAILABLE:
            raise RuntimeError("authlib package is required for AuthlibAdapter")
        
        self.app = app
        self.oauth = oauth or OAuth()
        self.providers = {}
        self.redirect_uri = None
    
    def register_provider(
        self,
        name: str,
        client_id: str,
        client_secret: str,
        server_metadata_url: str = None,
        access_token_url: str = None,
        authorize_url: str = None,
        api_base_url: str = None,
        client_kwargs: Dict[str, Any] = None,
    ) -> None:
        """
        Register an OAuth provider.
        
        Args:
            name: Provider name (e.g., "google", "github")
            client_id: OAuth client ID
            client_secret: OAuth client secret
            server_metadata_url: OpenID Connect metadata URL
            access_token_url: Access token endpoint URL
            authorize_url: Authorization endpoint URL
            api_base_url: API base URL
            client_kwargs: Additional client kwargs
        """
        # Register the provider with Authlib
        self.oauth.register(
            name=name,
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=server_metadata_url,
            access_token_url=access_token_url,
            authorize_url=authorize_url,
            api_base_url=api_base_url,
            client_kwargs=client_kwargs or {"scope": "openid email profile"},
        )
        
        # Store provider info
        self.providers[name] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "server_metadata_url": server_metadata_url,
            "access_token_url": access_token_url,
            "authorize_url": authorize_url,
            "api_base_url": api_base_url,
            "client_kwargs": client_kwargs,
        }
    
    async def login_with_provider(self, request: Request, provider_name: str) -> RedirectResponse:
        """
        Initiate OAuth login flow with a provider.
        
        Args:
            request: The incoming request
            provider_name: The name of the provider to use
            
        Returns:
            A redirect response to the provider's authorization endpoint
        """
        # Get the provider
        provider = self.oauth.create_client(provider_name)
        
        # Generate redirect URI
        redirect_uri = request.url_for("auth_callback", provider=provider_name)
        
        # Save redirect URI for later use
        self.redirect_uri = str(redirect_uri)
        
        # Create redirect to provider
        return await provider.authorize_redirect(request, redirect_uri)
    
    async def handle_callback(self, request: Request, provider_name: str) -> Dict[str, Any]:
        """
        Handle OAuth callback from a provider.
        
        Args:
            request: The incoming request
            provider_name: The name of the provider
            
        Returns:
            A dictionary containing the user info and access token
        """
        # Get the provider
        provider = self.oauth.create_client(provider_name)
        
        # Handle authorization callback
        token = await provider.authorize_access_token(request)
        
        # Get user info
        user = token.get("userinfo")
        if not user:
            user = await provider.parse_id_token(request, token)
        
        return {
            "user": user,
            "token": token,
            "provider": provider_name,
        }
    
    def get_oauth_routes(self) -> list:
        """
        Get the OAuth routes for the application.
        
        Returns:
            A list of route handlers
        """
        return [
            # Login route
            ("/auth/{provider}/login", self._login_route, ["GET"]),
            # Callback route
            ("/auth/{provider}/callback", self._callback_route, ["GET"]),
        ]
    
    async def _login_route(self, request: Request) -> RedirectResponse:
        """Handle OAuth login route."""
        provider = request.path_params["provider"]
        return await self.login_with_provider(request, provider)
    
    async def _callback_route(self, request: Request) -> Response:
        """Handle OAuth callback route."""
        provider = request.path_params["provider"]
        result = await self.handle_callback(request, provider)
        
        # This is a simplified response - in a real app, you'd likely
        # create a session and redirect to a protected page
        return Response(f"OAuth successful for {provider}: {result['user']}")

# Convenience functions
def create_authlib_adapter(app=None) -> AuthlibAdapter:
    """
    Create an Authlib adapter.
    
    Args:
        app: The Starlette application
        
    Returns:
        An AuthlibAdapter instance
    """
    return AuthlibAdapter(app)

# Example usage:
"""
# In your app setup:
auth = create_authlib_adapter(app)

# Register providers:
auth.register_provider(
    name="google",
    client_id="your-google-client-id",
    client_secret="your-google-client-secret",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
)

# Add routes to your app:
for path, handler, methods in auth.get_oauth_routes():
    app.add_route(path, handler, methods=methods)
"""