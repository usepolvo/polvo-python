"""
Logging middleware for request and response logging.
"""

import logging
from typing import Any, Dict, Optional

from usepolvo_core.core.response import Response
from usepolvo_core.middleware.base import Middleware


class LoggingMiddleware(Middleware):
    """Middleware for logging requests and responses."""

    def __init__(self, logger: Optional[logging.Logger] = None, level: int = logging.INFO):
        """
        Initialize LoggingMiddleware.

        Args:
            logger: Logger to use (defaults to a logger named 'polvo')
            level: Logging level
        """
        self.logger = logger or logging.getLogger("polvo")
        self.level = level

    def pre_request(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log request before sending.

        Args:
            request_kwargs: Request parameters

        Returns:
            Modified request parameters
        """
        method = request_kwargs.get("method", "GET")
        url = request_kwargs.get("url", "")

        self.logger.log(
            self.level,
            f"Request: {method} {url}",
            extra={
                "request": {
                    "method": method,
                    "url": url,
                    "headers": request_kwargs.get("headers", {}),
                    "params": request_kwargs.get("params", {}),
                }
            },
        )

        return request_kwargs

    def post_request(self, response: Response) -> Response:
        """
        Log response after receiving.

        Args:
            response: Response object

        Returns:
            Modified response
        """
        self.logger.log(
            self.level,
            f"Response: {response.status_code} from {response.url}",
            extra={
                "response": {
                    "status_code": response.status_code,
                    "url": response.url,
                    "headers": response.headers,
                    "elapsed": response.elapsed,
                }
            },
        )

        return response
