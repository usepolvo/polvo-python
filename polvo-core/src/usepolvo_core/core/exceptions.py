"""
Exception classes for Polvo.
"""

from typing import Optional

from usepolvo_core.core.response import Response


class PolvoError(Exception):
    """Base exception for all Polvo errors."""

    pass


class TransportError(PolvoError):
    """Error during HTTP transport."""

    pass


class TimeoutError(TransportError):
    """Request timed out."""

    pass


class HTTPError(PolvoError):
    """HTTP error response."""

    def __init__(self, message: str, response: Optional[Response] = None):
        """
        Initialize an HTTPError.

        Args:
            message: Error message
            response: Response that caused the error
        """
        super().__init__(message)
        self.response = response

    @property
    def status_code(self) -> Optional[int]:
        """Return the status code of the response, if available."""
        return self.response.status_code if self.response else None


class SchemaValidationError(PolvoError):
    """Error validating response against schema."""

    pass
