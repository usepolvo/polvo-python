# tentacles/openai/config.py

from functools import lru_cache
from typing import Optional

from usepolvo.core.config import PolvoSettings


@lru_cache
def get_settings():
    return OpenAISettings()


class OpenAISettings(PolvoSettings):
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_ORGANIZATION_ID: Optional[str] = None
    OPENAI_DEFAULT_MODEL: str = "gpt-4o"
    OPENAI_RATE_LIMIT_RPM: int = 60  # Requests per minute
    OPENAI_RATE_LIMIT_TPM: int = 120000  # Tokens per minute
