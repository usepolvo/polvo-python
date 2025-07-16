"""
Basic authentication.
"""

import base64
from typing import Dict
from .base import AuthStrategy


class BasicAuth(AuthStrategy):
    """
    Basic authentication strategy.
    
    Adds an Authorization header with Basic authentication.
    """
    
    def __init__(self, username: str, password: str):
        """
        Initialize Basic authentication.
        
        Args:
            username: Username for authentication
            password: Password for authentication
        """
        self.username = username
        self.password = password
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get Basic authentication headers.
        
        Returns:
            Dictionary with Authorization header
        """
        # Encode username:password in base64
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        return {"Authorization": f"Basic {encoded}"} 