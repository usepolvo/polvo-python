# tentacles/openai/embeddings.py

from typing import Any, Dict, List, Optional, Union

import openai


class Embeddings:
    """
    Handles interactions with OpenAI's Embeddings API.
    https://platform.openai.com/docs/api-reference/embeddings
    """

    def __init__(self, client):
        """
        Initialize the Embeddings resource.

        Args:
            client: The OpenAITentacle client instance
        """
        self.client = client

    def create(
        self,
        input: Union[str, List[str]],
        model: Optional[str] = None,
        encoding_format: Optional[str] = None,
        dimensions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create embeddings for the input text.

        Args:
            input: Input text to embed, can be a string or array of strings
            model: Model to use, defaults to "text-embedding-ada-002"
            encoding_format: Specifies encoding format, e.g., "float" or "base64"
            dimensions: Number of dimensions the resulting output embeddings should have
            user: Optional end-user ID for tracking and rate limiting

        Returns:
            Complete API response with embeddings
        """
        # Apply rate limiting - simple character-based estimation
        if isinstance(input, str):
            token_estimate = len(input) // 4
        else:
            token_estimate = sum(len(text) for text in input) // 4

        # self.client.rate_limiter.acquire(resource_amount=token_estimate)

        try:
            embedding_model = model or "text-embedding-ada-002"

            response = self.client.client.embeddings.create(
                model=embedding_model,
                input=input,
                encoding_format=encoding_format,
                dimensions=dimensions,
                user=user,
            )
            return response.model_dump()
        except openai.RateLimitError:
            # Adjust rate limiter on hitting limits
            self.client.rate_limiter.backoff()
            raise
