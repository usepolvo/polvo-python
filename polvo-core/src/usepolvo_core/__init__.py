"""
Polvo Core - A requests-style, protocol-agnostic SDK for API integration

This package provides a simple, ergonomic interface for interacting with
various API protocols (REST, GraphQL, SOAP) while maintaining the familiar
feel of the Python 'requests' library.
"""

__version__ = "0.1.0"

import usepolvo_core.auth as auth
import usepolvo_core.middleware as middleware
from usepolvo_core.core.client import AsyncClient, Client
from usepolvo_core.core.response import Response
from usepolvo_core.protocols.graphql import AsyncGraphQLClient, GraphQLClient
from usepolvo_core.protocols.rest import AsyncRestClient, RestClient
from usepolvo_core.protocols.soap import AsyncSoapClient, SoapClient

__all__ = [
    "Client",
    "AsyncClient",
    "Response",
    "auth",
    "middleware",
    "RestClient",
    "AsyncRestClient",
    "GraphQLClient",
    "AsyncGraphQLClient",
    "SoapClient",
    "AsyncSoapClient",
]
