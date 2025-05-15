"""
Base class for middleware.
"""

from typing import Any, Dict

from usepolvo_core.core.response import Response


class Middleware:
    """Base class for middleware."""

    def pre_request(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify request parameters before sending.

        Args:
            request_kwargs: Request parameters

        Returns:
            Modified request parameters
        """
        return request_kwargs

    def post_request(self, response: Response) -> Response:
        """
        Process response after receiving.

        Args:
            response: Response object

        Returns:
            Modified response
        """
        return response
