"""
Resilience patterns for production-ready API clients.

Provides retry with exponential backoff and rate limiting
to handle real-world API integration challenges.
"""

import time
import random
import threading
from typing import Callable, Any, Optional, Dict
import httpx


class RetryStrategy:
    """
    Exponential backoff retry strategy with jitter.
    
    Handles transient failures gracefully with configurable retry logic.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry strategy.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to prevent thundering herd
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def execute(self, func: Callable[[], Any]) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            
        Returns:
            Result of the function
            
        Raises:
            Exception: If all retries are exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func()
            except Exception as e:
                last_exception = e
                
                # Don't retry on the last attempt
                if attempt == self.max_retries:
                    break
                
                # Check if this is a retryable error
                if not self._is_retryable(e):
                    break
                
                # Calculate delay
                delay = self._calculate_delay(attempt)
                time.sleep(delay)
        
        # All retries exhausted
        raise last_exception
    
    def _is_retryable(self, exception: Exception) -> bool:
        """Check if an exception is retryable."""
        # Retry on network errors and 5xx HTTP errors
        if isinstance(exception, (
            httpx.NetworkError,
            httpx.TimeoutException,
            httpx.ConnectError
        )):
            return True
        
        if isinstance(exception, httpx.HTTPStatusError):
            # Retry on 5xx server errors and 429 rate limit
            return exception.response.status_code >= 500 or exception.response.status_code == 429
        
        return False
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add random jitter (±25%)
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)


class RateLimiter:
    """
    Token bucket rate limiter.
    
    Prevents overwhelming APIs with too many requests.
    """
    
    def __init__(self, requests_per_second: float, burst_size: Optional[int] = None):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum requests per second
            burst_size: Maximum burst size (defaults to requests_per_second)
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size or int(requests_per_second)
        
        self._tokens = float(self.burst_size)
        self._last_update = time.time()
        self._lock = threading.Lock()
    
    def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, blocking if necessary.
        
        Args:
            tokens: Number of tokens to acquire
        """
        with self._lock:
            now = time.time()
            
            # Add tokens based on time elapsed
            elapsed = now - self._last_update
            self._tokens = min(
                self.burst_size,
                self._tokens + (elapsed * self.requests_per_second)
            )
            self._last_update = now
            
            # If we don't have enough tokens, wait
            if self._tokens < tokens:
                wait_time = (tokens - self._tokens) / self.requests_per_second
                time.sleep(wait_time)
                self._tokens = 0
            else:
                self._tokens -= tokens


class AdaptiveRateLimiter(RateLimiter):
    """
    Adaptive rate limiter that adjusts based on API response headers.
    
    Reads rate limit information from common API headers and adjusts accordingly.
    """
    
    def __init__(self, initial_requests_per_second: float = 10.0):
        """
        Initialize adaptive rate limiter.
        
        Args:
            initial_requests_per_second: Initial rate limit
        """
        super().__init__(initial_requests_per_second)
        self.initial_rate = initial_requests_per_second
    
    def update_from_response(self, response: httpx.Response) -> None:
        """
        Update rate limits based on response headers.
        
        Args:
            response: HTTP response to analyze
        """
        headers = response.headers
        
        # Common rate limit headers
        remaining = None
        reset_time = None
        
        # GitHub style
        if 'x-ratelimit-remaining' in headers and 'x-ratelimit-reset' in headers:
            remaining = int(headers['x-ratelimit-remaining'])
            reset_time = int(headers['x-ratelimit-reset'])
        
        # Twitter style
        elif 'x-rate-limit-remaining' in headers and 'x-rate-limit-reset' in headers:
            remaining = int(headers['x-rate-limit-remaining'])
            reset_time = int(headers['x-rate-limit-reset'])
        
        # Update rate if we have the information
        if remaining is not None and reset_time is not None:
            now = time.time()
            time_until_reset = reset_time - now
            
            if time_until_reset > 0:
                # Calculate safe rate (with 10% buffer)
                safe_rate = (remaining * 0.9) / time_until_reset
                
                with self._lock:
                    self.requests_per_second = max(0.1, safe_rate)


 