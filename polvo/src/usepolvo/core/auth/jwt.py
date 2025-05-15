# core/auth/jwt.py
from typing import Dict

from usepolvo.core.auth.base import BaseAuth


class JWTAuth(BaseAuth):
    """JWT authentication with automatic signing."""

    def __init__(self, private_key: str, algorithm: str = "HS256"):
        self.private_key = private_key
        self.algorithm = algorithm

    def get_auth_headers(self) -> Dict[str, str]:
        token = self._generate_token()
        return {"Authorization": f"Bearer {token}"}

    def _generate_token(self) -> str:
        # JWT token generation logic
        pass
