# tentacles/integrations/hubspot/deals.py

from typing import Any, Dict, List, Union

from usepolvo.core.tools.base import ToolDefinition
from usepolvo.tentacles.integrations.hubspot.base import HubSpotBaseTentacle
from usepolvo.tentacles.integrations.hubspot.models import (
    DealInput,
    DealListOutput,
    DealOutput,
)


class HubSpotDealsTentacle(HubSpotBaseTentacle):
    """HubSpot deals management tentacle"""

    DEFAULT_SCOPES = [
        "crm.objects.deals.read",
        "crm.objects.deals.write",
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
        """Set up the deals tentacle definition"""
        self._definition = ToolDefinition(
            name="hubspot_deals",
            description="""
            Manage HubSpot deals with full CRUD operations and search capabilities.

            Operations:
            - create: Create a new deal (requires deal_name)
            - update: Update an existing deal (requires deal_id)
            - get: Get a deal by ID (requires deal_id)
            - list: List deals with pagination
            - search: Search deals using a query string
            """,
            input_schema=DealInput.model_json_schema(),
            output_schema={
                "oneOf": [DealOutput.model_json_schema(), DealListOutput.model_json_schema()]
            },
        )

    async def execute(
        self, input: Union[DealInput, Dict[str, Any]]
    ) -> Union[DealOutput, DealListOutput]:
        """Execute deal operations"""
        if isinstance(input, dict):
            deal_input = DealInput(**input)
        else:
            deal_input = input

        try:
            if deal_input.operation == "create":
                if not deal_input.dealname:
                    raise ValueError("Deal name is required for creation")

                # Create deal using HubSpot SDK
                simple_public_object_input = {"properties": deal_input.properties}
                api_response = self.client.crm.deals.basic_api.create(
                    simple_public_object_input_for_create=simple_public_object_input
                )

                # Handle associations if provided
                if deal_input.associated_company:
                    self.client.crm.associations.batch_api.create(
                        from_object_type="deals",
                        to_object_type="companies",
                        batch_input_public_association={
                            "inputs": [
                                {
                                    "from": {"id": api_response.id},
                                    "to": {"id": deal_input.associated_company},
                                    "type": "deal_to_company",
                                }
                            ]
                        },
                    )

                if deal_input.associated_contacts:
                    self.client.crm.associations.batch_api.create(
                        from_object_type="deals",
                        to_object_type="contacts",
                        batch_input_public_association={
                            "inputs": [
                                {
                                    "from": {"id": api_response.id},
                                    "to": {"id": contact_id},
                                    "type": "deal_to_contact",
                                }
                                for contact_id in deal_input.associated_contacts
                            ]
                        },
                    )

                return DealOutput(**api_response.to_dict())

            elif deal_input.operation == "update":
                if not deal_input.deal_id:
                    raise ValueError("Deal ID is required for updates")

                # Update deal using HubSpot SDK
                simple_public_object_input = {"properties": deal_input.properties}
                api_response = self.client.crm.deals.basic_api.update(
                    deal_id=deal_input.deal_id,
                    simple_public_object_input=simple_public_object_input,
                )
                return DealOutput(**api_response.to_dict())

            elif deal_input.operation == "get":
                if not deal_input.deal_id:
                    raise ValueError("Deal ID is required")

                # Get deal using HubSpot SDK
                api_response = self.client.crm.deals.basic_api.get_by_id(
                    deal_id=deal_input.deal_id,
                    properties=["dealname", "amount", "pipeline", "dealstage", "closedate"],
                )
                return DealOutput(**api_response.to_dict())

            elif deal_input.operation == "list":
                # List deals using HubSpot SDK
                api_response = self.client.crm.deals.basic_api.get_page(
                    limit=deal_input.limit,
                    properties=["dealname", "amount", "pipeline", "dealstage", "closedate"],
                )
                return DealListOutput(
                    results=[DealOutput(**deal.to_dict()) for deal in api_response.results],
                    has_more=(
                        api_response.paging.next.get("after") is not None
                        if api_response.paging
                        else False
                    ),
                    total=len(api_response.results),
                )

            elif deal_input.operation == "search":
                if not deal_input.search_query:
                    raise ValueError("Search query is required")

                # Search deals using HubSpot SDK
                public_object_search_request = {
                    "query": deal_input.search_query,
                    "limit": deal_input.limit,
                    "properties": ["dealname", "amount", "pipeline", "dealstage", "closedate"],
                }
                api_response = self.client.crm.deals.search_api.do_search(
                    public_object_search_request=public_object_search_request
                )
                return DealListOutput(
                    results=[DealOutput(**deal.to_dict()) for deal in api_response.results],
                    has_more=(
                        api_response.paging.next.get("after") is not None
                        if api_response.paging
                        else False
                    ),
                    total=api_response.total,
                )

            else:
                raise ValueError(f"Invalid operation: {deal_input.operation}")

        except Exception as e:
            raise Exception(f"Deal operation failed: {str(e)}")
