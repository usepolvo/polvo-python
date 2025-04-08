# tentacles/gemini/client.py

from typing import Any, Dict, List, Optional, Union

from google import genai
from google.genai import types

from usepolvo.core.auth.api_key import APIKeyAuth
from usepolvo.core.clients.rest import RESTClient
from usepolvo.core.rate_limiters.adaptive import AdaptiveRateLimiter
from usepolvo.tentacles.base import BaseTentacle
from usepolvo.tentacles.gemini.config import get_settings
from usepolvo.tentacles.gemini.embeddings import Embeddings
from usepolvo.tentacles.gemini.generation import Generation


class GeminiTentacle(RESTClient, BaseTentacle):
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

    def generate(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a response using Google Gemini.

        Implementation of the BaseTentacle.generate method.

        Args:
            messages: List of message objects
            model: Model to use, defaults to instance default_model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: System instructions
            tools: Tool definitions for function calling
            tool_choice: Specify which tool to use
            **kwargs: Additional parameters

        Returns:
            Standardized response dictionary
        """
        # Convert messages to Gemini format
        contents = self._format_messages_for_gemini(messages)

        # Pass generation configuration
        generation_config = {}
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        if temperature:
            generation_config["temperature"] = temperature

        # Generate content
        return self.generation.generate_content(
            contents=contents,
            model=model,
            generation_config=generation_config if generation_config else None,
            tools=tools,
            system_instruction=system_message,  # Gemini uses system_instruction
        )

    def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None,
        **kwargs,
    ):
        """
        Generate a streaming response using Google Gemini.

        Implementation of the BaseTentacle.generate_stream method.

        Args:
            messages: List of message objects
            model: Model to use, defaults to instance default_model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: System instructions
            **kwargs: Additional parameters

        Returns:
            A stream of response chunks
        """
        # Convert messages to Gemini format
        contents = self._format_messages_for_gemini(messages)

        # Prepare generation config
        generation_config = {"stream": True}
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        if temperature:
            generation_config["temperature"] = temperature

        # Create model with system instruction
        model_instance = genai.GenerativeModel(
            model_name=model or self.default_model,
            generation_config=generation_config,
            system_instruction=system_message,
        )

        # Generate streaming response
        return model_instance.generate_content(contents)

    def _format_messages_for_gemini(self, messages: List[Dict[str, Any]]) -> Any:
        """
        Format messages from the standard format to Gemini's expected format.

        Args:
            messages: List of messages in the standard format

        Returns:
            Messages in Gemini's format
        """
        # For simple cases, we can use the first message content directly
        if len(messages) == 1 and "content" in messages[0]:
            return messages[0]["content"]

        # For more complex conversations, format as Gemini expects
        formatted_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                formatted_messages.append({"role": "user", "parts": [{"text": content}]})
            elif role == "assistant":
                formatted_messages.append({"role": "model", "parts": [{"text": content}]})
            # Gemini doesn't use system messages in the messages list

        return formatted_messages
