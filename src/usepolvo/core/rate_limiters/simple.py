# core/rate_limiters/simple.py
from usepolvo.core.rate_limiters.base import BaseRateLimiter


class SimpleRateLimiter(BaseRateLimiter):
    """Simple rate limiter with single time window."""

    def __init__(self, requests_per_second: int = 10):
        super().__init__()
        self.requests_per_second = requests_per_second
        self._initialize_window("default")

    def wait_if_needed(self):
        with self.lock:
            self._wait_if_window_full("default", self.requests_per_second, 1)
