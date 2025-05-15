"""
Base class for authentication methods.
"""

from typing import Dict


class Auth:
    """Base class for authentication methods."""

    def sign(self, method: str, url: str, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sign a request.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers

        Returns:
            Modified headers
        """
        return headers
