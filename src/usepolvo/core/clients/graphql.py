# core/clients/graphql.py
from typing import Any, Dict, Optional

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from usepolvo.core.clients.base import BaseClient
from usepolvo.core.exceptions import APIError


class GraphQLClient(BaseClient):
    """Template for GraphQL APIs."""

    def __init__(self):
        super().__init__()
        self._client = None

    def _setup_client(self):
        """Initialize GQL client."""
        transport = RequestsHTTPTransport(
            url=self.base_url,
            headers=self.auth.get_auth_headers() if self.auth else {},
            use_json=True,
        )
        self._client = Client(transport=transport, fetch_schema_from_transport=True)

    def execute(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute GraphQL query."""
        if not self._client:
            self._setup_client()

        try:
            return self._client.execute(gql(query), variable_values=variables)
        except Exception as e:
            raise APIError(f"GraphQL query failed: {str(e)}")
