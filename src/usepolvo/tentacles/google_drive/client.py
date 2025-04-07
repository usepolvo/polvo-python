# src/usepolvo/tentacles/google_drive/client.py

from typing import Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from usepolvo.core.auth.oauth2 import OAuth2Auth
from usepolvo.core.auth.tokens import TokenStore
from usepolvo.core.clients.base import BaseClient
from usepolvo.core.clients.user_context import UserContextClientMixin
from usepolvo.core.exceptions import AuthenticationError
from usepolvo.tentacles.google_drive.config import get_settings
from usepolvo.tentacles.google_drive.files import Files


class GoogleDriveClient(BaseClient, UserContextClientMixin):
    """
    Google Drive client that supports multi-tenant OAuth2 authentication.
    Provides access to Google Drive API for multiple users.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        token_store: Optional[TokenStore] = None,
    ):
        """
        Initialize Google Drive client with multi-tenant OAuth2 support.

        Environment variables (prefixed with POLVO_):
            GOOGLE_CLIENT_ID: OAuth2 client ID
            GOOGLE_CLIENT_SECRET: OAuth2 client secret
            GOOGLE_REDIRECT_URI: OAuth2 redirect URI
            GOOGLE_DEFAULT_SCOPES: OAuth2 scopes

        Args:
            client_id: Optional OAuth2 client ID (overrides env var)
            client_secret: Optional OAuth2 client secret (overrides env var)
            redirect_uri: OAuth2 redirect URI (overrides env var)
            scopes: Optional list of OAuth2 scopes (overrides env var)
            token_store: Optional custom token store
        """
        super().__init__()
        UserContextClientMixin.__init__(self)

        # Load settings from environment
        self.settings = get_settings()

        # Use provided values or fall back to environment variables
        self._client_id = client_id or self.settings.GOOGLE_CLIENT_ID
        self._client_secret = client_secret or self.settings.GOOGLE_CLIENT_SECRET
        self._redirect_uri = redirect_uri or self.settings.GOOGLE_REDIRECT_URI
        self._scopes = scopes or self.settings.GOOGLE_DEFAULT_SCOPES

        if not all([self._client_id, self._client_secret, self._redirect_uri]):
            raise ValueError(
                "Must provide (client_id, client_secret, redirect_uri) "
                "via constructor arguments or environment variables"
            )

        # Initialize OAuth2 handler using core implementation
        self.auth: OAuth2Auth = OAuth2Auth(
            client_id=self._client_id,
            client_secret=self._client_secret,
            auth_url=self.settings.GOOGLE_AUTH_URI,
            token_url=self.settings.GOOGLE_TOKEN_URI,
            redirect_uri=self._redirect_uri,
            scopes=self._scopes,
        )

        self.api_base = self.settings.GOOGLE_API_BASE

        # User-specific services
        self._user_services = {}

        # Initialize API resources
        self._files = Files(self)

    @property
    def files(self) -> Files:
        """Access the Files API."""
        return self._files

    def get_auth_url_for_user(self, user_id: str) -> str:
        """
        Get the OAuth2 authorization URL for a specific user.

        Args:
            user_id: The user ID to generate the auth URL for

        Returns:
            The authorization URL the user should visit
        """
        # Use the existing OAuth2Auth to generate the auth URL
        auth_params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "scope": " ".join(self._scopes),
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": user_id,  # Include user_id as state parameter
        }

        auth_url = self.auth._build_url(self.settings.GOOGLE_AUTH_URI, auth_params)
        return auth_url

    def process_callback(self, callback_url: str) -> str:
        """
        Process the OAuth2 callback and store tokens for the user.

        Args:
            callback_url: The full callback URL from the OAuth2 flow

        Returns:
            The user ID extracted from the callback

        Raises:
            AuthenticationError: If authentication fails
        """
        # Extract the user_id from the state parameter
        from urllib.parse import parse_qs, urlparse

        parsed_url = urlparse(callback_url)
        params = parse_qs(parsed_url.query)

        if "state" not in params:
            raise AuthenticationError("No state parameter in callback URL")

        user_id = params["state"][0]

        # Extract code from callback URL
        if "code" not in params:
            raise AuthenticationError("No code parameter in callback URL")

        code = params["code"][0]

        # Exchange code for tokens
        token_data = self.auth.exchange_code(code)

        # Store tokens for this user
        # In a real application, you would store these tokens in a secure database
        # For this example, we'll simulate a token store
        # Save the token_data for this user (would use token_store in production)
        self._user_services[user_id] = {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expiry": token_data.get("expires_in"),
            "service": None,  # Will be lazily created when needed
        }

        return user_id

    def list_authenticated_users(self) -> List[str]:
        """
        List all authenticated users.

        Returns:
            List of user IDs
        """
        # In a real application, you would query your token store
        # For this example, we'll return keys from our in-memory dict
        return list(self._user_services.keys())

    def remove_user_authentication(self, user_id: str) -> None:
        """
        Remove authentication for a specific user.

        Args:
            user_id: The user ID to remove
        """
        if user_id in self._user_services:
            del self._user_services[user_id]

    def get_service_for_user(self, user_id: str):
        """
        Get the Drive API service for a specific user.

        Args:
            user_id: The user ID to get service for

        Returns:
            The Drive API service object

        Raises:
            AuthenticationError: If user has no valid credentials
        """
        if user_id not in self._user_services:
            raise AuthenticationError(f"No credentials found for user {user_id}")

        user_data = self._user_services[user_id]

        # If service already exists, return it
        if user_data["service"]:
            return user_data["service"]

        # Otherwise, create a new service
        from google.oauth2.credentials import Credentials

        # Create credentials object from stored tokens
        credentials = Credentials(
            token=user_data["access_token"],
            refresh_token=user_data["refresh_token"],
            token_uri=self.settings.GOOGLE_TOKEN_URI,
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=self._scopes,
        )

        # Build and cache the service
        try:
            service = build("drive", "v3", credentials=credentials)
            user_data["service"] = service
            return service
        except Exception as e:
            raise AuthenticationError(f"Failed to build Drive service: {str(e)}")

    def get_current_user_service(self):
        """
        Get the Drive API service for the current user context.

        Returns:
            The Drive API service object

        Raises:
            AuthenticationError: If no user context is set or user has no valid credentials
        """
        if not self._current_user_id:
            raise AuthenticationError(
                "No user context set. Call for_user() or use user_context() first."
            )

        return self.get_service_for_user(self._current_user_id)
