"""
REST client implementation.
"""

from typing import Any, Dict, List, Optional, Union

from usepolvo_core.auth.base import Auth
from usepolvo_core.core.client import AsyncClient, Client
from usepolvo_core.core.response import Response
from usepolvo_core.middleware.base import Middleware


class RestClient(Client):
    """REST client for making RESTful API requests."""

    def __init__(
        self,
        base_url: str = "",
        auth: Optional[Auth] = None,
        middlewares: Optional[List[Middleware]] = None,
        timeout: Union[float, tuple] = 10.0,
        verify: bool = True,
        **kwargs,
    ):
        """
        Initialize a REST client.

        Args:
            base_url: Base URL for all requests
            auth: Authentication method
            middlewares: List of middleware to apply to requests
            timeout: Request timeout in seconds
            verify: Verify SSL certificates
            **kwargs: Additional keyword arguments to pass to the underlying transport
        """
        super().__init__(
            base_url=base_url,
            auth=auth,
            middlewares=middlewares,
            timeout=timeout,
            verify=verify,
            **kwargs,
        )

    def resource(self, path: str) -> "ResourceClient":
        """
        Create a resource client for a specific API endpoint.

        Args:
            path: Resource path

        Returns:
            ResourceClient for the specified path
        """
        return ResourceClient(self, path)


class AsyncRestClient(AsyncClient):
    """Asynchronous REST client for making RESTful API requests."""

    def __init__(
        self,
        base_url: str = "",
        auth: Optional[Auth] = None,
        middlewares: Optional[List[Middleware]] = None,
        timeout: Union[float, tuple] = 10.0,
        verify: bool = True,
        **kwargs,
    ):
        """
        Initialize an asynchronous REST client.

        Args:
            base_url: Base URL for all requests
            auth: Authentication method
            middlewares: List of middleware to apply to requests
            timeout: Request timeout in seconds
            verify: Verify SSL certificates
            **kwargs: Additional keyword arguments to pass to the underlying transport
        """
        super().__init__(
            base_url=base_url,
            auth=auth,
            middlewares=middlewares,
            timeout=timeout,
            verify=verify,
            **kwargs,
        )

    def resource(self, path: str) -> "AsyncResourceClient":
        """
        Create an asynchronous resource client for a specific API endpoint.

        Args:
            path: Resource path

        Returns:
            AsyncResourceClient for the specified path
        """
        return AsyncResourceClient(self, path)


class ResourceClient:
    """Client for a specific REST resource."""

    def __init__(self, client: RestClient, path: str):
        """
        Initialize a ResourceClient.

        Args:
            client: REST client
            path: Resource path
        """
        self.client = client
        self.path = path.strip("/")

    def __call__(self, resource_id: Optional[str] = None) -> "ResourceClient":
        """
        Create a sub-resource client.

        Args:
            resource_id: Resource ID or sub-path

        Returns:
            ResourceClient for the specified sub-resource
        """
        if resource_id is None:
            return self

        return ResourceClient(self.client, f"{self.path}/{resource_id}")

    def _url(self, path: Optional[str] = None) -> str:
        """
        Build resource URL.

        Args:
            path: Additional path

        Returns:
            Complete URL
        """
        if path:
            return f"{self.path}/{path.lstrip('/')}"
        return self.path

    def get(self, path: Optional[str] = None, **kwargs) -> Response:
        """
        Make a GET request to the resource.

        Args:
            path: Additional path
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response
        """
        return self.client.get(self._url(path), **kwargs)

    def post(self, path: Optional[str] = None, **kwargs) -> Response:
        """
        Make a POST request to the resource.

        Args:
            path: Additional path
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response
        """
        return self.client.post(self._url(path), **kwargs)

    def put(self, path: Optional[str] = None, **kwargs) -> Response:
        """
        Make a PUT request to the resource.

        Args:
            path: Additional path
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response
        """
        return self.client.put(self._url(path), **kwargs)

    def patch(self, path: Optional[str] = None, **kwargs) -> Response:
        """
        Make a PATCH request to the resource.

        Args:
            path: Additional path
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response
        """
        return self.client.patch(self._url(path), **kwargs)

    def delete(self, path: Optional[str] = None, **kwargs) -> Response:
        """
        Make a DELETE request to the resource.

        Args:
            path: Additional path
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response
        """
        return self.client.delete(self._url(path), **kwargs)


class AsyncResourceClient:
    """Asynchronous client for a specific REST resource."""

    def __init__(self, client: AsyncRestClient, path: str):
        """
        Initialize an AsyncResourceClient.

        Args:
            client: Asynchronous REST client
            path: Resource path
        """
        self.client = client
        self.path = path.strip("/")

    def __call__(self, resource_id: Optional[str] = None) -> "AsyncResourceClient":
        """
        Create a sub-resource client.

        Args:
            resource_id: Resource ID or sub-path

        Returns:
            AsyncResourceClient for the specified sub-resource
        """
        if resource_id is None:
            return self

        return AsyncResourceClient(self.client, f"{self.path}/{resource_id}")

    def _url(self, path: Optional[str] = None) -> str:
        """
        Build resource URL.

        Args:
            path: Additional path

        Returns:
            Complete URL
        """
        if path:
            return f"{self.path}/{path.lstrip('/')}"
        return self.path

    async def get(self, path: Optional[str] = None, **kwargs) -> Response:
        """
        Make a GET request to the resource.

        Args:
            path: Additional path
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response
        """
        return await self.client.get(self._url(path), **kwargs)

    async def post(self, path: Optional[str] = None, **kwargs) -> Response:
        """
        Make a POST request to the resource.

        Args:
            path: Additional path
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response
        """
        return await self.client.post(self._url(path), **kwargs)

    async def put(self, path: Optional[str] = None, **kwargs) -> Response:
        """
        Make a PUT request to the resource.

        Args:
            path: Additional path
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response
        """
        return await self.client.put(self._url(path), **kwargs)

    async def patch(self, path: Optional[str] = None, **kwargs) -> Response:
        """
        Make a PATCH request to the resource.

        Args:
            path: Additional path
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response
        """
        return await self.client.patch(self._url(path), **kwargs)

    async def delete(self, path: Optional[str] = None, **kwargs) -> Response:
        """
        Make a DELETE request to the resource.

        Args:
            path: Additional path
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response
        """
        return await self.client.delete(self._url(path), **kwargs)
