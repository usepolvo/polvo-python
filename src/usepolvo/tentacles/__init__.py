# tentacles/__init__.py
from usepolvo.tentacles.anthropic import AnthropicTentacle
from usepolvo.tentacles.gemini import GeminiTentacle
from usepolvo.tentacles.hubspot import HubSpotClient
from usepolvo.tentacles.openai import OpenAITentacle

__all__ = ["HubSpotClient", "OpenAITentacle", "GeminiTentacle", "AnthropicTentacle"]
