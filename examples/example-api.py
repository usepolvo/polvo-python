from usepolvo.brain.base import create_brain
from usepolvo.tentacles.hubspot.companies import HubSpotCompaniesTentacle
from usepolvo.tentacles.hubspot.contacts import HubSpotContactsTentacle
from usepolvo.tentacles.hubspot.deals import HubSpotDealsTentacle
from usepolvo.tentacles.hubspot.models import ContactInput, DealInput


async def example_usage():
    """Example usage of HubSpot tentacles."""

    # Initialize contacts tentacle with default scopes
    contacts = HubSpotContactsTentacle()

    # Initialize companies tentacle with default scopes
    companies = HubSpotCompaniesTentacle()

    # Initialize deals tentacle with custom scopes
    deals = HubSpotDealsTentacle(scopes=["crm.objects.deals.read"])  # Only read access

    # 1. Create a contact using schema input
    contact_result = await contacts.execute(
        ContactInput(
            operation="create",
            email="test@example.com",
            firstname="Test",
            lastname="User",
        )
    )

    # 2. Create a company using dict input
    company_result = await companies.execute(
        {
            "operation": "create",
            "name": "Test Company",
            "domain": "testcompany.com",
        }
    )
    print(f"Created company: {company_result.id}")

    # 3. Create a deal associated with the contact and company
    if contact_result.id and company_result.id:
        deal_result = await deals.execute(
            DealInput(
                operation="create",
                dealname="Test Deal",
                amount=10000.0,
                associated_company=company_result.id,
                associated_contacts=[contact_result.id],
            )
        )
        print(f"Created deal: {deal_result.id}")

    # 4. List contacts with pagination
    contacts_list = await contacts.execute({"operation": "list", "limit": 5})
    print(f"Listed contacts: {len(contacts_list.results)} contacts")

    # 5. Using with Brain
    brain = await create_brain(
        name="HubSpot Assistant",
        tentacles=[contacts, companies, deals],
        system_prompt="You are a HubSpot CRM management assistant.",
    )

    response = await brain.process(
        "Create a new contact with email john@example.com and name John Smith"
    )
    print(f"Brain response: {response}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
