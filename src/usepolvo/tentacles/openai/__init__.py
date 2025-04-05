# tentacles/openai/__init__.py

from usepolvo.tentacles.openai.chat import ChatCompletions
from usepolvo.tentacles.openai.client import OpenAITentacle
from usepolvo.tentacles.openai.config import get_settings
from usepolvo.tentacles.openai.embeddings import Embeddings

__all__ = ["OpenAITentacle", "get_settings", "ChatCompletions", "Embeddings"]
