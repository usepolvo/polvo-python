"""
API key authentication.
"""

from enum import Enum, auto
from typing import Dict

from usepolvo_core.auth.base import Auth


class ApiKeyLocation(Enum):
    """Location of API key in the request."""

    HEADER = auto()
    QUERY = auto()


class ApiKeyAuth(Auth):
    """API key authentication."""

    def __init__(
        self,
        api_key: str,
        key_name: str = "X-API-Key",
        location: ApiKeyLocation = ApiKeyLocation.HEADER,
    ):
        """
        Initialize ApiKeyAuth.

        Args:
            api_key: API key
            key_name: Name of the API key parameter
            location: Location of the API key (header or query)
        """
        self.api_key = api_key
        self.key_name = key_name
        self.location = location

    def sign(self, method: str, url: str, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sign a request with an API key.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers

        Returns:
            Modified headers
        """
        if self.location == ApiKeyLocation.HEADER:
            headers = headers.copy()
            headers[self.key_name] = self.api_key

        return headers
