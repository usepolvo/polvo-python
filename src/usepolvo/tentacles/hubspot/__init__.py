# tentacles/hubspot/__init__.py

from usepolvo.tentacles.hubspot.client import HubSpotClient
from usepolvo.tentacles.hubspot.config import get_settings

__all__ = ["HubSpotClient", "get_settings"]
