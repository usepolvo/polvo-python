"""
Bearer token authentication.
"""

from typing import Dict

from usepolvo_core.auth.base import Auth


class BearerAuth(Auth):
    """Bearer token authentication."""

    def __init__(self, token: str):
        """
        Initialize BearerAuth.

        Args:
            token: Bearer token
        """
        self.token = token

    def sign(self, method: str, url: str, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sign a request with Bearer authentication.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers

        Returns:
            Modified headers
        """
        headers = headers.copy()
        headers["Authorization"] = f"Bearer {self.token}"

        return headers
