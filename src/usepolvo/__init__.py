"""
Polvo v2 - Simple, production-ready API client

A requests-like library that handles the hard parts of API integration:
- OAuth2 with automatic token refresh
- Smart rate limiting and retry with exponential backoff
- Secure token storage with encryption

Usage:
    import polvo
    
    # Simple usage
    api = polvo.API("https://api.example.com")
    response = api.get("/users")
    
    # With authentication
    api = polvo.API("https://api.example.com", auth=polvo.auth.bearer("token"))
    
    # OAuth2 with automatic token refresh
    oauth = polvo.auth.oauth2(
        client_id="your_client_id",
        client_secret="your_secret",
        token_url="https://api.example.com/oauth/token"
    )
    api = polvo.API("https://api.example.com", auth=oauth)
"""

__version__ = "2.0.0"

from .api import API
from . import auth
from . import storage
from . import retry
from . import rate_limit

__all__ = [
    "API",
    "auth",
    "storage", 
    "retry",
    "rate_limit"
] 