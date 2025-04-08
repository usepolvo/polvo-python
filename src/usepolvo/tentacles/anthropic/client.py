# tentacles/anthropic/client.py

from typing import Any, Dict, List, Optional, Union

from anthropic import Anthropic as AnthropicClient

from usepolvo.core.auth.api_key import APIKeyAuth
from usepolvo.core.clients.rest import RESTClient
from usepolvo.core.rate_limiters.adaptive import AdaptiveRateLimiter
from usepolvo.tentacles.anthropic.config import get_settings
from usepolvo.tentacles.anthropic.messages import Messages
from usepolvo.tentacles.base import BaseTentacle


class AnthropicTentacle(RESTClient, BaseTentacle):
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

    def generate(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = 1024,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a response using Anthropic's Claude model.

        Implementation of the BaseTentacle.generate method using Anthropic's API.

        Args:
            messages: List of message objects
            model: Model to use, defaults to instance default_model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: System instructions for Claude
            tools: Tool definitions for function calling
            tool_choice: Specify which tool to use
            **kwargs: Additional parameters passed to Anthropic's API

        Returns:
            Standardized response dictionary
        """
        # Pass all parameters to the Messages.create method
        params = {
            "messages": messages,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_message,  # Anthropic uses 'system' param
            "tools": tools,
            "tool_choice": tool_choice,
        }

        # Add any additional kwargs
        params.update({k: v for k, v in kwargs.items() if v is not None})

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        return self.messages.create(**params)

    def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = 1024,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None,
        **kwargs,
    ):
        """
        Generate a streaming response using Anthropic's Claude model.

        Implementation of the BaseTentacle.generate_stream method.

        Args:
            messages: List of message objects
            model: Model to use, defaults to instance default_model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: System instructions for Claude
            **kwargs: Additional parameters

        Returns:
            A stream of response chunks
        """
        return self.messages.with_streaming(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,  # Anthropic uses 'system' param
        )
