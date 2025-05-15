# tentacles/integrations/hubspot/companies.py


from typing import Any, Dict, List, Union

from usepolvo.core.tools.base import ToolDefinition
from usepolvo.tentacles.integrations.hubspot.base import HubSpotBaseTentacle
from usepolvo.tentacles.integrations.hubspot.models import (
    CompanyInput,
    CompanyListOutput,
    CompanyOutput,
)


class HubSpotCompaniesTentacle(HubSpotBaseTentacle):
    """HubSpot companies management tentacle"""

    DEFAULT_SCOPES = [
        "crm.objects.companies.read",
        "crm.objects.companies.write",
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
        """Set up the companies tentacle definition"""
        self._definition = ToolDefinition(
            name="hubspot_companies",
            description="""
            Manage HubSpot companies with full CRUD operations and search capabilities.

            Operations:
            - create: Create a new company (requires name)
            - update: Update an existing company (requires company_id)
            - get: Get a company by ID (requires company_id)
            - list: List companies with pagination
            - search: Search companies using a query string
            """,
            input_schema=CompanyInput.model_json_schema(),
            output_schema={
                "oneOf": [CompanyOutput.model_json_schema(), CompanyListOutput.model_json_schema()]
            },
        )

    async def execute(
        self, input: Union[CompanyInput, Dict[str, Any]]
    ) -> Union[CompanyOutput, CompanyListOutput]:
        """Execute company operations"""
        if isinstance(input, dict):
            company_input = CompanyInput(**input)
        else:
            company_input = input

        try:
            if company_input.operation == "create":
                if not company_input.name:
                    raise ValueError("Company name is required for creation")

                # Create company using HubSpot SDK
                simple_public_object_input = {"properties": company_input.properties}
                api_response = self.client.crm.companies.basic_api.create(
                    simple_public_object_input_for_create=simple_public_object_input
                )
                return CompanyOutput(**api_response.to_dict())

            elif company_input.operation == "update":
                if not company_input.company_id:
                    raise ValueError("Company ID is required for updates")

                # Update company using HubSpot SDK
                simple_public_object_input = {"properties": company_input.properties}
                api_response = self.client.crm.companies.basic_api.update(
                    company_id=company_input.company_id,
                    simple_public_object_input=simple_public_object_input,
                )
                return CompanyOutput(**api_response.to_dict())

            elif company_input.operation == "get":
                if not company_input.company_id:
                    raise ValueError("Company ID is required")

                # Get company using HubSpot SDK
                api_response = self.client.crm.companies.basic_api.get_by_id(
                    company_id=company_input.company_id,
                    properties=["name", "domain", "industry", "website"],
                )
                return CompanyOutput(**api_response.to_dict())

            elif company_input.operation == "list":
                # List companies using HubSpot SDK
                api_response = self.client.crm.companies.basic_api.get_page(
                    limit=company_input.limit,
                    properties=["name", "domain", "industry", "website"],
                )
                return CompanyListOutput(
                    results=[
                        CompanyOutput(**company.to_dict()) for company in api_response.results
                    ],
                    has_more=(
                        api_response.paging.next.get("after") is not None
                        if api_response.paging
                        else False
                    ),
                    total=len(api_response.results),
                )

            elif company_input.operation == "search":
                if not company_input.search_query:
                    raise ValueError("Search query is required")

                # Search companies using HubSpot SDK
                public_object_search_request = {
                    "query": company_input.search_query,
                    "limit": company_input.limit,
                    "properties": ["name", "domain", "industry", "website"],
                }
                api_response = self.client.crm.companies.search_api.do_search(
                    public_object_search_request=public_object_search_request
                )
                return CompanyListOutput(
                    results=[
                        CompanyOutput(**company.to_dict()) for company in api_response.results
                    ],
                    has_more=(
                        api_response.paging.next.get("after") is not None
                        if api_response.paging
                        else False
                    ),
                    total=api_response.total,
                )

            else:
                raise ValueError(f"Invalid operation: {company_input.operation}")

        except Exception as e:
            raise Exception(f"Company operation failed: {str(e)}")
