# tentacles/openai/client.py

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import openai
from openai import OpenAI as OpenAIClient

from usepolvo.core.auth.api_key import APIKeyAuth
from usepolvo.core.clients.rest import RESTClient
from usepolvo.core.rate_limiters.adaptive import AdaptiveRateLimiter
from usepolvo.tentacles.openai.chat import ChatCompletions
from usepolvo.tentacles.openai.config import get_settings
from usepolvo.tentacles.openai.embeddings import Embeddings


class OpenAITentacle(RESTClient):
    """
    OpenAI client that leverages the official SDK.
    Handles authentication and rate limiting.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        organization_id: Optional[str] = None,
        api_base: Optional[str] = None,
        default_model: Optional[str] = None,
        rate_limit_rpm: Optional[int] = None,
        rate_limit_tpm: Optional[int] = None,
    ):
        """
        Initialize OpenAI client using the official SDK.

        Environment variables (prefixed with POLVO_):
            OPENAI_API_KEY: Your OpenAI API key
            OPENAI_ORGANIZATION_ID: Optional organization ID
            OPENAI_API_BASE: API base URL
            OPENAI_DEFAULT_MODEL: Default model to use
            OPENAI_RATE_LIMIT_RPM: Requests per minute rate limit
            OPENAI_RATE_LIMIT_TPM: Tokens per minute rate limit

        Args:
            api_key: OpenAI API key (overrides env var)
            organization_id: Optional organization ID (overrides env var)
            api_base: Optional API base URL (overrides env var)
            default_model: Default model to use (overrides env var)
            rate_limit_rpm: Optional requests per minute rate limit (overrides env var)
            rate_limit_tpm: Optional tokens per minute rate limit (overrides env var)
        """
        super().__init__()

        # Load settings from environment
        self.settings = get_settings()

        # Use provided values or fall back to environment variables
        self._api_key = api_key or self.settings.OPENAI_API_KEY
        self._organization_id = organization_id or self.settings.OPENAI_ORGANIZATION_ID
        self.default_model = default_model or self.settings.OPENAI_DEFAULT_MODEL

        if not self._api_key:
            raise ValueError(
                "Must provide API key via constructor argument or environment variable"
            )

        # # Set up rate limiting
        # rpm = rate_limit_rpm or self.settings.OPENAI_RATE_LIMIT_RPM
        # tpm = rate_limit_tpm or self.settings.OPENAI_RATE_LIMIT_TPM
        # self.rate_limiter = AdaptiveRateLimiter(
        #     requests_per_minute=rpm,
        #     resource_per_minute=tpm,
        #     resource_field="tokens"
        # )

        # Initialize the OpenAI client
        self.client = OpenAIClient(
            api_key=self._api_key,
            organization=self._organization_id,
        )

        # Initialize API resources
        self._chat = ChatCompletions(self)
        self._embeddings = Embeddings(self)

    @property
    def chat(self) -> ChatCompletions:
        """Access the Chat Completions API."""
        return self._chat

    @property
    def embeddings(self) -> Embeddings:
        """Access the Embeddings API."""
        return self._embeddings

    def _estimate_tokens(self, messages: List[Dict[str, str]], max_tokens: int) -> int:
        """Estimate the number of tokens used in a request and response."""
        # Simple token estimation - can be improved with tiktoken
        prompt_tokens = sum(len(m.get("content", "")) for m in messages) // 4
        return prompt_tokens + max_tokens
