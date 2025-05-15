"""
Rate limiting middleware using token bucket algorithm.
"""

import time
from typing import Any, Dict, Optional

from usepolvo_core.core.response import Response
from usepolvo_core.middleware.base import Middleware


class RateLimiterMiddleware(Middleware):
    """Rate limiting middleware using token bucket algorithm."""

    def __init__(self, calls: int = 10, period: float = 1.0):
        """
        Initialize RateLimiterMiddleware.

        Args:
            calls: Number of allowed calls per period
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self.tokens = calls
        self.last_check = time.time()

    def pre_request(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement rate limiting before request is sent.

        Args:
            request_kwargs: Request parameters

        Returns:
            Modified request parameters
        """
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current

        # Add tokens for time passed
        self.tokens = min(self.calls, self.tokens + time_passed * (self.calls / self.period))

        # If we have less than 1 token, we need to wait
        if self.tokens < 1:
            # Calculate sleep time
            sleep_time = (1 - self.tokens) * self.period / self.calls
            time.sleep(sleep_time)
            self.tokens = 1

        # Consume a token
        self.tokens -= 1

        return request_kwargs

    def post_request(self, response: Response) -> Response:
        """
        Check for rate limit headers and adjust accordingly.

        Args:
            response: Response object

        Returns:
            Modified response
        """
        # Some APIs provide rate limit information in headers
        # We could adjust our rate limiting based on this information
        # For example:
        # - X-RateLimit-Limit
        # - X-RateLimit-Remaining
        # - X-RateLimit-Reset

        return response
