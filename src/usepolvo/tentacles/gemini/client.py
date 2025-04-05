# tentacles/gemini/client.py

from typing import Any, Dict, List, Optional, Union

from google import genai
from google.genai import types

from usepolvo.core.auth.api_key import APIKeyAuth
from usepolvo.core.clients.rest import RESTClient
from usepolvo.core.rate_limiters.adaptive import AdaptiveRateLimiter
from usepolvo.tentacles.gemini.config import get_settings
from usepolvo.tentacles.gemini.embeddings import Embeddings
from usepolvo.tentacles.gemini.generation import Generation


class GeminiTentacle(RESTClient):
    """
    Google Gemini client that leverages the official SDK.
    Handles authentication and rate limiting.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        default_model: Optional[str] = None,
        rate_limit_qpm: Optional[int] = None,
        rate_limit_tpm: Optional[int] = None,
    ):
        """
        Initialize Gemini client using the official SDK.

        Environment variables (prefixed with POLVO_):
            GEMINI_API_KEY: Your Google API key
            GEMINI_API_BASE: API base URL
            GEMINI_DEFAULT_MODEL: Default model to use
            GEMINI_RATE_LIMIT_QPM: Queries per minute rate limit
            GEMINI_RATE_LIMIT_TPM: Tokens per minute rate limit

        Args:
            api_key: Google API key (overrides env var)
            api_base: Optional API base URL (overrides env var)
            default_model: Default model to use (overrides env var)
            rate_limit_qpm: Optional queries per minute rate limit (overrides env var)
            rate_limit_tpm: Optional tokens per minute rate limit (overrides env var)
        """
        super().__init__()

        # Load settings from environment
        self.settings = get_settings()

        # Use provided values or fall back to environment variables
        self._api_key = api_key or self.settings.GEMINI_API_KEY
        self.default_model = default_model or self.settings.GEMINI_DEFAULT_MODEL

        if not self._api_key:
            raise ValueError(
                "Must provide API key via constructor argument or environment variable"
            )

        # # Set up rate limiting
        # qpm = rate_limit_qpm or self.settings.GEMINI_RATE_LIMIT_QPM
        # tpm = rate_limit_tpm or self.settings.GEMINI_RATE_LIMIT_TPM
        # self.rate_limiter = AdaptiveRateLimiter(
        #     requests_per_minute=qpm,
        #     resource_per_minute=tpm,
        #     resource_field="tokens"
        # )

        # Initialize the Gemini client
        self.client = genai.Client(api_key=self._api_key)

        # Initialize API resources
        self._generation = Generation(self)
        self._embeddings = Embeddings(self)

    @property
    def generation(self) -> Generation:
        """Access the Generation API."""
        return self._generation

    @property
    def embeddings(self) -> Embeddings:
        """Access the Embeddings API."""
        return self._embeddings

    def _estimate_tokens(self, contents: List[Dict[str, Any]]) -> int:
        """Estimate the number of tokens used in a request and response."""
        # Simple token estimation - can be improved with more accurate calculation
        text_content = ""
        for content in contents:
            for part in content.get("parts", []):
                if isinstance(part, dict) and "text" in part:
                    text_content += part["text"]
                elif isinstance(part, str):
                    text_content += part

        # Assuming 4 characters per token and response similar to request size
        token_estimate = len(text_content) // 4
        return token_estimate * 2  # Double for response estimation

    def _response_to_dict(self, response: Any) -> Dict[str, Any]:
        """Convert Gemini response object to dictionary."""
        if hasattr(response, "to_dict"):
            return response.to_dict()
        elif isinstance(response, dict):
            return response
        else:
            # Basic conversion
            result = {"candidates": []}

            # Extract content if available
            if hasattr(response, "candidates"):
                for candidate in response.candidates:
                    cand_dict = {"content": {"parts": []}}

                    if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                        for part in candidate.content.parts:
                            if hasattr(part, "text"):
                                cand_dict["content"]["parts"].append({"text": part.text})

                    result["candidates"].append(cand_dict)

            return result
