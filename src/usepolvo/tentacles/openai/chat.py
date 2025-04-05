# tentacles/openai/chat.py

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import openai

# Conditional import only used during type checking
if TYPE_CHECKING:
    from usepolvo.tentacles.openai.client import OpenAITentacle


class ChatCompletions:
    """
    Handles interactions with OpenAI's Chat Completions API.
    https://platform.openai.com/docs/api-reference/chat/create
    """

    def __init__(self, client: "OpenAITentacle"):
        """
        Initialize the Chat Completions resource.

        Args:
            client: The OpenAITentacle client instance
        """
        self.client = client

    def create(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, str]]] = None,
        response_format: Optional[Dict[str, str]] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a chat completion using OpenAI's chat API.

        Args:
            messages: List of message objects
            model: Model to use, defaults to instance default_model
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            stop: Stop sequences
            tools: Tool definitions
            tool_choice: Tool choice strategy
            response_format: Response format
            seed: Random seed for deterministic results

        Returns:
            Complete API response
        """
        # Apply rate limiting
        estimated_tokens = self.client._estimate_tokens(messages, max_tokens or 1000)
        # self.client.rate_limiter.acquire(resource_amount=estimated_tokens)

        try:
            response = self.client.client.chat.completions.create(
                model=model or self.client.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                tools=tools,
                tool_choice=tool_choice,
                response_format=response_format,
                seed=seed,
            )
            return response.model_dump()
        except openai.RateLimitError:
            # Adjust rate limiter on hitting limits
            self.client.rate_limiter.backoff()
            raise

    def with_streaming(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """
        Create a streaming chat completion.

        Args:
            messages: List of message objects
            model: Model to use, defaults to instance default_model
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            A stream of response chunks
        """
        # Apply rate limiting
        estimated_tokens = self.client._estimate_tokens(messages, max_tokens or 1000)
        self.client.rate_limiter.acquire(resource_amount=estimated_tokens)

        return self.client.client.chat.completions.create(
            model=model or self.client.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
