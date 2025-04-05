# tentacles/gemini/generation.py

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from google import genai
from google.genai import types

# Conditional import only used during type checking
if TYPE_CHECKING:
    from usepolvo.tentacles.gemini.client import GeminiTentacle


class Generation:
    """
    Handles interactions with Google Gemini's Generation API.
    https://ai.google.dev/gemini-api/docs/text-generation
    """

    def __init__(self, client: "GeminiTentacle"):
        """
        Initialize the Generation resource.

        Args:
            client: The GeminiTentacle client instance
        """
        self.client = client

    def generate_content(
        self,
        contents: Union[str, List[Union[str, Dict[str, Any]]]],
        model: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        safety_settings: Optional[List[Dict[str, Any]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        system_instruction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate content using Gemini's generative API.

        Args:
            contents: Text or structured content to generate from
            model: Model to use, defaults to instance default_model
            generation_config: Generation configuration
            safety_settings: Safety settings
            tools: Tools configuration
            system_instruction: System instructions for the model

        Returns:
            Complete API response
        """
        # Apply rate limiting
        # estimated_tokens = self.client._estimate_tokens(contents)
        # self.client.rate_limiter.acquire(resource_amount=estimated_tokens)

        try:
            response = self.client.client.models.generate_content(
                model=model or self.client.default_model,
                config=types.GenerateContentConfig(system_instruction=system_instruction),
                contents=contents,
            )

            # Convert to dictionary
            return self.client._response_to_dict(response)
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                # Adjust rate limiter on hitting limits
                self.client.rate_limiter.backoff()
            raise

    def with_streaming(
        self,
        contents: Union[str, List[Union[str, Dict[str, Any]]]],
        model: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Generate streaming content using Gemini's generative API.

        Args:
            contents: Text or structured content to generate from
            model: Model to use, defaults to instance default_model
            generation_config: Generation configuration

        Returns:
            A stream of response chunks
        """
        # Standardize content format
        if isinstance(contents, str):
            contents = [{"role": "user", "parts": [{"text": contents}]}]
        elif isinstance(contents, list) and all(isinstance(item, str) for item in contents):
            contents = [{"role": "user", "parts": [{"text": text} for text in contents]}]

        # Apply rate limiting
        estimated_tokens = self.client._estimate_tokens(contents)
        self.client.rate_limiter.acquire(resource_amount=estimated_tokens)

        # Set default generation config parameters
        default_config = {"stream": True}
        if generation_config:
            default_config.update(generation_config)

        # Get model object
        model_instance = genai.GenerativeModel(
            model_name=model or self.client.default_model,
            generation_config=default_config,
        )

        # Generate streaming response
        return model_instance.generate_content(contents)
