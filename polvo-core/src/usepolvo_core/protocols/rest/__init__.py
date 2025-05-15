"""
REST protocol adapter for Polvo.
"""

from usepolvo_core.protocols.rest.client import AsyncRestClient, RestClient

__all__ = [
    "RestClient",
    "AsyncRestClient",
]
