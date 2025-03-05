# core/auth/oauth2.py
import time
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import requests

from usepolvo.core.auth.base import BaseAuth
from usepolvo.core.exceptions import AuthenticationError


class OAuth2Auth(BaseAuth):
    """
    Base class for OAuth2 authentication.
    Handles OAuth2 flow and token management.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        auth_url: str,
        token_url: str,
        redirect_uri: str,
        scopes: List[str],
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.redirect_uri = redirect_uri
        self.scopes = scopes

        # Token state
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: float = 0
        self.current_scopes: List[str] = []

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers using current access token."""
        if not self.access_token:
            raise AuthenticationError("No access token available. Call authenticate() first.")
        return {"Authorization": f"Bearer {self.access_token}"}

    def is_token_valid(self) -> bool:
        """Check if current access token is valid."""
        return bool(self.access_token and time.time() < self.token_expiry)

    def authenticate(self) -> Dict[str, str]:
        """
        Start OAuth2 authentication flow.
        Returns token response or raises AuthenticationError.
        """
        # Build authorization URL
        auth_params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "%20".join(self.scopes),  # Convert scopes to URL-encoded format
            "response_type": "code",
        }

        auth_url = self._build_url(self.auth_url, auth_params)

        # Guide user through auth flow
        print("\nPlease visit this URL to authenticate:")
        print(auth_url)
        print("\nAfter authorizing, paste the complete redirect URL here:")
        redirect_url = input().strip()

        # Extract auth code
        try:
            parsed_url = urlparse(redirect_url)
            params = parse_qs(parsed_url.query)
            code = params["code"][0]
        except (KeyError, IndexError):
            raise AuthenticationError("Could not extract authorization code from URL")

        # Exchange code for tokens
        return self.exchange_code(code)

    def exchange_code(self, code: str) -> Dict[str, str]:
        """Exchange authorization code for tokens."""
        token_data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
        }

        return self._token_request(token_data)

    def refresh_token_if_needed(self) -> Optional[Dict[str, str]]:
        """Refresh access token if expired and refresh token is available."""
        if not self.is_token_valid() and self.refresh_token:
            return self.refresh_tokens()
        return None

    def refresh_tokens(self) -> Dict[str, str]:
        """Refresh access token using refresh token."""
        if not self.refresh_token:
            raise AuthenticationError("No refresh token available")

        token_data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        return self._token_request(token_data)

    def _token_request(self, data: Dict[str, str]) -> Dict[str, str]:
        """Make token request and update token state."""
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            token_data = response.json()

            # Update token state
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            self.token_expiry = time.time() + token_data.get("expires_in", 3600)

            # Add scopes to the response data
            token_data["scopes"] = self.scopes

            return token_data

        except requests.RequestException as e:
            raise AuthenticationError(f"Token request failed: {str(e)}")

    def _build_url(self, base: str, params: Dict[str, str]) -> str:
        """Build URL with parameters."""
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base}?{param_str}"
