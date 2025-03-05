# core/clients/base.py
from typing import Any, Dict, Optional

import requests

from usepolvo.core.auth import BaseAuth
from usepolvo.core.exceptions import APIError, AuthenticationError


class BaseClient:
    """Minimal base API client."""

    def __init__(self):
        self.base_url: Optional[str] = None
        self.auth: Optional[BaseAuth] = None

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request with error handling."""
        if not self.base_url:
            raise ValueError("base_url must be set")

        # Prepare URL and headers
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = kwargs.pop("headers", {})

        if self.auth:
            headers.update(self.auth.get_auth_headers())

        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (401, 403):
                raise AuthenticationError(f"Authentication failed: {e.response.text}")
            raise APIError(f"Request failed: {e.response.text}")

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
