# tentacles/gemini/embeddings.py

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from google import genai
from google.genai import types

# Conditional import only used during type checking
if TYPE_CHECKING:
    from usepolvo.tentacles.gemini.client import GeminiTentacle


class Embeddings:
    """
    Handles interactions with Google Gemini's Embeddings API.
    https://ai.google.dev/gemini-api/docs/embeddings
    """

    def __init__(self, client: "GeminiTentacle"):
        """
        Initialize the Embeddings resource.

        Args:
            client: The GeminiTentacle client instance
        """
        self.client = client

    def batch_embed_contents(
        self,
        contents: Union[str, List[str]],
        model: Optional[str] = None,
        task_type: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create embeddings for the input text.

        Args:
            contents: Input text to embed, can be a string or array of strings
            model: Model to use, defaults to an embedding-specific model
            task_type: Type of task for the embedding (e.g., "RETRIEVAL_DOCUMENT")
            title: Optional title for the content

        Returns:
            Complete API response with embeddings
        """
        # Standardize input format
        if isinstance(contents, str):
            contents = [contents]

        # Apply rate limiting - simple character-based estimation
        token_estimate = sum(len(text) for text in contents) // 4
        # self.client.rate_limiter.acquire(resource_amount=token_estimate)

        try:
            # Use embedding-specific model
            embedding_model = model or "models/embedding-001"

            # Create embeddings
            response = self.client.client.models.embed_content(
                model=embedding_model,
                contents=contents,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    title=title,
                ),
            )

            # Convert to dictionary
            if hasattr(response, "to_dict"):
                return response.to_dict()
            else:
                # Basic conversion
                result = {"embeddings": []}

                if hasattr(response, "embeddings"):
                    for embedding in response.embeddings:
                        if hasattr(embedding, "values"):
                            result["embeddings"].append({"values": embedding.values})

                return result

        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                # Adjust rate limiter on hitting limits
                self.client.rate_limiter.backoff()
            raise
