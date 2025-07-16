"""
Bearer token authentication.
"""

from typing import Dict
from .base import AuthStrategy


class BearerAuth(AuthStrategy):
    """
    Bearer token authentication strategy.
    
    Adds an Authorization header with a Bearer token.
    """
    
    def __init__(self, token: str):
        """
        Initialize Bearer authentication.
        
        Args:
            token: Bearer token to use for authentication
        """
        self.token = token
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get Bearer authentication headers.
        
        Returns:
            Dictionary with Authorization header
        """
        return {"Authorization": f"Bearer {self.token}"} 