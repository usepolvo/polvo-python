# tentacles/hubspot/client.py

from pathlib import Path
from typing import List, Optional

import hubspot

from usepolvo.core.auth.oauth2 import OAuth2Auth
from usepolvo.core.auth.tokens import TokenStore
from usepolvo.core.clients.rest import RESTClient
from usepolvo.tentacles.hubspot.config import get_settings


class HubSpotClient(RESTClient):
    """
    HubSpot client that leverages the official HubSpot SDK.
    Handles authentication and provides access to SDK clients.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        token_storage_path: Optional[Path] = None,
        encryption_key: Optional[str] = None,
    ):
        """
        Initialize HubSpot client using the official SDK.

        Environment variables (prefixed with POLVO_):
            HUBSPOT_CLIENT_ID: OAuth2 client ID
            HUBSPOT_CLIENT_SECRET: OAuth2 client secret
            HUBSPOT_REDIRECT_URI: OAuth2 redirect URI
            HUBSPOT_OAUTH_SCOPES: OAuth2 scopes

        Args:
            client_id: Optional OAuth2 client ID (overrides env var)
            client_secret: Optional OAuth2 client secret (overrides env var)
            redirect_uri: OAuth2 redirect URI (overrides env var)
            scopes: Optional list of OAuth2 scopes (overrides env var)
            token_storage_path: Optional custom path for token storage
            encryption_key: Optional key for token encryption
        """
        # Load settings from environment
        self.settings = get_settings()

        # Set up token storage
        self.token_store = TokenStore(
            encryption_key=encryption_key, storage_path=token_storage_path
        )

        # Use provided values or fall back to environment variables
        self._client_id = client_id or self.settings.HUBSPOT_CLIENT_ID
        self._client_secret = client_secret or self.settings.HUBSPOT_CLIENT_SECRET
        self._redirect_uri = redirect_uri or self.settings.HUBSPOT_REDIRECT_URI
        self._scopes = scopes or self.settings.HUBSPOT_OAUTH_SCOPES

        if not all([self._client_id, self._client_secret, self._redirect_uri]):
            raise ValueError(
                "Must provide (client_id, client_secret, redirect_uri) "
                "via constructor arguments or environment variables"
            )

        # Initialize OAuth2 handler
        self.oauth = OAuth2Auth(
            client_id=self._client_id,
            client_secret=self._client_secret,
            auth_url=self.settings.HUBSPOT_OAUTH_URL,
            token_url="https://api.hubapi.com/oauth/v1/token",
            redirect_uri=self._redirect_uri,
            scopes=self._scopes,
        )

        # Initialize the HubSpot client
        stored_tokens = self.token_store.load_tokens("hubspot")
        if stored_tokens and stored_tokens.get("access_token"):
            stored_scopes = set(stored_tokens.get("scopes", []))
            requested_scopes = set(self._scopes)

            # Check if we need to re-authenticate due to missing required scopes
            if not requested_scopes.issubset(stored_scopes):
                self._authenticate()
            else:
                self.oauth.access_token = stored_tokens["access_token"]
                self.oauth.refresh_token = stored_tokens.get("refresh_token")
                self.oauth.token_expiry = stored_tokens.get("expires_in", 0)
                self.client = hubspot.Client.create(access_token=stored_tokens["access_token"])
        else:
            self._authenticate()

    def _authenticate(self) -> None:
        """Run OAuth2 authentication flow and store tokens."""
        try:
            # Run OAuth2 authentication flow
            tokens = self.oauth.authenticate()

            # Store tokens along with current scopes
            self.token_store.save_tokens(
                "hubspot",
                {
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                    "expires_in": tokens["expires_in"],
                    "scopes": self._scopes,  # Store the scopes used for this authentication
                },
            )

            # Create new client with access token
            self.client = hubspot.Client.create(access_token=tokens["access_token"])

        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")

    def refresh_token(self) -> None:
        """Refresh the access token if needed."""
        stored_tokens = self.token_store.load_tokens("hubspot")
        if not stored_tokens or not stored_tokens.get("refresh_token"):
            self._authenticate()
            return

        try:
            tokens = self.oauth.refresh_tokens()

            # Store new tokens while preserving existing scopes
            self.token_store.save_tokens(
                "hubspot",
                {
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                    "expires_in": tokens["expires_in"],
                    "scopes": stored_tokens.get("scopes", self._scopes),  # Preserve existing scopes
                },
            )

            # Create new client with fresh access token
            self.client = hubspot.Client.create(access_token=tokens["access_token"])

        except Exception:
            # If refresh fails, try full authentication
            self._authenticate()

    def _ensure_valid_token(self) -> None:
        """Ensure the access token is valid, refresh if needed."""
        stored_tokens = self.token_store.load_tokens("hubspot")

        if not stored_tokens or not stored_tokens.get("access_token"):
            self._authenticate()
            return

        # Check if token is expired or about to expire (within 5 minutes)
        if not self.oauth.is_token_valid():
            self.refresh_token()

    @property
    def crm(self):
        """Return the CRM client from the HubSpot SDK."""
        self._ensure_valid_token()
        return self.client.crm

    def reset_auth(self) -> None:
        """
        Clear stored tokens and reset authentication.
        Use this when you need to re-authenticate with different scopes.
        """
        # Clear stored tokens
        self.token_store.delete_tokens("hubspot")

        # Reset OAuth2 state
        self.oauth.access_token = None
        self.oauth.refresh_token = None
        self.oauth.token_expiry = 0

        # Reset client
        self.client = None

        # Re-authenticate with current scopes
        self._authenticate()

    def authenticate(self):
        """Force a new authentication flow"""
        token_data = self.oauth.authenticate()
        self._update_token_state(token_data)
