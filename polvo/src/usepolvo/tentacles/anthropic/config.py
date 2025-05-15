# tentacles/anthropic/config.py

from functools import lru_cache
from typing import Optional

from usepolvo.core.config import PolvoSettings


@lru_cache
def get_settings():
    return AnthropicSettings()


class AnthropicSettings(PolvoSettings):
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_API_BASE: str = "https://api.anthropic.com"
    ANTHROPIC_DEFAULT_MODEL: str = "claude-3-opus-20240229"
    ANTHROPIC_RATE_LIMIT_RPM: int = 60  # Requests per minute
    ANTHROPIC_RATE_LIMIT_TPM: int = 120000  # Tokens per minute
