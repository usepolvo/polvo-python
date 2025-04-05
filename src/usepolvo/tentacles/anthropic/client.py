# tentacles/anthropic/client.py

from typing import Any, Dict, List, Optional, Union

from anthropic import Anthropic as AnthropicClient

from usepolvo.core.auth.api_key import APIKeyAuth
from usepolvo.core.clients.rest import RESTClient
from usepolvo.core.rate_limiters.adaptive import AdaptiveRateLimiter
from usepolvo.tentacles.anthropic.config import get_settings
from usepolvo.tentacles.anthropic.messages import Messages


class AnthropicTentacle(RESTClient):
    """
    Anthropic client that leverages the official SDK.
    Handles authentication and rate limiting.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        """
        Initialize Anthropic client using the official SDK.

        Environment variables (prefixed with POLVO_):
            ANTHROPIC_API_KEY: Your Anthropic API key
            ANTHROPIC_API_BASE: API base URL
            ANTHROPIC_DEFAULT_MODEL: Default model to use (e.g. claude-3-opus-20240229)

        Args:
            api_key: Anthropic API key (overrides env var)
            api_base: Optional API base URL (overrides env var)
            default_model: Default model to use (overrides env var)
        """
        super().__init__()

        # Load settings from environment
        self.settings = get_settings()

        # Use provided values or fall back to environment variables
        self._api_key = api_key or self.settings.ANTHROPIC_API_KEY
        self.default_model = default_model or self.settings.ANTHROPIC_DEFAULT_MODEL

        if not self._api_key:
            raise ValueError(
                "Must provide API key via constructor argument or environment variable"
            )

        # # Set up rate limiting
        # rpm = rate_limit_rpm or self.settings.ANTHROPIC_RATE_LIMIT_RPM
        # tpm = rate_limit_tpm or self.settings.ANTHROPIC_RATE_LIMIT_TPM
        # self.rate_limiter = AdaptiveRateLimiter(
        #     requests_per_minute=rpm,
        #     resource_per_minute=tpm,
        #     resource_field="tokens"
        # )

        # Initialize the Anthropic client
        self.client = AnthropicClient(api_key=self._api_key)

        # Initialize API resources
        self._messages = Messages(self)

    @property
    def messages(self) -> Messages:
        """Access the Messages API."""
        return self._messages

    def _estimate_tokens(self, messages: List[Dict[str, Any]], max_tokens: int) -> int:
        """Estimate the number of tokens used in a request and response."""
        # Simple token estimation - can be improved with a proper tokenizer
        prompt_tokens = 0

        for message in messages:
            content = message.get("content", "")
            if isinstance(content, str):
                prompt_tokens += len(content) // 4
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        prompt_tokens += len(item["text"]) // 4

        return prompt_tokens + max_tokens

    def _response_to_dict(self, response: Any) -> Dict[str, Any]:
        """Convert Anthropic response object to dictionary."""
        if hasattr(response, "dict"):
            return response.dict()
        elif hasattr(response, "model_dump"):
            return response.model_dump()
        elif isinstance(response, dict):
            return response
        else:
            # Basic conversion for other response types
            result = {}

            # Extract common fields
            if hasattr(response, "id"):
                result["id"] = response.id
            if hasattr(response, "model"):
                result["model"] = response.model
            if hasattr(response, "content"):
                if isinstance(response.content, list):
                    result["content"] = [
                        {key: getattr(c, key) for key in dir(c) if not key.startswith("_")}
                        for c in response.content
                    ]
                else:
                    result["content"] = response.content

            return result
