# tentacles/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseTentacle(ABC):
    """Base class for AI model tentacles with a standardized interface."""

    @abstractmethod
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
        Generate a response from an AI model using a standardized interface.

        Args:
            messages: List of message objects in the format [{"role": "user", "content": "..."}]
            model: Model to use, defaults to instance default_model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: System instructions for the model
            tools: Tool definitions for function calling
            tool_choice: Specify which tool to use
            **kwargs: Additional model-specific parameters

        Returns:
            Standardized response dictionary
        """
        pass

    @abstractmethod
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
        Generate a streaming response from an AI model.

        Args:
            messages: List of message objects in the format [{"role": "user", "content": "..."}]
            model: Model to use, defaults to instance default_model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: System instructions for the model
            **kwargs: Additional model-specific parameters

        Returns:
            A stream of response chunks
        """
        pass
