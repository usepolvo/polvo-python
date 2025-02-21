# tentacles/integration/__init__.py
from .hubspot.base import HubSpotBaseTentacle
from .hubspot.client import HubSpotBaseClient
from .hubspot.models import ContactInput, ContactListOutput, ContactOutput

__all__ = [
    "HubSpotBaseClient",
    "HubSpotBaseTentacle",
    "ContactInput",
    "ContactListOutput",
    "ContactOutput",
]
