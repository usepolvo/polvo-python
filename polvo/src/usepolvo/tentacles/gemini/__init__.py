# tentacles/gemini/__init__.py

from usepolvo.tentacles.gemini.client import GeminiTentacle
from usepolvo.tentacles.gemini.config import get_settings
from usepolvo.tentacles.gemini.embeddings import Embeddings
from usepolvo.tentacles.gemini.generation import Generation

__all__ = ["GeminiTentacle", "get_settings", "Generation", "Embeddings"]
