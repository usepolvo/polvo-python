"""
Basic HTTP authentication.
"""

import base64
from typing import Dict

from usepolvo_core.auth.base import Auth


class BasicAuth(Auth):
    """Basic HTTP authentication."""

    def __init__(self, username: str, password: str):
        """
        Initialize BasicAuth.

        Args:
            username: Username
            password: Password
        """
        self.username = username
        self.password = password

    def sign(self, method: str, url: str, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sign a request with Basic authentication.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers

        Returns:
            Modified headers
        """
        auth = f"{self.username}:{self.password}"
        token = base64.b64encode(auth.encode("utf-8")).decode("utf-8")

        headers = headers.copy()
        headers["Authorization"] = f"Basic {token}"

        return headers
