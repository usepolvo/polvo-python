# tentacles/anthropic/messages.py

from typing import TYPE_CHECKING, Any, Dict, List, Optional

import anthropic

# Conditional import only used during type checking
if TYPE_CHECKING:
    from usepolvo.tentacles.anthropic.client import AnthropicTentacle


class Messages:
    """
    Handles interactions with Anthropic's Messages API.
    https://docs.anthropic.com/en/api/messages
    """

    def __init__(self, client: "AnthropicTentacle"):
        """
        Initialize the Messages resource.

        Args:
            client: The AnthropicTentacle client instance
        """
        self.client = client

    def create(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None,
        stop_sequences: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a message using Anthropic's Messages API.

        Args:
            messages: List of message objects
            model: Model to use, defaults to instance default_model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            system: System prompt to control Claude's behavior
            tools: Tool definitions for function calling
            tool_choice: Specify which tool to use
            stop_sequences: Custom stop sequences
            metadata: Additional metadata

        Returns:
            Complete API response
        """
        # Apply rate limiting
        estimated_tokens = self.client._estimate_tokens(messages, max_tokens)
        # self.client.rate_limiter.acquire(resource_amount=estimated_tokens)

        try:
            # Prepare request parameters
            params = {
                "model": model or self.client.default_model,
                "messages": messages,
                "max_tokens": max_tokens,
            }

            # Add optional parameters
            if temperature is not None:
                params["temperature"] = temperature
            if top_p is not None:
                params["top_p"] = top_p
            if top_k is not None:
                params["top_k"] = top_k
            if system is not None:
                params["system"] = system
            if tools is not None:
                params["tools"] = tools
            if tool_choice is not None:
                params["tool_choice"] = tool_choice
            if stop_sequences is not None:
                params["stop_sequences"] = stop_sequences
            if metadata is not None:
                params["metadata"] = metadata

            # Make the API request
            response = self.client.client.messages.create(**params)

            # Convert to dictionary
            return self.client._response_to_dict(response)

        except anthropic.RateLimitError:
            # Adjust rate limiter on hitting limits
            self.client.rate_limiter.backoff()
            raise

    def with_streaming(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: Optional[float] = None,
        system: Optional[str] = None,
    ):
        """
        Create a streaming message response.

        Args:
            messages: List of message objects
            model: Model to use, defaults to instance default_model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            system: System prompt to control Claude's behavior

        Returns:
            A stream of response chunks
        """
        # Apply rate limiting
        estimated_tokens = self.client._estimate_tokens(messages, max_tokens)
        # self.client.rate_limiter.acquire(resource_amount=estimated_tokens)

        # Prepare request parameters
        params = {
            "model": model or self.client.default_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": True,
        }

        # Add optional parameters
        if temperature is not None:
            params["temperature"] = temperature
        if system is not None:
            params["system"] = system

        return self.client.client.messages.create(**params)
