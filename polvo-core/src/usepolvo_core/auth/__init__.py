"""
Authentication methods for Polvo.
"""

from usepolvo_core.auth.api_key import ApiKeyAuth
from usepolvo_core.auth.base import Auth
from usepolvo_core.auth.basic import BasicAuth
from usepolvo_core.auth.bearer import BearerAuth
from usepolvo_core.auth.oauth2 import OAuth2

__all__ = [
    "Auth",
    "BasicAuth",
    "BearerAuth",
    "OAuth2",
    "ApiKeyAuth",
]
