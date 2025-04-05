# tentacles/gemini/config.py

from functools import lru_cache
from typing import Optional

from usepolvo.core.config import PolvoSettings


@lru_cache
def get_settings():
    return GeminiSettings()


class GeminiSettings(PolvoSettings):
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_API_BASE: str = "https://generativelanguage.googleapis.com/v1"
    GEMINI_DEFAULT_MODEL: str = "gemini-1.5-pro"
    GEMINI_RATE_LIMIT_QPM: int = 60  # Queries per minute
    GEMINI_RATE_LIMIT_TPM: int = 120000  # Tokens per minute
