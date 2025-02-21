# tentacles/integrations/hubspot/base.py

from typing import List, Set

from usepolvo.arms.tentacles.api import APITentacle
from usepolvo.tentacles.integrations.hubspot.client import HubSpotBaseClient
from usepolvo.tentacles.integrations.hubspot.config import get_settings


class HubSpotBaseTentacle(APITentacle):
    """Base class for HubSpot tentacles with common authentication"""

    # Shared client instance and scopes as class variables
    _shared_client = None
    _current_scopes: Set[str] = set()

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        redirect_uri: str = None,
        scopes: List[str] = None,
    ):
        # Get default settings
        settings = get_settings()

        # Combine default scopes from settings with any additional scopes
        base_scopes = set(settings.HUBSPOT_OAUTH_SCOPES)  # Always include oauth scope etc
        additional_scopes = set(scopes) if scopes else set()

        if hasattr(self, "DEFAULT_SCOPES"):
            additional_scopes.update(self.DEFAULT_SCOPES)

        # First combine with existing scopes
        all_required_scopes = HubSpotBaseTentacle._current_scopes | base_scopes | additional_scopes

        # Check if we need to re-authenticate due to new scopes
        new_scopes = all_required_scopes - HubSpotBaseTentacle._current_scopes
        if new_scopes and HubSpotBaseTentacle._shared_client:
            print("Re-initializing client due to new scopes")
            HubSpotBaseTentacle._shared_client = None  # Force new client creation

        if not HubSpotBaseTentacle._shared_client:
            HubSpotBaseTentacle._shared_client = HubSpotBaseClient(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scopes=list(all_required_scopes),  # Use complete set of scopes
            )
            # Update current scopes with all required scopes
            HubSpotBaseTentacle._current_scopes = all_required_scopes

        self.client = HubSpotBaseTentacle._shared_client
        super().__init__(self.client)
