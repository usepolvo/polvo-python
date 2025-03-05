# core/rate_limiters/base.py
import time
from collections import deque
from threading import Lock
from typing import Dict


class BaseRateLimiter:
    """Base rate limiter with core functionality."""

    def __init__(self):
        self.windows: Dict[str, deque] = {}
        self.lock = Lock()

    def wait_if_needed(self):
        """Implement rate limiting logic."""
        raise NotImplementedError("Subclasses must implement wait_if_needed")

    def _initialize_window(self, window_name: str):
        """Initialize a new rate limit window."""
        if window_name not in self.windows:
            self.windows[window_name] = deque()

    def _clean_old_requests(self, window_name: str, current_time: float, time_frame: float):
        """Remove expired requests from window."""
        cutoff = current_time - time_frame
        while self.windows[window_name] and self.windows[window_name][0] <= cutoff:
            self.windows[window_name].popleft()

    def _wait_if_window_full(self, window_name: str, limit: int, time_frame: float) -> float:
        """Wait if request limit is reached."""
        current_time = time.time()
        self._clean_old_requests(window_name, current_time, time_frame)

        if len(self.windows[window_name]) >= limit:
            sleep_time = time_frame - (current_time - self.windows[window_name][0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            current_time = time.time()
            self._clean_old_requests(window_name, current_time, time_frame)

        self.windows[window_name].append(current_time)
        return current_time
