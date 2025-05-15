"""
GraphQL protocol adapter for Polvo.
"""

from usepolvo_core.protocols.graphql.client import AsyncGraphQLClient, GraphQLClient

__all__ = [
    "GraphQLClient",
    "AsyncGraphQLClient",
]
