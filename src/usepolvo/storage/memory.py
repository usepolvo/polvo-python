"""
In-memory token storage.

Useful for testing and development. Tokens are lost when the process exits.
"""

from typing import Dict, Any, Optional
from .base import TokenStorage


class MemoryStorage(TokenStorage):
    """
    In-memory token storage.
    
    Stores tokens in a dictionary in memory. Tokens are lost when the
    process exits, making this suitable for testing and development only.
    """
    
    def __init__(self):
        """Initialize empty token storage."""
        self._tokens: Dict[str, Dict[str, Any]] = {}
    
    def store_token(self, key: str, token_data: Dict[str, Any]) -> None:
        """
        Store token data in memory.
        
        Args:
            key: Unique key to identify the token
            token_data: Token data dictionary
        """
        self._tokens[key] = token_data.copy()
    
    def get_token(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve token data from memory.
        
        Args:
            key: Unique key to identify the token
            
        Returns:
            Token data dictionary or None if not found
        """
        return self._tokens.get(key)
    
    def delete_token(self, key: str) -> None:
        """
        Delete token data from memory.
        
        Args:
            key: Unique key to identify the token
        """
        self._tokens.pop(key, None)
    
    def clear_all(self) -> None:
        """Clear all stored tokens from memory."""
        self._tokens.clear()
    
    def __len__(self) -> int:
        """Return the number of stored tokens."""
        return len(self._tokens)
    
    def keys(self):
        """Return all stored token keys."""
        return self._tokens.keys() 