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
        response = polvo.get("https://api.example.com/data", auth=auth)
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
    storage=None,
    scope: str = ""
) -> OAuth2Flow:
    """
    Create OAuth2 authentication with automatic token refresh.
    
    This handles complex OAuth2 flows transparently with secure token storage.
    
    Args:
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret  
        token_url: Token endpoint URL
        storage: Token storage backend (optional - defaults to memory with warning)
                 Use polvo.storage.encrypted_file() for production
                 Use polvo.storage.memory() for testing
        scope: OAuth2 scopes (space-separated)
        
    Returns:
        OAuth2Flow instance
        
    Example:
        # Simple usage (uses memory storage with warning)
        oauth = polvo.auth.oauth2(
            client_id="your_client_id",
            client_secret="your_secret", 
            token_url="https://api.example.com/oauth/token"
        )
        
        # Production usage with encrypted file storage
        oauth = polvo.auth.oauth2(
            client_id="your_client_id",
            client_secret="your_secret", 
            token_url="https://api.example.com/oauth/token",
            storage=polvo.storage.encrypted_file("~/.myapp/tokens.enc")
        )
    """        
    return OAuth2Flow(
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url,
        storage=storage,
        scope=scope
    )


def oauth2_with_file_storage(
    client_id: str,
    client_secret: str,
    token_url: str,
    token_file: str = "~/.polvo/tokens.enc",
    scope: str = ""
) -> OAuth2Flow:
    """
    Create OAuth2 authentication with explicit encrypted file storage.
    
    This convenience function provides a secure default for production use.
    
    Args:
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        token_url: Token endpoint URL
        token_file: Path where encrypted tokens should be stored
        scope: OAuth2 scopes (space-separated)
        
    Returns:
        OAuth2Flow instance
        
    Example:
        oauth = polvo.auth.oauth2_with_file_storage(
            client_id="your_client_id",
            client_secret="your_secret",
            token_url="https://api.example.com/oauth/token",
            token_file="~/.myapp/api-tokens.enc"
        )
    """
    from .. import storage
    
    token_storage = storage.encrypted_file(token_file)
    
    return OAuth2Flow(
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url,
        storage=token_storage,
        scope=scope
    )

# Pythonic aliases for convenience
class OAuth2(OAuth2Flow):
    """
    OAuth2 authentication (shorter, more Pythonic name).
    
    Use this for APIs that use OAuth2 client credentials flow.
    Same as OAuth2Flow but with a shorter name.
    """
    pass


__all__ = [
    # Base classes
    "AuthStrategy",
    "BearerAuth", 
    "BasicAuth",
    "APIKeyAuth",
    "OAuth2Flow",
    
    # Pythonic aliases
    "OAuth2",
    
    # Convenience functions
    "bearer",
    "basic", 
    "api_key",
    "oauth2",
    "oauth2_with_file_storage"
] 