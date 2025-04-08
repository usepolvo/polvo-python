from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import openai

# Conditional import only used during type checking
if TYPE_CHECKING:
    from usepolvo.tentacles.openai.client import OpenAITentacle


class Responses:
    """
    Handles interactions with OpenAI's Responses API.
    https://platform.openai.com/docs/api-reference/responses/create
    """

    def __init__(self, client: "OpenAITentacle"):
        """
        Initialize the Responses resource.

        Args:
            client: The OpenAITentacle client instance
        """
        self.client = client

    def create(
        self,
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        input: Optional[str] = None,
        temperature: Optional[float] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        max_tokens: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a response using OpenAI's responses API.

        Args:
            model: Model to use, defaults to instance default_model
            tools: List of tools to use in the response
            input: Input text for the response
            temperature: Sampling temperature (0-2)
            tool_choice: Tool choice strategy
            max_tokens: Maximum tokens to generate
            seed: Random seed for deterministic results

        Returns:
            Complete API response
        """
        # Apply rate limiting
        estimated_tokens = self.client._estimate_tokens(
            [{"content": input}] if input else [], max_tokens or 1000
        )
        # self.client.rate_limiter.acquire(resource_amount=estimated_tokens)

        try:
            response = self.client.client.responses.create(
                model=model or self.client.default_model,
                tools=tools,
                input=input,
                temperature=temperature,
                tool_choice=tool_choice,
                max_tokens=max_tokens,
                seed=seed,
            )
            return response.model_dump()
        except openai.RateLimitError:
            # Adjust rate limiter on hitting limits
            self.client.rate_limiter.backoff()
            raise

    def with_streaming(
        self,
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        input: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Create a streaming response.

        Args:
            model: Model to use, defaults to instance default_model
            tools: List of tools to use in the response
            input: Input text for the response
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            A stream of response chunks
        """
        # Apply rate limiting
        estimated_tokens = self.client._estimate_tokens(
            [{"content": input}] if input else [], max_tokens or 1000
        )
        # self.client.rate_limiter.acquire(resource_amount=estimated_tokens)

        return self.client.client.responses.create(
            model=model or self.client.default_model,
            tools=tools,
            input=input,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
