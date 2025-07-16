"""
Main API client that provides a requests-like interface.
"""

import httpx
from typing import Any, Dict, Optional, Union, List
from urllib.parse import urljoin

from .auth.base import AuthStrategy
from .resilience import RetryStrategy, RateLimiter
from .storage.base import TokenStorage


class API:
    """
    Main API client with requests-like interface.
    
    Handles authentication, retry, rate limiting, and multi-tenant scenarios
    transparently while providing a familiar requests-style API.
    """
    
    def __init__(
        self,
        base_url: str,
        auth: Optional[AuthStrategy] = None,
        retry: Optional[RetryStrategy] = None,
        rate_limit: Optional[RateLimiter] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for all requests
            auth: Authentication strategy (Bearer, OAuth2, etc.)
            retry: Retry strategy with exponential backoff
            rate_limit: Rate limiting strategy
            timeout: Request timeout in seconds
            headers: Default headers to include with requests
            **kwargs: Additional arguments passed to httpx.Client
        """
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.retry = retry
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.default_headers = headers or {}
        
        # Initialize httpx client
        self._client = httpx.Client(
            timeout=timeout,
            **kwargs
        )
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def close(self):
        """Close the underlying HTTP client."""
        self._client.close()
        

    
    def _build_url(self, path: str) -> str:
        """Build full URL from base URL and path."""
        if path.startswith(('http://', 'https://')):
            return path
        return urljoin(self.base_url + '/', path.lstrip('/'))
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare headers including auth and defaults."""
        final_headers = self.default_headers.copy()
        if headers:
            final_headers.update(headers)
            
        # Apply authentication
        if self.auth:
            auth_headers = self.auth.get_headers()
            final_headers.update(auth_headers)
            
        return final_headers
    
    def _make_request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Make an HTTP request with all the resilience patterns applied.
        """
        full_url = self._build_url(url)
        final_headers = self._prepare_headers(headers)
        
        # Apply rate limiting
        if self.rate_limit:
            self.rate_limit.acquire()
        
        # Apply retry logic if configured
        if self.retry:
            return self.retry.execute(
                lambda: self._client.request(
                    method, full_url, headers=final_headers, **kwargs
                )
            )
        
        # Simple request without retry
        return self._client.request(method, full_url, headers=final_headers, **kwargs)
    
    # Requests-like interface methods
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        """Make a GET request."""
        return self._make_request('GET', url, params=params, **kwargs)
    
    def post(self, url: str, data: Any = None, json: Any = None, **kwargs) -> httpx.Response:
        """Make a POST request."""
        return self._make_request('POST', url, data=data, json=json, **kwargs)
    
    def put(self, url: str, data: Any = None, json: Any = None, **kwargs) -> httpx.Response:
        """Make a PUT request."""
        return self._make_request('PUT', url, data=data, json=json, **kwargs)
    
    def patch(self, url: str, data: Any = None, json: Any = None, **kwargs) -> httpx.Response:
        """Make a PATCH request."""
        return self._make_request('PATCH', url, data=data, json=json, **kwargs)
    
    def delete(self, url: str, **kwargs) -> httpx.Response:
        """Make a DELETE request."""
        return self._make_request('DELETE', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> httpx.Response:
        """Make a HEAD request."""
        return self._make_request('HEAD', url, **kwargs)
    
    def options(self, url: str, **kwargs) -> httpx.Response:
        """Make an OPTIONS request."""
        return self._make_request('OPTIONS', url, **kwargs)


class AsyncAPI:
    """
    Async version of the API client.
    
    Provides the same interface as API but with async/await support.
    """
    
    def __init__(
        self,
        base_url: str,
        auth: Optional[AuthStrategy] = None,
        retry: Optional[RetryStrategy] = None,
        rate_limit: Optional[RateLimiter] = None,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.retry = retry
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.default_headers = headers or {}
        
        # Initialize async httpx client
        self._client = httpx.AsyncClient(
            timeout=timeout,
            **kwargs
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the underlying HTTP client."""
        await self._client.aclose()
    

    
    def _build_url(self, path: str) -> str:
        """Build full URL from base URL and path."""
        if path.startswith(('http://', 'https://')):
            return path
        return urljoin(self.base_url + '/', path.lstrip('/'))
    
    async def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare headers including auth and defaults."""
        final_headers = self.default_headers.copy()
        if headers:
            final_headers.update(headers)
            
        # Apply authentication (async)
        if self.auth:
            if hasattr(self.auth, 'get_headers_async'):
                auth_headers = await self.auth.get_headers_async()
            else:
                auth_headers = self.auth.get_headers()
            final_headers.update(auth_headers)
            
        return final_headers
    
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Make an async HTTP request with resilience patterns."""
        full_url = self._build_url(url)
        final_headers = await self._prepare_headers(headers)
        
        # Apply rate limiting
        if self.rate_limit and hasattr(self.rate_limit, 'acquire_async'):
            await self.rate_limit.acquire_async()
        elif self.rate_limit:
            self.rate_limit.acquire()
        
        # Apply retry logic if configured
        if self.retry and hasattr(self.retry, 'execute_async'):
            return await self.retry.execute_async(
                lambda: self._client.request(
                    method, full_url, headers=final_headers, **kwargs
                )
            )
        
        # Simple request without retry
        return await self._client.request(method, full_url, headers=final_headers, **kwargs)
    
    # Async requests-like interface methods
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        """Make an async GET request."""
        return await self._make_request('GET', url, params=params, **kwargs)
    
    async def post(self, url: str, data: Any = None, json: Any = None, **kwargs) -> httpx.Response:
        """Make an async POST request."""
        return await self._make_request('POST', url, data=data, json=json, **kwargs)
    
    async def put(self, url: str, data: Any = None, json: Any = None, **kwargs) -> httpx.Response:
        """Make an async PUT request."""
        return await self._make_request('PUT', url, data=data, json=json, **kwargs)
    
    async def patch(self, url: str, data: Any = None, json: Any = None, **kwargs) -> httpx.Response:
        """Make an async PATCH request."""
        return await self._make_request('PATCH', url, data=data, json=json, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Make an async DELETE request."""
        return await self._make_request('DELETE', url, **kwargs)
    
    async def head(self, url: str, **kwargs) -> httpx.Response:
        """Make an async HEAD request."""
        return await self._make_request('HEAD', url, **kwargs)
    
    async def options(self, url: str, **kwargs) -> httpx.Response:
        """Make an async OPTIONS request."""
        return await self._make_request('OPTIONS', url, **kwargs) 