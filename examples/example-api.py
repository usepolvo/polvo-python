from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field

from usepolvo.arms.tentacles.api import APITentacle
from usepolvo.arms.tentacles.base import TentacleDefinition
from usepolvo.brain.base import create_brain
from usepolvo.tentacles.integration import HubSpotClient


# User defines their models
class ContactInput(BaseModel):
    operation: str = Field(..., description="Operation to perform: create, update, get, or list")
    email: Optional[EmailStr] = Field(
        None, description="Contact email (required for create/update)"
    )
    firstname: Optional[str] = Field(None, alias="first_name", description="Contact first name")
    lastname: Optional[str] = Field(None, alias="last_name", description="Contact last name")
    phone: Optional[str] = Field(None, description="Contact phone number")
    contact_id: Optional[str] = Field(None, description="Contact ID (required for update/get)")
    limit: Optional[int] = Field(10, description="Number of contacts to list")

    class Config:
        populate_by_name = True

    @property
    def properties(self) -> Dict[str, Any]:
        """Get contact properties for API calls."""
        props = {}
        for field in ["email", "firstname", "lastname", "phone"]:
            value = getattr(self, field)
            if value is not None:
                props[field] = value
        return props


class ContactOutput(BaseModel):
    id: str
    properties: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    archived: Optional[bool] = None


class ContactListOutput(BaseModel):
    results: List[ContactOutput]
    has_more: bool


# User implements their client
class MyHubSpotClient(HubSpotClient):
    """Custom HubSpot client implementation."""

    def create_contact(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact."""
        try:
            result = self.client.crm.contacts.basic_api.create(
                simple_public_object_input_for_create={"properties": properties}
            )
            return result.to_dict()
        except Exception as e:
            if getattr(e, "status", None) == 401:
                self.refresh_token()
                result = self.client.crm.contacts.basic_api.create(
                    simple_public_object_input={"properties": properties}
                )
                return result.to_dict()
            raise e

    def update_contact(self, contact_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing contact."""
        try:
            result = self.client.crm.contacts.basic_api.update(
                contact_id=contact_id, simple_public_object_input={"properties": properties}
            )
            return result.to_dict()
        except Exception as e:
            if getattr(e, "status", None) == 401:
                self.refresh_token()
                result = self.client.crm.contacts.basic_api.update(
                    contact_id=contact_id, simple_public_object_input={"properties": properties}
                )
                return result.to_dict()
            raise e

    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get a contact by ID."""
        try:
            result = self.client.crm.contacts.basic_api.get_by_id(contact_id)
            return result.to_dict()
        except Exception as e:
            if getattr(e, "status", None) == 401:
                self.refresh_token()
                result = self.client.crm.contacts.basic_api.get_by_id(contact_id)
                return result.to_dict()
            raise e

    def list_contacts(self, limit: int = 10) -> Dict[str, Any]:
        """List contacts with pagination."""
        try:
            result = self.client.crm.contacts.basic_api.get_page(limit=limit)
            return {
                "results": [r.to_dict() for r in result.results],
                "has_more": bool(getattr(result, "paging", False)),
            }
        except Exception as e:
            if getattr(e, "status", None) == 401:
                self.refresh_token()
                result = self.client.crm.contacts.basic_api.get_page(limit=limit)
                return {
                    "results": [r.to_dict() for r in result.results],
                    "has_more": bool(getattr(result, "pagging", False)),
                }
            raise e


class HubSpotContactsTentacle(APITentacle[ContactInput, Union[ContactOutput, ContactListOutput]]):
    """HubSpot contacts management tentacle."""

    def __init__(self):
        self.client = MyHubSpotClient()
        super().__init__(self.client)

    def _setup(self) -> None:
        """Set up the HubSpot tentacle definition."""
        self._definition = TentacleDefinition(
            name="hubspot_contacts",
            description="""
            Manage HubSpot contacts with input validation.

            Operations:
            - create: Create a new contact (requires email)
            - update: Update an existing contact (requires contact_id)
            - get: Get a contact by ID (requires contact_id)
            - list: List contacts with pagination

            Examples:
            - Create: {"operation": "create", "email": "test@example.com", "first_name": "Test"}
            - Update: {"operation": "update", "contact_id": "123", "phone": "555-0123"}
            - Get: {"operation": "get", "contact_id": "123"}
            - List: {"operation": "list", "limit": 5}
            """,
            input_schema=ContactInput.model_json_schema(),
            output_schema={
                "oneOf": [ContactOutput.model_json_schema(), ContactListOutput.model_json_schema()]
            },
        )

    async def execute(
        self, input: Union[ContactInput, Dict[str, Any]]
    ) -> Union[ContactOutput, ContactListOutput]:
        """Execute HubSpot contact operations."""
        # Convert dict to schema if needed
        if isinstance(input, dict):
            contact_input = ContactInput(**input)
        else:
            contact_input = input

        if contact_input.operation == "create":
            if not contact_input.email:
                raise ValueError("Email is required for contact creation")
            result = self.client.create_contact(contact_input.properties)
            return ContactOutput(**result)

        elif contact_input.operation == "update":
            if not contact_input.contact_id:
                raise ValueError("Contact ID is required for updates")
            result = self.client.update_contact(contact_input.contact_id, contact_input.properties)
            return ContactOutput(**result)

        elif contact_input.operation == "get":
            if not contact_input.contact_id:
                raise ValueError("Contact ID is required")
            result = self.client.get_contact(contact_input.contact_id)
            return ContactOutput(**result)

        elif contact_input.operation == "list":
            result = self.client.list_contacts(limit=contact_input.limit)
            return ContactListOutput(**result)

        else:
            raise ValueError(f"Invalid operation: {contact_input.operation}")


# Usage example
async def example_usage():
    # Create tentacle
    hubspot = HubSpotContactsTentacle()

    # 1. Using schema input
    schema_result = await hubspot(
        ContactInput(
            operation="create", email="test@example.com", first_name="Test", last_name="User"
        )
    )
    print(f"Created contact (schema): {schema_result.id}")

    # 2. Using dict input
    dict_result = await hubspot({"operation": "list", "limit": 5})
    print(f"Listed contacts (dict): {len(dict_result.results)} contacts")

    # 3. Using keyword arguments
    if schema_result.id:  # Use ID from first creation
        kwargs_result = await hubspot(
            operation="update", contact_id=schema_result.id, phone="555-0123"
        )
        print(f"Updated contact (kwargs): {kwargs_result.properties}")

    # 4. Using with Brain (which will use dict/kwargs format)
    brain = await create_brain(
        name="HubSpot Assistant",
        tentacles=[hubspot],
        system_prompt="You are a HubSpot contact management assistant.",
    )
    response = await brain.process(
        "Create a new contact with email john@example.com and name John Smith"
    )
    print(f"Brain response: {response}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
