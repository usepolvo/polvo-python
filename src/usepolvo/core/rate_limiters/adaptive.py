# core/rate_limiters/adaptive.py
from typing import Dict

from usepolvo.core.rate_limiters.base import BaseRateLimiter


class AdaptiveRateLimiter(BaseRateLimiter):
    """Rate limiter that adapts to API response headers."""

    def __init__(self, initial_limit: int = 10):
        super().__init__()
        self.current_limit = initial_limit
        self._initialize_window("default")

    def wait_if_needed(self):
        with self.lock:
            self._wait_if_window_full("default", self.current_limit, 1)

    def update_limits(self, response_headers: Dict[str, str]):
        """Update rate limits based on API response headers."""
        if "X-RateLimit-Remaining" in response_headers:
            remaining = int(response_headers["X-RateLimit-Remaining"])
            self.current_limit = max(1, remaining)
