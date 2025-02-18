# beak/config.py

from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


@lru_cache
def get_settings():
    return PolvoSettings()


class PolvoSettings(BaseSettings):
    """
    Base settings class that reads environment variables with POLVO_ prefix.
    """

    model_config = SettingsConfigDict(
        env_prefix="POLVO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    ENCRYPTION_KEY: str
