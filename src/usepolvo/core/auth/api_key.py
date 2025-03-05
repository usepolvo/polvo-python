# core/auth/api_key.py
from typing import Dict

from usepolvo.core.auth.base import BaseAuth


class APIKeyAuth(BaseAuth):
    """Simple API key authentication."""

    def __init__(self, api_key: str, header_name: str = "X-API-Key"):
        self.api_key = api_key
        self.header_name = header_name

    def get_auth_headers(self) -> Dict[str, str]:
        return {self.header_name: self.api_key}
