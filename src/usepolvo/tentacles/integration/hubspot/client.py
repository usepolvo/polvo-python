# tentacles/integration/hubspot/client.py
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

import hubspot

from usepolvo.ink.tokens import SecureTokenStore
from usepolvo.tentacles.integration.hubspot.config import get_settings


class HubSpotClient:
    """
    Base HubSpot client that leverages the official HubSpot SDK.
    Handles authentication and provides access to SDK clients.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        token_storage_path: Optional[Path] = None,
        encryption_key: Optional[str] = None,
    ):
        """
        Initialize HubSpot client using the official SDK.

        Environment variables (prefixed with POLVO_):
            HUBSPOT_CLIENT_ID: OAuth2 client ID
            HUBSPOT_CLIENT_SECRET: OAuth2 client secret
            HUBSPOT_REDIRECT_URI: OAuth2 redirect URI

        Args:
            client_id: Optional OAuth2 client ID (overrides env var)
            client_secret: Optional OAuth2 client secret (overrides env var)
            redirect_uri: OAuth2 redirect URI (overrides env var)
            token_storage_path: Optional custom path for token storage
            encryption_key: Optional key for token encryption
        """
        # Load settings from environment
        self.settings = get_settings()

        # Set up token storage
        self.token_store = SecureTokenStore(
            encryption_key=encryption_key, storage_path=token_storage_path
        )

        # Use provided values or fall back to environment variables
        self._client_id = client_id or self.settings.HUBSPOT_CLIENT_ID
        self._client_secret = client_secret or self.settings.HUBSPOT_CLIENT_SECRET
        self._redirect_uri = redirect_uri or self.settings.HUBSPOT_REDIRECT_URI

        if not all([self._client_id, self._client_secret, self._redirect_uri]):
            raise ValueError(
                "Must provide (client_id, client_secret, redirect_uri) "
                "via constructor arguments or environment variables"
            )

        # Initialize the HubSpot client
        stored_tokens = self.token_store.load_tokens("hubspot")
        if stored_tokens and stored_tokens.get("access_token"):
            self.client = hubspot.Client.create(access_token=stored_tokens["access_token"])
        else:
            self._authenticate()

    def _authenticate(self) -> None:
        """Run OAuth2 authentication flow and store tokens."""
        try:
            # Create a client for authentication
            self.client = hubspot.Client.create()

            # Get authorization URL
            auth_url = f"https://app.hubspot.com/oauth/authorize?client_id={self._client_id}&redirect_uri={self._redirect_uri}&scope={' '.join(self.settings.HUBSPOT_OAUTH_SCOPES)}"

            print("\nPlease visit this URL to authenticate:")
            print(auth_url)
            print("\nAfter authorizing, paste the complete redirect URL here:")
            redirect_url = input().strip()

            # Extract code from redirect URL
            parsed_url = urlparse(redirect_url)
            code = parse_qs(parsed_url.query)["code"][0]

            # Exchange code for tokens
            tokens = self.client.auth.oauth.tokens.create(
                grant_type="authorization_code",
                code=code,
                client_id=self._client_id,
                client_secret=self._client_secret,
                redirect_uri=self._redirect_uri,
            )

            # Store tokens
            self.token_store.save_tokens(
                "hubspot",
                {
                    "access_token": tokens.access_token,
                    "refresh_token": tokens.refresh_token,
                    "expires_in": tokens.expires_in,
                },
            )

            # Create new client with access token
            self.client = hubspot.Client.create(access_token=tokens.access_token)

        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")

    def refresh_token(self) -> None:
        """Refresh the access token if needed."""
        stored_tokens = self.token_store.load_tokens("hubspot")
        if not stored_tokens or not stored_tokens.get("refresh_token"):
            self._authenticate()
            return

        try:
            tokens = self.client.auth.oauth.tokens.create(
                grant_type="refresh_token",
                refresh_token=stored_tokens["refresh_token"],
                client_id=self._client_id,
                client_secret=self._client_secret,
            )

            # Store new tokens
            self.token_store.save_tokens(
                "hubspot",
                {
                    "access_token": tokens.access_token,
                    "refresh_token": tokens.refresh_token,
                    "expires_in": tokens.expires_in,
                },
            )

            # Create new client with fresh access token
            self.client = hubspot.Client.create(access_token=tokens.access_token)

        except Exception:
            # If refresh fails, try full authentication
            self._authenticate()
