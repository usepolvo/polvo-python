"""
API key authentication.
"""

from typing import Dict
from .base import AuthStrategy


class APIKeyAuth(AuthStrategy):
    """
    API key authentication strategy.
    
    Adds a custom header with the API key.
    """
    
    def __init__(self, key: str, header_name: str = "X-API-Key", prefix: str = ""):
        """
        Initialize API key authentication.
        
        Args:
            key: API key value
            header_name: Name of the header to use (default: X-API-Key)
            prefix: Optional prefix to add to the key value
        """
        self.key = key
        self.header_name = header_name
        self.prefix = prefix
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get API key authentication headers.
        
        Returns:
            Dictionary with the API key header
        """
        value = f"{self.prefix}{self.key}" if self.prefix else self.key
        return {self.header_name: value} 