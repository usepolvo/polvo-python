"""
OAuth 2.0 authentication.
"""

from typing import Dict, Optional

from usepolvo_core.auth.bearer import BearerAuth


class OAuth2(BearerAuth):
    """OAuth 2.0 authentication with Bearer token."""

    def __init__(
        self,
        token: str,
        token_type: str = "Bearer",
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None,
    ):
        """
        Initialize OAuth2.

        Args:
            token: OAuth 2.0 access token
            token_type: Token type (default: Bearer)
            refresh_token: Refresh token for refreshing access token
            expires_in: Token expiration time in seconds
        """
        super().__init__(token)
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.expires_in = expires_in

    def sign(self, method: str, url: str, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sign a request with OAuth 2.0 authentication.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers

        Returns:
            Modified headers
        """
        # TODO: Implement token refresh logic if expires_in is provided

        headers = headers.copy()
        headers["Authorization"] = f"{self.token_type} {self.token}"

        return headers
