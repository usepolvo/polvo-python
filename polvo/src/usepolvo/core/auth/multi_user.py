# src/usepolvo/core/auth/multi_user.py
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from usepolvo.core.auth.oauth2 import OAuth2Auth
from usepolvo.core.auth.tokens import TokenStore
from usepolvo.core.exceptions import AuthenticationError


class MultiUserOAuth2Auth(OAuth2Auth):
    """
    Extended OAuth2Auth class that supports multiple users.
    Handles per-user authentication flows and token management.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        auth_url: str,
        token_url: str,
        redirect_uri: str,
        scopes: List[str],
        token_store: Optional[TokenStore] = None,
        service_name: str = "oauth2",
    ):
        """
        Initialize multi-user OAuth2 authentication.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            auth_url: Authorization URL
            token_url: Token URL
            redirect_uri: Redirect URI
            scopes: OAuth scopes
            token_store: Optional custom token store
            service_name: Service name for token storage
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            auth_url=auth_url,
            token_url=token_url,
            redirect_uri=redirect_uri,
            scopes=scopes,
        )

        self.token_store = token_store or TokenStore()
        self.service_name = service_name
        self._current_user_id = None

    def get_user_auth_url(
        self, user_id: str, additional_params: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate an authorization URL for a specific user.

        Args:
            user_id: User ID to generate URL for
            additional_params: Additional URL parameters

        Returns:
            Authorization URL
        """
        # Create a state parameter that includes the user ID
        state = f"user_{user_id}_{int(time.time())}"

        # Build the parameters with the state
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "state": state,
            "access_type": "offline",  # Request refresh token
            "prompt": "consent",  # Force consent screen for refresh token
        }

        # Add any additional parameters
        if additional_params:
            params.update(additional_params)

        # Build and return the URL
        return self._build_url(self.auth_url, params)

    def process_callback(self, callback_url: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process an OAuth callback, extract the user ID from state, and store tokens.

        Args:
            callback_url: The full callback URL

        Returns:
            Tuple of (user_id, token_data)

        Raises:
            AuthenticationError: If authentication fails
        """
        # Parse the URL
        parsed_url = urlparse(callback_url)
        params = parse_qs(parsed_url.query)

        # Check for errors
        if "error" in params:
            raise AuthenticationError(f"OAuth error: {params['error'][0]}")

        # Extract the code
        if "code" not in params:
            raise AuthenticationError("No authorization code found in callback")
        code = params["code"][0]

        # Extract user ID from state
        if "state" not in params:
            raise AuthenticationError("No state parameter found in callback")

        state = params["state"][0]
        # In a real implementation, validate state against stored state
        if not state.startswith("user_"):
            raise AuthenticationError("Invalid state parameter")

        # Extract user ID from state (format: user_{id}_{timestamp})
        user_id = state.split("_")[1]

        # Exchange code for tokens
        token_data = self.exchange_code(code)

        # Store tokens for this user
        self.store_user_tokens(user_id, token_data)

        return user_id, token_data

    def store_user_tokens(self, user_id: str, tokens: Dict[str, Any]) -> None:
        """
        Store tokens for a specific user.

        Args:
            user_id: User ID
            tokens: Token data
        """
        # Add the scopes to the token data
        tokens["scopes"] = self.scopes

        # Store the tokens
        self.token_store.save_tokens(f"{self.service_name}_{user_id}", tokens)

    def get_user_tokens(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tokens for a specific user.

        Args:
            user_id: User ID

        Returns:
            Token data or None if not found
        """
        return self.token_store.load_tokens(f"{self.service_name}_{user_id}")

    def delete_user_tokens(self, user_id: str) -> None:
        """
        Delete tokens for a specific user.

        Args:
            user_id: User ID
        """
        self.token_store.delete_tokens(f"{self.service_name}_{user_id}")

    def get_auth_headers_for_user(self, user_id: str) -> Dict[str, str]:
        """
        Get authentication headers for a specific user.

        Args:
            user_id: User ID

        Returns:
            Authentication headers

        Raises:
            AuthenticationError: If user has no valid tokens
        """
        tokens = self.get_user_tokens(user_id)
        if not tokens or "access_token" not in tokens:
            raise AuthenticationError(f"No access token for user {user_id}")

        # Check if token is expired
        if "expires_in" in tokens and time.time() >= tokens.get("token_expiry", 0):
            # Try to refresh the token
            self.refresh_token = tokens.get("refresh_token")
            try:
                new_tokens = self.refresh_tokens()

                # Add the scopes to the new tokens
                new_tokens["scopes"] = tokens.get("scopes", self.scopes)

                # Preserve the refresh token if we didn't get a new one
                if "refresh_token" not in new_tokens and "refresh_token" in tokens:
                    new_tokens["refresh_token"] = tokens["refresh_token"]

                # Store the new tokens
                self.store_user_tokens(user_id, new_tokens)

                # Return headers with new access token
                return {"Authorization": f"Bearer {new_tokens['access_token']}"}

            except Exception as e:
                raise AuthenticationError(f"Failed to refresh token for user {user_id}: {str(e)}")

        # Return headers with current access token
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    def set_current_user(self, user_id: Optional[str]) -> None:
        """
        Set the current user context.

        Args:
            user_id: User ID or None to clear
        """
        self._current_user_id = user_id

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Override the base method to use the current user context.

        Returns:
            Authentication headers

        Raises:
            AuthenticationError: If no user context is set or user has no valid tokens
        """
        if not self._current_user_id:
            raise AuthenticationError("No user context set. Call set_current_user() first.")

        return self.get_auth_headers_for_user(self._current_user_id)

    def list_authenticated_users(self) -> List[str]:
        """
        List all authenticated users.

        Returns:
            List of user IDs
        """
        # The token store doesn't have a direct way to list all tokens,
        # so this is a simple implementation that would need to be enhanced
        # with a proper user registry in production

        # This is a placeholder implementation
        return []  # In a real implementation, this would return a list of user IDs
