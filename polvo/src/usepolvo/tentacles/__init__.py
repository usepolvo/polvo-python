# tentacles/__init__.py
from usepolvo.tentacles.anthropic import AnthropicTentacle
from usepolvo.tentacles.base import BaseTentacle
from usepolvo.tentacles.gemini import GeminiTentacle
from usepolvo.tentacles.google_drive import GoogleDriveClient
from usepolvo.tentacles.hubspot import HubSpotClient
from usepolvo.tentacles.openai import OpenAITentacle

__all__ = [
    "BaseTentacle",
    "HubSpotClient",
    "OpenAITentacle",
    "GeminiTentacle",
    "AnthropicTentacle",
    "GoogleDriveClient",
]
