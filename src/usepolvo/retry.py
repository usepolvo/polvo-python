"""
Retry module with convenient functions for common retry patterns.
"""

from .resilience import RetryStrategy

def exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> RetryStrategy:
    """
    Create an exponential backoff retry strategy.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter
        
    Returns:
        RetryStrategy instance
        
    Example:
        retry_strategy = polvo.retry.exponential_backoff(max_retries=5)
        api = polvo.API("https://api.example.com", retry=retry_strategy)
    """
    return RetryStrategy(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        jitter=jitter
    )

def linear_backoff(
    max_retries: int = 3,
    delay: float = 1.0,
    jitter: bool = True
) -> RetryStrategy:
    """
    Create a linear backoff retry strategy.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Fixed delay between retries
        jitter: Whether to add random jitter
        
    Returns:
        RetryStrategy instance
    """
    return RetryStrategy(
        max_retries=max_retries,
        base_delay=delay,
        max_delay=delay,
        exponential_base=1.0,  # No exponential growth
        jitter=jitter
    )

def immediate(max_retries: int = 3) -> RetryStrategy:
    """
    Create an immediate retry strategy (no delay).
    
    Args:
        max_retries: Maximum number of retry attempts
        
    Returns:
        RetryStrategy instance
    """
    return RetryStrategy(
        max_retries=max_retries,
        base_delay=0.0,
        max_delay=0.0,
        jitter=False
    )

__all__ = [
    "RetryStrategy",
    "exponential_backoff",
    "linear_backoff", 
    "immediate"
] 