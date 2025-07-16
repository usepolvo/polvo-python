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
        session = polvo.Session("https://api.example.com", rate_limit=rate_limiter)
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
        session = polvo.Session("https://api.example.com", rate_limit=rate_limiter)
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

def for_apis(requests_per_second: float = 5.0) -> AdaptiveRateLimiter:
    """
    Create a rate limiter optimized for API calls.
    
    Uses adaptive rate limiting with reasonable defaults for most APIs.
    
    Args:
        requests_per_second: Initial requests per second
        
    Returns:
        AdaptiveRateLimiter instance
        
    Example:
        rate_limiter = polvo.rate_limit.for_apis()
        session = polvo.Session("https://api.example.com", rate_limit=rate_limiter)
    """
    return AdaptiveRateLimiter(requests_per_second)

# Aliases for common use cases
def github() -> AdaptiveRateLimiter:
    """Rate limiter tuned for GitHub API (5000 requests/hour)."""
    return AdaptiveRateLimiter(initial_requests_per_second=1.3)  # ~5000/hour

def twitter() -> AdaptiveRateLimiter:
    """Rate limiter tuned for Twitter API (300 requests/15min window)."""
    return AdaptiveRateLimiter(initial_requests_per_second=0.3)  # ~300/15min

__all__ = [
    "RateLimiter",
    "AdaptiveRateLimiter",
    "fixed",
    "adaptive",
    "conservative",
    "for_apis",
    "github",
    "twitter"
] 