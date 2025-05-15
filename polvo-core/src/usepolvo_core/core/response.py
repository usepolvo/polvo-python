"""
Response class for handling HTTP responses.
"""

from typing import Any, Dict, Optional, Union

import httpx


class Response:
    """HTTP response object."""

    def __init__(
        self,
        status_code: int,
        headers: Dict[str, str],
        content: bytes,
        url: str,
        request_info: Optional[Dict[str, Any]] = None,
        encoding: Optional[str] = None,
        elapsed: Optional[float] = None,
    ):
        """
        Initialize a Response object.

        Args:
            status_code: HTTP status code
            headers: Response headers
            content: Response body
            url: Response URL
            request_info: Information about the request
            encoding: Response encoding
            elapsed: Time elapsed since request was sent
        """
        self.status_code = status_code
        self.headers = headers
        self._content = content
        self.url = url
        self.request_info = request_info or {}
        self.encoding = encoding
        self.elapsed = elapsed

    @property
    def ok(self) -> bool:
        """Return True if status_code is less than 400."""
        return self.status_code < 400

    @property
    def content(self) -> bytes:
        """Return the response content as bytes."""
        return self._content

    def text(self) -> str:
        """Return the response content as a string."""
        if self.encoding:
            return self._content.decode(self.encoding)
        return self._content.decode("utf-8")

    def json(self) -> Any:
        """Return the response content as a JSON object."""
        import json

        return json.loads(self.text())

    @classmethod
    def from_httpx(cls, response: httpx.Response) -> "Response":
        """
        Create a Response object from an httpx.Response.

        Args:
            response: httpx.Response object

        Returns:
            Response object
        """
        request_info = {
            "method": response.request.method,
            "url": str(response.request.url),
            "headers": dict(response.request.headers),
        }

        return cls(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
            url=str(response.url),
            request_info=request_info,
            encoding=response.encoding,
            elapsed=response.elapsed.total_seconds() if response.elapsed else None,
        )

    def raise_for_status(self) -> None:
        """
        Raise an HTTPError if the response has a status code >= 400.

        Raises:
            HTTPError: If the response has a status code >= 400
        """
        from usepolvo_core.src.core.exceptions import HTTPError

        if not self.ok:
            raise HTTPError(f"HTTP Error {self.status_code}: {self.text()}", response=self)
