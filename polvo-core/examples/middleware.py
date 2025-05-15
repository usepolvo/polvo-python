"""
Middleware examples using Polvo Core.

This example demonstrates how to use different middleware components with Polvo.
"""

import asyncio
import logging

import usepolvo_core as pv
from usepolvo_core.middleware import (
    LoggingMiddleware,
    RateLimiterMiddleware,
    RetryMiddleware,
)


def setup_logging():
    """Set up logging for the examples."""
    logger = logging.getLogger("polvo")
    logger.setLevel(logging.INFO)

    # Create a console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger


def logging_middleware_example():
    """Example using LoggingMiddleware."""
    logger = setup_logging()

    # Create a client with LoggingMiddleware
    client = pv.Client(middlewares=[LoggingMiddleware(logger=logger)])

    # Each request will be logged
    response = client.get("https://httpbin.org/get", params={"q": "logging"})
    print(f"Logging Status: {response.status_code}")

    # Try a different HTTP method
    response = client.post("https://httpbin.org/post", json={"data": "test"})
    print(f"Logging POST Status: {response.status_code}")


def retry_middleware_example():
    """Example using RetryMiddleware."""
    logger = setup_logging()

    # Create a client with RetryMiddleware and LoggingMiddleware
    client = pv.Client(
        middlewares=[
            RetryMiddleware(retries=3, backoff_factor=0.5),
            LoggingMiddleware(logger=logger),
        ]
    )

    # This endpoint should return a 500 error, which will trigger retries
    try:
        response = client.get("https://httpbin.org/status/500")
        print(f"Retry Status: {response.status_code}")
    except Exception as e:
        print(f"Retry example caught exception after retries: {e}")

    # This endpoint should succeed
    response = client.get("https://httpbin.org/status/200")
    print(f"Retry Success Status: {response.status_code}")


def rate_limit_middleware_example():
    """Example using RateLimiterMiddleware."""
    logger = setup_logging()

    # Create a client with RateLimiterMiddleware and LoggingMiddleware
    client = pv.Client(
        middlewares=[
            RateLimiterMiddleware(calls=2, period=1.0),  # 2 requests per second
            LoggingMiddleware(logger=logger),
        ]
    )

    # Make multiple requests that will be rate-limited
    for i in range(5):
        response = client.get("https://httpbin.org/get", params={"i": i})
        print(f"Rate Limit Request {i+1}: {response.status_code}")


async def async_middleware_example():
    """Example using middleware with AsyncClient."""
    logger = setup_logging()

    # Create an async client with multiple middleware
    async with pv.AsyncClient(
        middlewares=[
            LoggingMiddleware(logger=logger),
            RetryMiddleware(retries=2),
            RateLimiterMiddleware(calls=3, period=1.0),
        ]
    ) as client:
        # Make concurrent requests
        tasks = [client.get("https://httpbin.org/get", params={"i": i}) for i in range(5)]

        # Wait for all requests to complete
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Print results
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Async Request {i+1}: Exception - {response}")
            else:
                print(f"Async Request {i+1}: {response.status_code}")


if __name__ == "__main__":
    print("Logging Middleware Example:")
    logging_middleware_example()

    print("\nRetry Middleware Example:")
    retry_middleware_example()

    print("\nRate Limit Middleware Example:")
    rate_limit_middleware_example()

    print("\nAsync Middleware Example:")
    asyncio.run(async_middleware_example())
