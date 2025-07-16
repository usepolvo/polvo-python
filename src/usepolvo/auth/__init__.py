"""
Authentication strategies for Polvo v2.

Provides simple, production-ready authentication strategies.
The crown jewel is OAuth2Flow with automatic token refresh.
"""

from .base import AuthStrategy
from .bearer import BearerAuth
from .basic import BasicAuth  
from .api_key import APIKeyAuth
from .oauth2 import OAuth2Flow

# Convenience functions for common auth patterns
def bearer(token: str) -> BearerAuth:
    """
    Create a Bearer token authentication.
    
    Args:
        token: Bearer token
    
    Returns:
        BearerAuth instance
    
    Example:
        auth = polvo.auth.bearer("your_token_here")
        api = polvo.API("https://api.example.com", auth=auth)
    """
    return BearerAuth(token)

def basic(username: str, password: str) -> BasicAuth:
    """
    Create Basic authentication.
    
    Args:
        username: Username
        password: Password
        
    Returns:
        BasicAuth instance
    """
    return BasicAuth(username, password)

def api_key(
    key: str, 
    header_name: str = "X-API-Key",
    prefix: str = ""
) -> APIKeyAuth:
    """
    Create API key authentication.
    
    Args:
        key: API key value
        header_name: Header name to use (default: X-API-Key)
        prefix: Optional prefix for the key value
        
    Returns:
        APIKeyAuth instance
    """
    return APIKeyAuth(key, header_name, prefix)

def oauth2(
    client_id: str,
    client_secret: str,
    token_url: str,
    scope: str = "",
    storage = None
) -> OAuth2Flow:
    """
    Create OAuth2 authentication with automatic token refresh.
    
    This is the crown jewel - handles complex OAuth2 flows transparently.
    
    Args:
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret  
        token_url: Token endpoint URL
        scope: OAuth2 scopes (space-separated)
        storage: Token storage backend (defaults to encrypted file storage)
        
    Returns:
        OAuth2Flow instance
        
    Example:
        oauth = polvo.auth.oauth2(
            client_id="your_client_id",
            client_secret="your_secret", 
            token_url="https://api.example.com/oauth/token"
        )
        api = polvo.API("https://api.example.com", auth=oauth)
    """
    from ..storage import encrypted_file  # Import here to avoid circular imports
    
    if storage is None:
        storage = encrypted_file()
        
    return OAuth2Flow(
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url,
        scope=scope,
        storage=storage
    )

__all__ = [
    "AuthStrategy",
    "BearerAuth", 
    "BasicAuth",
    "APIKeyAuth",
    "OAuth2Flow",
    "bearer",
    "basic", 
    "api_key",
    "oauth2"
] 