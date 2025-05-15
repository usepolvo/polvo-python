"""
Core client classes for making HTTP requests.
"""

from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from usepolvo_core.auth.base import Auth
from usepolvo_core.core.exceptions import PolvoError, TransportError
from usepolvo_core.core.response import Response
from usepolvo_core.middleware.base import Middleware


class BaseClient:
    """Base class for Polvo clients."""

    def __init__(
        self,
        base_url: str = "",
        auth: Optional[Auth] = None,
        middlewares: Optional[List[Middleware]] = None,
        timeout: Union[float, tuple, httpx.Timeout] = 10.0,
        verify: bool = True,
        **kwargs,
    ):
        """
        Initialize a BaseClient.

        Args:
            base_url: Base URL for all requests
            auth: Authentication method
            middlewares: List of middleware to apply to requests
            timeout: Request timeout in seconds
            verify: Verify SSL certificates
            **kwargs: Additional keyword arguments to pass to the underlying transport
        """
        self.base_url = base_url
        self.auth = auth
        self.middlewares = middlewares or []

        if isinstance(timeout, (int, float)):
            self.timeout = httpx.Timeout(timeout)
        elif isinstance(timeout, tuple):
            self.timeout = httpx.Timeout(*timeout)
        else:
            self.timeout = timeout

        self.verify = verify
        self.kwargs = kwargs


class Client(BaseClient):
    """Synchronous HTTP client for making requests."""

    def __init__(self, *args, **kwargs):
        """Initialize a synchronous Client."""
        super().__init__(*args, **kwargs)
        self._client = httpx.Client(timeout=self.timeout, verify=self.verify, **self.kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Response:
        """
        Make a synchronous HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request (will be joined with base_url)
            params: Query parameters
            headers: HTTP headers
            cookies: Cookies to send
            data: Form data or raw request body
            json: JSON data to send
            files: Files to upload
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response object

        Raises:
            PolvoError: If the request fails
        """
        # Apply middlewares (pre-request)
        request_url = urljoin(self.base_url, url)

        # Apply authentication if provided
        final_headers = headers or {}
        if self.auth:
            final_headers = self.auth.sign(method, request_url, final_headers)

        # Create and apply middlewares to request params
        request_kwargs = {
            "method": method,
            "url": request_url,
            "params": params,
            "headers": final_headers,
            "cookies": cookies,
            "data": data,
            "json": json,
            "files": files,
            **kwargs,
        }

        for middleware in self.middlewares:
            request_kwargs = middleware.pre_request(request_kwargs)

        # Extract retry configuration if present
        retry_config = request_kwargs.pop("_retry_config", None)
        retries_left = retry_config.get("count", 0) if retry_config else 0
        retry_status_codes = retry_config.get("status_codes", []) if retry_config else []
        backoff_factor = retry_config.get("backoff_factor", 0.3) if retry_config else 0.3

        # Initial attempt
        attempt = 0
        last_exception = None

        while True:
            try:
                httpx_response = self._client.request(**request_kwargs)
                response = Response.from_httpx(httpx_response)

                # Check if we should retry based on status code
                if retries_left > 0 and response.status_code in retry_status_codes:
                    attempt += 1
                    retries_left -= 1
                    if retries_left >= 0:
                        # Calculate backoff time with jitter
                        backoff_time = backoff_factor * (2**attempt)
                        import random
                        import time

                        backoff_time = backoff_time + (random.randint(0, 1000) / 1000.0)
                        time.sleep(backoff_time)
                        continue

                # Apply middlewares (post-request)
                for middleware in self.middlewares:
                    response = middleware.post_request(response)

                return response

            except httpx.RequestError as exc:
                last_exception = exc
                attempt += 1
                retries_left -= 1

                if retries_left < 0:
                    raise TransportError(f"Request failed: {str(exc)}") from exc

                # Calculate backoff time with jitter
                backoff_time = backoff_factor * (2**attempt)
                import random
                import time

                backoff_time = backoff_time + (random.randint(0, 1000) / 1000.0)
                time.sleep(backoff_time)

    def get(self, url: str, **kwargs) -> Response:
        """Make a GET request."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Response:
        """Make a POST request."""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> Response:
        """Make a PUT request."""
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs) -> Response:
        """Make a PATCH request."""
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs) -> Response:
        """Make a DELETE request."""
        return self.request("DELETE", url, **kwargs)

    def head(self, url: str, **kwargs) -> Response:
        """Make a HEAD request."""
        return self.request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs) -> Response:
        """Make an OPTIONS request."""
        return self.request("OPTIONS", url, **kwargs)

    def close(self):
        """Close the underlying transport."""
        self._client.close()


class AsyncClient(BaseClient):
    """Asynchronous HTTP client for making requests."""

    def __init__(self, *args, **kwargs):
        """Initialize an asynchronous Client."""
        super().__init__(*args, **kwargs)
        self._client = httpx.AsyncClient(timeout=self.timeout, verify=self.verify, **self.kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Response:
        """
        Make an asynchronous HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request (will be joined with base_url)
            params: Query parameters
            headers: HTTP headers
            cookies: Cookies to send
            data: Form data or raw request body
            json: JSON data to send
            files: Files to upload
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response object

        Raises:
            PolvoError: If the request fails
        """
        # Apply middlewares (pre-request)
        request_url = urljoin(self.base_url, url)

        # Apply authentication if provided
        final_headers = headers or {}
        if self.auth:
            final_headers = self.auth.sign(method, request_url, final_headers)

        # Create and apply middlewares to request params
        request_kwargs = {
            "method": method,
            "url": request_url,
            "params": params,
            "headers": final_headers,
            "cookies": cookies,
            "data": data,
            "json": json,
            "files": files,
            **kwargs,
        }

        for middleware in self.middlewares:
            request_kwargs = middleware.pre_request(request_kwargs)

        # Extract retry configuration if present
        retry_config = request_kwargs.pop("_retry_config", None)
        retries_left = retry_config.get("count", 0) if retry_config else 0
        retry_status_codes = retry_config.get("status_codes", []) if retry_config else []
        backoff_factor = retry_config.get("backoff_factor", 0.3) if retry_config else 0.3

        # Initial attempt
        attempt = 0
        last_exception = None

        while True:
            try:
                httpx_response = await self._client.request(**request_kwargs)
                response = Response.from_httpx(httpx_response)

                # Check if we should retry based on status code
                if retries_left > 0 and response.status_code in retry_status_codes:
                    attempt += 1
                    retries_left -= 1
                    if retries_left >= 0:
                        # Calculate backoff time with jitter
                        backoff_time = backoff_factor * (2**attempt)
                        import asyncio
                        import random

                        backoff_time = backoff_time + (random.randint(0, 1000) / 1000.0)
                        await asyncio.sleep(backoff_time)
                        continue

                # Apply middlewares (post-request)
                for middleware in self.middlewares:
                    response = middleware.post_request(response)

                return response

            except httpx.RequestError as exc:
                last_exception = exc
                attempt += 1
                retries_left -= 1

                if retries_left < 0:
                    raise TransportError(f"Request failed: {str(exc)}") from exc

                # Calculate backoff time with jitter
                backoff_time = backoff_factor * (2**attempt)
                import asyncio
                import random

                backoff_time = backoff_time + (random.randint(0, 1000) / 1000.0)
                await asyncio.sleep(backoff_time)

    async def get(self, url: str, **kwargs) -> Response:
        """Make a GET request."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> Response:
        """Make a POST request."""
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> Response:
        """Make a PUT request."""
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> Response:
        """Make a PATCH request."""
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> Response:
        """Make a DELETE request."""
        return await self.request("DELETE", url, **kwargs)

    async def head(self, url: str, **kwargs) -> Response:
        """Make a HEAD request."""
        return await self.request("HEAD", url, **kwargs)

    async def options(self, url: str, **kwargs) -> Response:
        """Make an OPTIONS request."""
        return await self.request("OPTIONS", url, **kwargs)

    async def close(self):
        """Close the underlying transport."""
        await self._client.aclose()
