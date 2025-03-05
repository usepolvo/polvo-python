# tentacles/integrations/hubspot/contacts.py

from typing import Any, Dict, List, Union

import hubspot

from usepolvo.core.tools.base import ToolDefinition
from usepolvo.tentacles.integrations.hubspot.base import HubSpotBaseTentacle
from usepolvo.tentacles.integrations.hubspot.models import (
    ContactInput,
    ContactListOutput,
    ContactOutput,
)


class HubSpotContactsTentacle(HubSpotBaseTentacle):
    """HubSpot contacts management tentacle"""

    DEFAULT_SCOPES = [
        "crm.objects.contacts.read",
        "crm.objects.contacts.write",
    ]

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        redirect_uri: str = None,
        scopes: List[str] = None,
    ):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scopes=scopes or self.DEFAULT_SCOPES,
        )

    def _setup(self) -> None:
        """Set up the contacts tentacle definition"""
        self._definition = ToolDefinition(
            name="hubspot_contacts",
            description="""
            Manage HubSpot contacts with full CRUD operations and search capabilities.

            Operations:
            - create: Create a new contact (requires email)
            - update: Update an existing contact (requires contact_id)
            - get: Get a contact by ID (requires contact_id)
            - list: List contacts with pagination
            - search: Search contacts using a query string
            """,
            input_schema=ContactInput.model_json_schema(),
            output_schema={
                "oneOf": [ContactOutput.model_json_schema(), ContactListOutput.model_json_schema()]
            },
        )

    async def execute(
        self, input: Union[ContactInput, Dict[str, Any]]
    ) -> Union[ContactOutput, ContactListOutput]:
        """Execute contact operations"""
        if isinstance(input, dict):
            contact_input = ContactInput(**input)
        else:
            contact_input = input

        try:
            # Ensure token is valid before making request
            self.client._ensure_valid_token()

            if contact_input.operation == "create":
                if not contact_input.email:
                    raise ValueError("Email is required for contact creation")

                try:
                    # Create contact using HubSpot SDK
                    simple_public_object_input = {"properties": contact_input.properties}
                    api_response = self.client.crm.contacts.basic_api.create(
                        simple_public_object_input_for_create=simple_public_object_input
                    )
                    return ContactOutput(**api_response.to_dict())
                except hubspot.crm.contacts.exceptions.UnauthorizedException:
                    # If unauthorized, try refreshing token and retry once
                    self.client.refresh_token()
                    api_response = self.client.crm.contacts.basic_api.create(
                        simple_public_object_input_for_create=simple_public_object_input
                    )
                    return ContactOutput(**api_response.to_dict())

            elif contact_input.operation == "update":
                if not contact_input.contact_id:
                    raise ValueError("Contact ID is required for updates")

                # Update contact using HubSpot SDK
                simple_public_object_input = {"properties": contact_input.properties}
                api_response = self.client.crm.contacts.basic_api.update(
                    contact_id=contact_input.contact_id,
                    simple_public_object_input=simple_public_object_input,
                )
                return ContactOutput(**api_response.to_dict())

            elif contact_input.operation == "get":
                if not contact_input.contact_id:
                    raise ValueError("Contact ID is required")

                # Get contact using HubSpot SDK
                api_response = self.client.crm.contacts.basic_api.get_by_id(
                    contact_id=contact_input.contact_id,
                    properties=["email", "firstname", "lastname", "phone"],
                )
                return ContactOutput(**api_response.to_dict())

            elif contact_input.operation == "list":
                # List contacts using HubSpot SDK
                api_response = self.client.crm.contacts.basic_api.get_page(
                    limit=contact_input.limit,
                    properties=["email", "firstname", "lastname", "phone"],
                )
                return ContactListOutput(
                    results=[
                        ContactOutput(**contact.to_dict()) for contact in api_response.results
                    ],
                    has_more=(
                        hasattr(api_response.paging, "next")
                        and api_response.paging.next is not None
                        if api_response.paging
                        else False
                    ),
                    total=len(api_response.results),
                )

            elif contact_input.operation == "search":
                if not contact_input.search_query:
                    raise ValueError("Search query is required")

                # Search contacts using HubSpot SDK
                public_object_search_request = {
                    "query": contact_input.search_query,
                    "limit": contact_input.limit,
                    "properties": ["email", "firstname", "lastname", "phone"],
                }
                api_response = self.client.crm.contacts.search_api.do_search(
                    public_object_search_request=public_object_search_request
                )
                return ContactListOutput(
                    results=[
                        ContactOutput(**contact.to_dict()) for contact in api_response.results
                    ],
                    has_more=(
                        api_response.paging.next.get("after") is not None
                        if api_response.paging
                        else False
                    ),
                    total=api_response.total,
                )

            else:
                raise ValueError(f"Invalid operation: {contact_input.operation}")

        except Exception as e:
            raise Exception(f"Contact operation failed: {str(e)}")
