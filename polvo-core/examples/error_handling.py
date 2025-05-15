"""
Error Handling examples using Polvo Core.

This example demonstrates how to handle various error scenarios with Polvo.
"""

import asyncio
import time

import usepolvo_core as pv
from usepolvo_core.core.exceptions import (
    HTTPError,
    PolvoError,
    TimeoutError,
    TransportError,
)


def basic_error_handling():
    """Example of basic error handling."""
    client = pv.Client()

    # Example 1: Handle 404 Not Found
    try:
        response = client.get("https://httpbin.org/status/404")
        response.raise_for_status()  # This will raise an HTTPError
    except HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Status Code: {e.status_code}")

    # Example 2: Handle 500 Server Error
    try:
        response = client.get("https://httpbin.org/status/500")
        response.raise_for_status()
    except HTTPError as e:
        print(f"Server Error: {e}")
        print(f"Status Code: {e.status_code}")

    # Example 3: Check response without raising
    response = client.get("https://httpbin.org/status/404")
    if not response.ok:
        print(f"Request failed with status: {response.status_code}")

    # Example 4: Connection error (invalid host)
    try:
        client.get("https://this-does-not-exist.example.com")
    except TransportError as e:
        print(f"Transport Error: {e}")


def timeout_error_handling():
    """Example of handling timeout errors."""
    # Create a client with a short timeout
    client = pv.Client(timeout=1.0)

    # Example 1: Request that takes too long
    try:
        response = client.get("https://httpbin.org/delay/3")  # Will timeout after 1s
    except TimeoutError as e:
        print(f"Timeout Error: {e}")
    except Exception as e:
        print(f"Unexpected error type: {type(e).__name__}: {e}")


def retry_with_error_handling():
    """Example of using retry with error handling."""
    # Create a client with retry middleware
    client = pv.Client(middlewares=[pv.middleware.RetryMiddleware(retries=3, backoff_factor=0.5)])

    # Example: Request that fails but retries
    start_time = time.time()
    try:
        response = client.get("https://httpbin.org/status/500")
        response.raise_for_status()
    except HTTPError as e:
        elapsed = time.time() - start_time
        print(f"Request failed after retries: {e}")
        print(f"Elapsed time with retries: {elapsed:.2f}s")


async def async_error_handling():
    """Example of async error handling."""
    async with pv.AsyncClient() as client:
        # Example 1: Handle errors in concurrent requests
        urls = [
            "https://httpbin.org/status/200",
            "https://httpbin.org/status/404",
            "https://httpbin.org/status/500",
            "https://this-does-not-exist.example.com",
        ]

        # Create tasks
        tasks = [client.get(url) for url in urls]

        # Wait for all requests to complete, even if some fail
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process the results
        for i, result in enumerate(responses):
            if isinstance(result, Exception):
                print(f"Request {i+1} failed: {type(result).__name__}: {result}")
            else:
                print(f"Request {i+1} succeeded: Status {result.status_code}")


if __name__ == "__main__":
    print("Basic Error Handling:")
    basic_error_handling()

    print("\nTimeout Error Handling:")
    timeout_error_handling()

    print("\nRetry with Error Handling:")
    retry_with_error_handling()

    print("\nAsync Error Handling:")
    asyncio.run(async_error_handling())
