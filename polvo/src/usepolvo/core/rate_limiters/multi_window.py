# core/rate_limiters/multi_window.py
from typing import Optional

from usepolvo.core.rate_limiters.base import BaseRateLimiter


class MultiWindowRateLimiter(BaseRateLimiter):
    """Rate limiter with multiple time windows (e.g., per-second and per-minute limits)."""

    def __init__(
        self,
        requests_per_second: int = 10,
        requests_per_minute: int = 100,
        requests_per_hour: Optional[int] = None,
    ):
        super().__init__()
        self.limits = {
            "second": (requests_per_second, 1),
            "minute": (requests_per_minute, 60),
        }
        if requests_per_hour:
            self.limits["hour"] = (requests_per_hour, 3600)

        for window in self.limits:
            self._initialize_window(window)

    def wait_if_needed(self):
        with self.lock:
            for window, (limit, time_frame) in self.limits.items():
                self._wait_if_window_full(window, limit, time_frame)
