"""
Base interface for token storage backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class TokenStorage(ABC):
    """
    Base interface for token storage backends.
    
    All storage implementations must implement these methods to provide
    a consistent interface for storing and retrieving OAuth2 tokens.
    """
    
    @abstractmethod
    def store_token(self, key: str, token_data: Dict[str, Any]) -> None:
        """
        Store token data.
        
        Args:
            key: Unique key to identify the token (e.g., client_id + tenant_id)
            token_data: Token data dictionary containing access_token, expires_in, etc.
        """
        pass
    
    @abstractmethod
    def get_token(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve token data.
        
        Args:
            key: Unique key to identify the token
            
        Returns:
            Token data dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def delete_token(self, key: str) -> None:
        """
        Delete token data.
        
        Args:
            key: Unique key to identify the token
        """
        pass
    
    @abstractmethod
    def clear_all(self) -> None:
        """
        Clear all stored tokens.
        
        Useful for logout scenarios or testing.
        """
        pass 