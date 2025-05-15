"""
Authentication examples using Polvo Core.

This example demonstrates how to use different authentication methods with Polvo.
"""

import os

import usepolvo_core as pv
from usepolvo_core.auth import ApiKeyAuth, BasicAuth, BearerAuth, OAuth2
from usepolvo_core.auth.api_key import ApiKeyLocation


def basic_auth_example():
    """Example using Basic authentication."""
    # Create a client with Basic authentication
    client = pv.Client(auth=BasicAuth(username="user", password="pass"))

    # The auth headers will be automatically added to all requests
    response = client.get("https://httpbin.org/basic-auth/user/pass")
    print(f"Basic Auth Status: {response.status_code}")
    print(f"Response: {response.json()}")


def bearer_auth_example():
    """Example using Bearer token authentication."""
    # In a real app, you would get this token from an OAuth flow or other source
    token = "my-token"

    # Create a client with Bearer authentication
    client = pv.Client(auth=BearerAuth(token=token))

    # The Authorization header will be automatically added to all requests
    response = client.get("https://httpbin.org/headers")
    print(f"Bearer Auth Headers: {response.json()}")


def api_key_example():
    """Example using API key authentication."""
    # API key in header (default)
    header_client = pv.Client(auth=ApiKeyAuth(api_key="my-api-key", key_name="X-API-Key"))

    # The API key header will be automatically added to all requests
    response = header_client.get("https://httpbin.org/headers")
    print(f"API Key in Header: {response.json()}")

    # API key in query parameter
    query_client = pv.Client(
        auth=ApiKeyAuth(api_key="my-api-key", key_name="api_key", location=ApiKeyLocation.QUERY)
    )

    # The API key will be automatically added to the query string
    # Note: Currently this requires manual implementation for query params
    response = query_client.get("https://httpbin.org/get", params={"api_key": "my-api-key"})
    print(f"API Key in Query: {response.json()}")


if __name__ == "__main__":
    print("Basic Authentication Example:")
    basic_auth_example()

    print("\nBearer Authentication Example:")
    bearer_auth_example()

    print("\nAPI Key Authentication Example:")
    api_key_example()
