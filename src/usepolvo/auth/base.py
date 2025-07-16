"""
Base authentication strategy interface.
"""

from abc import ABC, abstractmethod
from typing import Dict


class AuthStrategy(ABC):
    """
    Base interface for authentication strategies.
    
    All authentication methods implement this interface to provide
    a consistent way to add authentication headers to requests.
    """
    
    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers to add to the request.
        
        Returns:
            Dictionary of headers to add to the request
        """
        pass
    
 