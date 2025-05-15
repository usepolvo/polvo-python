# tentacles/integrations/hubspot/models.py

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


# Common Models
class HubSpotProperties(BaseModel):
    """Base model for common HubSpot object properties"""

    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    archived: Optional[bool] = None


# Contact Models
class ContactInput(BaseModel):
    """Input model for contact operations"""

    operation: str = Field(
        ..., description="Operation to perform: create, update, get, list, or search"
    )
    email: Optional[EmailStr] = Field(None, description="Contact email (required for create)")
    firstname: Optional[str] = Field(None, description="First name")
    lastname: Optional[str] = Field(None, description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    contact_id: Optional[str] = Field(None, description="Contact ID (required for update/get)")
    limit: Optional[int] = Field(10, description="Number of records to return for list operations")
    search_query: Optional[str] = Field(None, description="Search query for searching contacts")

    @property
    def properties(self) -> Dict[str, Any]:
        """Get contact properties for API calls"""
        props = {}
        for field in ["email", "firstname", "lastname", "phone"]:
            value = getattr(self, field)
            if value is not None:
                props[field] = value
        return props


class ContactOutput(HubSpotProperties):
    """Output model for contact operations"""

    email: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    properties: Dict[str, Any]


class ContactListOutput(BaseModel):
    """Output model for list operations"""

    results: List[ContactOutput]
    has_more: bool
    total: Optional[int]


# Deal Models
class DealInput(BaseModel):
    """Input model for deal operations"""

    operation: str = Field(
        ..., description="Operation to perform: create, update, get, list, or search"
    )
    deal_id: Optional[str] = Field(None, description="Deal ID (required for update/get)")
    dealname: Optional[str] = Field(
        None, description="Deal name"
    )  # Changed from deal_name to dealname
    pipeline: Optional[str] = Field(None, description="Pipeline ID")
    dealstage: Optional[str] = Field(
        None, description="Deal stage"
    )  # Changed from stage to dealstage
    amount: Optional[float] = Field(None, description="Deal amount")
    closedate: Optional[datetime] = Field(
        None, description="Expected close date"
    )  # Changed from close_date to closedate
    associated_company: Optional[str] = Field(None, description="Associated company ID")
    associated_contacts: Optional[List[str]] = Field(
        None, description="List of associated contact IDs"
    )
    limit: Optional[int] = Field(10, description="Number of records to return for list operations")
    search_query: Optional[str] = Field(None, description="Search query for searching deals")

    @property
    def properties(self) -> Dict[str, Any]:
        """Get deal properties for API calls"""
        props = {}
        for field in [
            "dealname",
            "pipeline",
            "dealstage",
            "amount",
            "closedate",
        ]:  # Updated field names
            value = getattr(self, field)
            if value is not None:
                props[field] = value
        return props


class DealOutput(HubSpotProperties):
    """Output model for deal operations"""

    dealname: Optional[str] = None  # Changed from deal_name
    pipeline: Optional[str] = None
    dealstage: Optional[str] = None  # Changed from stage
    amount: Optional[float] = None
    closedate: Optional[datetime] = None  # Changed from close_date
    properties: Dict[str, Any]


class DealListOutput(BaseModel):
    """Output model for deal list operations"""

    results: List[DealOutput]
    has_more: bool
    total: Optional[int]


# Company Models
class CompanyInput(BaseModel):
    """Input model for company operations"""

    operation: str = Field(
        ..., description="Operation to perform: create, update, get, list, or search"
    )
    company_id: Optional[str] = Field(None, description="Company ID (required for update/get)")
    name: Optional[str] = Field(None, description="Company name")
    domain: Optional[str] = Field(None, description="Company website domain")
    industry: Optional[str] = Field(None, description="Company industry")
    type: Optional[str] = Field(None, description="Company type")
    city: Optional[str] = Field(None, description="City")
    country: Optional[str] = Field(None, description="Country")
    website: Optional[HttpUrl] = Field(None, description="Company website URL")
    limit: Optional[int] = Field(10, description="Number of records to return for list operations")
    search_query: Optional[str] = Field(None, description="Search query for searching companies")

    @property
    def properties(self) -> Dict[str, Any]:
        """Get company properties for API calls"""
        props = {}
        for field in ["name", "domain", "industry", "type", "city", "country", "website"]:
            value = getattr(self, field)
            if value is not None:
                props[field] = str(value)
        return props


class CompanyOutput(HubSpotProperties):
    """Output model for company operations"""

    id: str
    archived: bool = False
    archived_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    type: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    properties: Dict[str, Any]
    properties_with_history: Optional[Dict[str, Any]] = None


class CompanyListOutput(BaseModel):
    """Output model for company list operations"""

    results: List[CompanyOutput]
    has_more: bool
    total: Optional[int]
