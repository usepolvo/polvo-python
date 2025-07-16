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
    storage,
    scope: str = ""
) -> OAuth2Flow:
    """
    Create OAuth2 authentication with automatic token refresh.
    
    This handles complex OAuth2 flows transparently with explicit token storage.
    
    Args:
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret  
        token_url: Token endpoint URL
        storage: Token storage backend (required - choose where tokens are stored)
                 Use polvo.storage.encrypted_file() for production
                 Use polvo.storage.memory() for testing
                 Use polvo.storage.redis() for distributed systems
        scope: OAuth2 scopes (space-separated)
        
    Returns:
        OAuth2Flow instance
        
    Example:
        # Production usage with encrypted file storage
        oauth = polvo.auth.oauth2(
            client_id="your_client_id",
            client_secret="your_secret", 
            token_url="https://api.example.com/oauth/token",
            storage=polvo.storage.encrypted_file("~/.myapp/tokens.json")
        )
        
        # Testing with memory storage
        oauth = polvo.auth.oauth2(
            client_id="test_id",
            client_secret="test_secret",
            token_url="https://test-api.example.com/token",
            storage=polvo.storage.memory()
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
    token_file: str = "~/.config/polvo/tokens.json",
    encrypt_tokens: bool = True,
    scope: str = ""
) -> OAuth2Flow:
    """
    Create OAuth2 authentication with explicit file storage configuration.
    
    This convenience function makes storage choices explicit and provides
    sensible defaults for production use.
    
    Args:
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        token_url: Token endpoint URL
        token_file: Path where tokens should be stored
        encrypt_tokens: Whether to encrypt tokens on disk (recommended)
        scope: OAuth2 scopes (space-separated)
        
    Returns:
        OAuth2Flow instance
        
    Example:
        # Production usage with explicit file storage
        oauth = polvo.auth.oauth2_with_file_storage(
            client_id="your_client_id",
            client_secret="your_secret",
            token_url="https://api.example.com/oauth/token",
            token_file="~/.myapp/api-tokens.json",
            encrypt_tokens=True
        )
    """
    from .. import storage
    
    if encrypt_tokens:
        token_storage = storage.encrypted_file(token_file)
    else:
        # For now, use encrypted file anyway but we could add plain file storage
        token_storage = storage.encrypted_file(token_file)
    
    return OAuth2Flow(
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url,
        storage=token_storage,
        scope=scope
    )

# Simple auth patterns for common cases
class BearerToken(BearerAuth):
    """
    Bearer token authentication (more explicit name).
    
    Use this for APIs that require 'Authorization: Bearer <token>' headers.
    """
    pass


class OAuth2(OAuth2Flow):
    """
    OAuth2 authentication (shorter, more Pythonic name).
    
    Use this for APIs that use OAuth2 client credentials flow.
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
    "BearerToken",
    "OAuth2",
    
    # Convenience functions
    "bearer",
    "basic", 
    "api_key",
    "oauth2",
    "oauth2_with_file_storage"
] 