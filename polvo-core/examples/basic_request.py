"""
Basic HTTP request example using Polvo Core.

This example demonstrates how to make basic HTTP requests using the Polvo Client.
"""

import asyncio

import usepolvo_core as pv


def sync_example():
    """Example using the synchronous client."""
    # Create a client
    client = pv.Client()

    # Make a GET request
    response = client.get("https://httpbin.org/get", params={"key": "value"})
    print(f"GET Status Code: {response.status_code}")
    print(f"Response JSON: {response.json()}")

    # Make a POST request with JSON data
    response = client.post("https://httpbin.org/post", json={"name": "Polvo", "type": "API Client"})
    print(f"POST Status Code: {response.status_code}")
    print(f"Response JSON: {response.json()}")

    # Using the context manager
    with pv.Client() as client:
        response = client.get("https://httpbin.org/headers", headers={"X-Custom-Header": "Polvo"})
        print(f"Headers Status Code: {response.status_code}")
        print(f"Custom header echoed: {response.json()}")


async def async_example():
    """Example using the asynchronous client."""
    # Create an async client
    async with pv.AsyncClient() as client:
        # Make a GET request
        response = await client.get("https://httpbin.org/get", params={"key": "value"})
        print(f"Async GET Status Code: {response.status_code}")
        print(f"Async Response JSON: {response.json()}")

        # Make a POST request with JSON data
        response = await client.post(
            "https://httpbin.org/post", json={"name": "Polvo Async", "type": "API Client"}
        )
        print(f"Async POST Status Code: {response.status_code}")
        print(f"Async Response JSON: {response.json()}")


if __name__ == "__main__":
    print("Running synchronous example:")
    sync_example()

    print("\nRunning asynchronous example:")
    asyncio.run(async_example())
