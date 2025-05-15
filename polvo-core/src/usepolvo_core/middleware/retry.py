"""
Retry middleware with exponential backoff.
"""

from typing import Any, Dict, List, Optional

from usepolvo_core.middleware.base import Middleware


class RetryMiddleware(Middleware):
    """Retry middleware with exponential backoff."""

    def __init__(
        self,
        retries: int = 3,
        retry_status_codes: Optional[List[int]] = None,
        backoff_factor: float = 0.3,
    ):
        """
        Initialize RetryMiddleware.

        Args:
            retries: Maximum number of retries
            retry_status_codes: Status codes to retry on
            backoff_factor: Backoff factor for exponential backoff
        """
        self.retries = retries
        self.retry_status_codes = retry_status_codes or [429, 500, 502, 503, 504]
        self.backoff_factor = backoff_factor

    def pre_request(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add retry configuration to request.

        Args:
            request_kwargs: Request parameters

        Returns:
            Modified request parameters
        """
        # Use a special key that won't be passed to httpx
        request_kwargs["_retry_config"] = {
            "count": self.retries,
            "status_codes": self.retry_status_codes,
            "backoff_factor": self.backoff_factor,
        }

        return request_kwargs
