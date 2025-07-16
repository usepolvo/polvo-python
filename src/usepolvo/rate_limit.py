"""
Rate limiting module with convenient functions for common rate limit patterns.
"""

from .resilience import RateLimiter, AdaptiveRateLimiter

def fixed(requests_per_second: float, burst_size: int = None) -> RateLimiter:
    """
    Create a fixed rate limiter.
    
    Args:
        requests_per_second: Maximum requests per second
        burst_size: Maximum burst size (defaults to requests_per_second)
        
    Returns:
        RateLimiter instance
        
    Example:
        rate_limiter = polvo.rate_limit.fixed(requests_per_second=10)
        api = polvo.API("https://api.example.com", rate_limit=rate_limiter)
    """
    return RateLimiter(requests_per_second, burst_size)

def adaptive(initial_requests_per_second: float = 10.0) -> AdaptiveRateLimiter:
    """
    Create an adaptive rate limiter that adjusts based on API response headers.
    
    This automatically reads rate limit headers from API responses and
    adjusts the rate limit accordingly to avoid hitting limits.
    
    Args:
        initial_requests_per_second: Initial rate limit
        
    Returns:
        AdaptiveRateLimiter instance
        
    Example:
        rate_limiter = polvo.rate_limit.adaptive(initial_requests_per_second=5)
        api = polvo.API("https://api.example.com", rate_limit=rate_limiter)
    """
    return AdaptiveRateLimiter(initial_requests_per_second)

def conservative(requests_per_second: float = 1.0) -> RateLimiter:
    """
    Create a conservative rate limiter for APIs with strict limits.
    
    Args:
        requests_per_second: Maximum requests per second (default: 1)
        
    Returns:
        RateLimiter instance
    """
    return RateLimiter(requests_per_second, burst_size=1)

def burst(requests_per_second: float, burst_size: int) -> RateLimiter:
    """
    Create a rate limiter optimized for bursty traffic.
    
    Args:
        requests_per_second: Sustained requests per second
        burst_size: Maximum burst size
        
    Returns:
        RateLimiter instance
    """
    return RateLimiter(requests_per_second, burst_size)

__all__ = [
    "RateLimiter",
    "AdaptiveRateLimiter",
    "fixed",
    "adaptive",
    "conservative",
    "burst"
] 