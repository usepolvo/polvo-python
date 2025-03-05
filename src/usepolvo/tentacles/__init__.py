# tentacles/integration/__init__.py
from .integrations.hubspot.base import HubSpotBaseTentacle
from .integrations.hubspot.client import HubSpotBaseClient
from .integrations.hubspot.models import ContactInput, ContactListOutput, ContactOutput

__all__ = [
    "HubSpotBaseClient",
    "HubSpotBaseTentacle",
    "ContactInput",
    "ContactListOutput",
    "ContactOutput",
]
