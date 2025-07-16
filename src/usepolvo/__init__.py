"""
Polvo v2 - Simple, production-ready API client

A requests-like library that handles the hard parts of API integration:
- OAuth2 with automatic token refresh
- Smart rate limiting and retry with exponential backoff
- Secure token storage with encryption

Usage:
    import polvo
    
    # Simple usage (like requests)
    response = polvo.get("https://api.github.com/users/octocat")
    
    # With authentication
    response = polvo.post(
        "https://api.example.com/data",
        json={"key": "value"},
        auth=polvo.auth.bearer("token123")
    )
    
    # Session for advanced usage
    session = polvo.Session("https://api.example.com")
    session.auth = polvo.auth.oauth2(
        client_id="your_client_id",
        client_secret="your_secret", 
        token_url="https://api.example.com/oauth/token"
    )
    response = session.get("/users")

Async Support:
    - Full async support with AsyncSession
    - OAuth2 token refresh uses sync internally (infrequent operations)
    - Rate limiting and retry work with both sync and async
"""

__version__ = "2.0.0"

# Import Session classes
from .api import Session, AsyncSession

# Import module-level convenience functions
from .api import get, post, put, patch, delete, head, options

# Import submodules
from . import auth
from . import storage
from . import retry
from . import rate_limit

__all__ = [
    # Module-level functions (primary interface)
    "get", "post", "put", "patch", "delete", "head", "options",
    
    # Session classes (advanced usage)
    "Session", "AsyncSession",
    
    # Submodules
    "auth", "storage", "retry", "rate_limit"
] 