from functools import lru_cache
from typing import List, Optional

from usepolvo.beak.config import PolvoSettings


@lru_cache
def get_settings():
    return HubSpotSettings()


class HubSpotSettings(PolvoSettings):
    HUBSPOT_OAUTH_URL: str = "https://app.hubspot.com/oauth/authorize"
    HUBSPOT_OAUTH_TOKEN_URL: str = "https://api.hubapi.com/oauth/v1/token"
    HUBSPOT_OAUTH_SCOPES: List[str] = ["crm.objects.contacts.write", "oauth", "crm.objects.contacts.read"]
    HUBSPOT_API_KEY: Optional[str] = None
    HUBSPOT_CLIENT_ID: Optional[str] = None
    HUBSPOT_CLIENT_SECRET: Optional[str] = None
    HUBSPOT_REDIRECT_URI: Optional[str] = None
