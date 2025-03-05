# core/rate_limiters/bucketed.py
import time

from usepolvo.core.rate_limiters.base import BaseRateLimiter


class BucketedRateLimiter(BaseRateLimiter):
    """Token bucket rate limiter."""

    def __init__(self, bucket_size: int = 100, refill_rate: int = 10):
        super().__init__()
        self.bucket_size = bucket_size
        self.refill_rate = refill_rate
        self.tokens = bucket_size
        self.last_refill = time.time()

    def wait_if_needed(self):
        with self.lock:
            self._refill_tokens()
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.refill_rate
                time.sleep(sleep_time)
                self._refill_tokens()
            self.tokens -= 1

    def _refill_tokens(self):
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.bucket_size, self.tokens + new_tokens)
        self.last_refill = now
