# src/usepolvo/tentacles/google_drive/config.py
from functools import lru_cache
from typing import List, Optional

from usepolvo.core.config import PolvoSettings


@lru_cache
def get_settings():
    return GoogleDriveSettings()


class GoogleDriveSettings(PolvoSettings):
    """Configuration settings for Google Drive integration."""

    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    GOOGLE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    GOOGLE_API_BASE: str = "https://www.googleapis.com/drive/v3"
    GOOGLE_DEFAULT_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.metadata.readonly",
    ]
