"""
Main API client that provides a requests-like interface.
"""

import httpx
from typing import Any, Dict, Optional, Union, List, Tuple
from urllib.parse import urljoin

from .auth.base import AuthStrategy
from .resilience import RetryStrategy, RateLimiter
from .storage.base import TokenStorage


class Session:
    """
    HTTP session for making requests with shared configuration.
    
    Similar to requests.Session, handles authentication, retry, rate limiting, 
    and multi-tenant scenarios while providing a familiar requests-style API.
    """
    
    def __init__(
        self,
        base_url: str,
        auth: Optional[AuthStrategy] = None,
        retry: Optional[RetryStrategy] = None,
        rate_limit: Optional[RateLimiter] = None,
        # circuit_breaker: Optional[CircuitBreaker] = None,  # TODO: Implement circuit breaker
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
    
    # Class method constructors for common patterns
    @classmethod
    def with_auth(cls, base_url: str, auth, **kwargs) -> 'Session':
        """
        Create a Session with authentication configured.
        
        Args:
            base_url: Base URL for all requests
            auth: Authentication strategy
            **kwargs: Additional Session arguments
            
        Example:
            session = polvo.Session.with_auth(
                "https://api.example.com",
                polvo.auth.bearer("token123")
            )
        """
        return cls(base_url, auth=auth, **kwargs)

    @classmethod  
    def with_retry(cls, base_url: str, max_retries: int = 3, **kwargs) -> 'Session':
        """
        Create a Session with simple retry configuration.
        
        Args:
            base_url: Base URL for all requests  
            max_retries: Maximum number of retries (uses exponential backoff)
            **kwargs: Additional Session arguments
            
        Example:
            session = polvo.Session.with_retry(
                "https://api.example.com",
                max_retries=5
            )
        """
        from . import retry
        retry_strategy = retry.exponential_backoff(max_retries=max_retries)
        return cls(base_url, retry=retry_strategy, **kwargs)

    @classmethod
    def for_api(cls, base_url: str, api_key: str, **kwargs) -> 'Session':
        """
        Create a Session configured for API key authentication.
        
        Args:
            base_url: Base URL for all requests
            api_key: API key value  
            **kwargs: Additional Session arguments (including 'header_name' for API key header)
            
        Example:
            session = polvo.Session.for_api(
                "https://api.example.com",
                "your-api-key-here"
            )
        """
        from . import auth
        header_name = kwargs.pop('header_name', 'X-API-Key')
        api_auth = auth.api_key(api_key, header_name)
        return cls(base_url, auth=api_auth, **kwargs)


class AsyncSession:
    """
    Async HTTP session for making requests with shared configuration.
    
    Provides the same interface as Session but with async/await support.
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





# Module-level convenience functions (like requests)
def _create_session_from_kwargs(**kwargs) -> Tuple[Session, Dict[str, Any]]:
    """Extract session-related kwargs and create a temporary Session."""
    session_kwargs = {}
    request_kwargs = {}
    
    # Session-level arguments
    session_args = {'auth', 'retry', 'rate_limit', 'timeout', 'headers'}
    
    for key, value in kwargs.items():
        if key in session_args:
            session_kwargs[key] = value
        else:
            request_kwargs[key] = value
    
    session = Session("", **session_kwargs)
    return session, request_kwargs


def get(url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
    """
    Make a GET request.
    
    Args:
        url: Complete URL to request
        params: Query parameters
        auth: Authentication strategy (Bearer, Basic, etc.)
        headers: Additional headers
        timeout: Request timeout
        **kwargs: Additional arguments passed to the request
    """
    session, request_kwargs = _create_session_from_kwargs(**kwargs)
    with session:
        return session.get(url, params=params, **request_kwargs)


def post(url: str, data: Any = None, json: Any = None, **kwargs) -> httpx.Response:
    """
    Make a POST request.
    
    Args:
        url: Complete URL to request
        data: Form data to send
        json: JSON data to send
        auth: Authentication strategy
        **kwargs: Additional arguments
    """
    session, request_kwargs = _create_session_from_kwargs(**kwargs)
    with session:
        return session.post(url, data=data, json=json, **request_kwargs)


def put(url: str, data: Any = None, json: Any = None, **kwargs) -> httpx.Response:
    """Make a PUT request."""
    session, request_kwargs = _create_session_from_kwargs(**kwargs)
    with session:
        return session.put(url, data=data, json=json, **request_kwargs)


def patch(url: str, data: Any = None, json: Any = None, **kwargs) -> httpx.Response:
    """Make a PATCH request."""
    session, request_kwargs = _create_session_from_kwargs(**kwargs)
    with session:
        return session.patch(url, data=data, json=json, **request_kwargs)


def delete(url: str, **kwargs) -> httpx.Response:
    """Make a DELETE request."""
    session, request_kwargs = _create_session_from_kwargs(**kwargs)
    with session:
        return session.delete(url, **request_kwargs)


def head(url: str, **kwargs) -> httpx.Response:
    """Make a HEAD request."""
    session, request_kwargs = _create_session_from_kwargs(**kwargs)
    with session:
        return session.head(url, **request_kwargs)


def options(url: str, **kwargs) -> httpx.Response:
    """Make an OPTIONS request."""
    session, request_kwargs = _create_session_from_kwargs(**kwargs)
    with session:
        return session.options(url, **request_kwargs) 