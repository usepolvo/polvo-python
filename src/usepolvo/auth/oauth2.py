"""
OAuth2 authentication with automatic token refresh.

This is the crown jewel of the auth module - handles complex OAuth2 flows transparently.
"""

import time
import httpx
import threading
from typing import Dict, Optional
from .base import AuthStrategy
from ..storage.base import TokenStorage


class OAuth2Flow(AuthStrategy):
    """
    OAuth2 authentication with automatic token refresh.
    
    This class handles:
    - Client credentials flow for machine-to-machine authentication
    - Automatic token refresh when tokens expire
    - Thread-safe token operations
    - Graceful error handling and recovery
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: str = "",
        storage: Optional[TokenStorage] = None
    ):
        """
        Initialize OAuth2 flow.
        
        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            token_url: Token endpoint URL
            scope: OAuth2 scopes (space-separated)
            storage: Token storage backend
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.scope = scope
        self.storage = storage
        
        # Thread safety for token refresh
        self._lock = threading.Lock()
        self._current_token = None
        self._token_expires_at = 0
        
        # Load existing token if available
        self._load_token()
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get OAuth2 authentication headers with automatic token refresh.
        
        Returns:
            Dictionary with Authorization header
        """
        token = self._get_valid_token()
        return {"Authorization": f"Bearer {token}"}
    

    
    def _get_valid_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token
            
        Raises:
            Exception: If unable to obtain a valid token
        """
        with self._lock:
            # Check if current token is still valid
            if self._current_token and time.time() < self._token_expires_at - 60:  # 60s buffer
                return self._current_token
            
            # Need to refresh or obtain new token
            return self._refresh_token()
    
    def _refresh_token(self) -> str:
        """
        Refresh or obtain a new access token using client credentials flow.
        
        Returns:
            New access token
            
        Raises:
            Exception: If token refresh fails
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        if self.scope:
            data["scope"] = self.scope
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.token_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0
                )
                response.raise_for_status()
                
                token_data = response.json()
                
                # Extract token information
                access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
                
                # Update internal state
                self._current_token = access_token
                self._token_expires_at = time.time() + expires_in
                
                # Store token for persistence
                self._store_token(token_data)
                
                return access_token
                
        except Exception as e:
            raise Exception(f"OAuth2 token refresh failed: {str(e)}")
    
    def _load_token(self):
        """Load existing token from storage if available."""
        if not self.storage:
            return
            
        try:
            token_data = self.storage.get_token(self._get_storage_key())
            if token_data and "access_token" in token_data:
                self._current_token = token_data["access_token"]
                
                # Calculate expiration time
                if "expires_at" in token_data:
                    self._token_expires_at = token_data["expires_at"]
                elif "expires_in" in token_data and "created_at" in token_data:
                    self._token_expires_at = token_data["created_at"] + token_data["expires_in"]
                else:
                    # If no expiration info, assume expired to force refresh
                    self._token_expires_at = 0
                    
        except Exception:
            # If loading fails, we'll just get a new token
            pass
    
    def _store_token(self, token_data: Dict):
        """Store token data for persistence."""
        if not self.storage:
            return
            
        try:
            # Add metadata for expiration calculation
            storage_data = token_data.copy()
            storage_data["created_at"] = time.time()
            storage_data["expires_at"] = self._token_expires_at
            
            self.storage.store_token(self._get_storage_key(), storage_data)
        except Exception:
            # Storage failures shouldn't break the auth flow
            pass
    
    def _get_storage_key(self) -> str:
        """Get storage key for this OAuth2 flow."""
        return f"oauth2_{self.client_id}"
    
    def revoke_token(self):
        """
        Revoke the current token and clear from storage.
        
        Useful for logout scenarios or when credentials change.
        """
        with self._lock:
            self._current_token = None
            self._token_expires_at = 0
            
            if self.storage:
                try:
                    self.storage.delete_token(self._get_storage_key())
                except Exception:
                    pass
    
    def force_refresh(self) -> str:
        """
        Force a token refresh regardless of current token validity.
        
        Returns:
            New access token
        """
        with self._lock:
            return self._refresh_token() 