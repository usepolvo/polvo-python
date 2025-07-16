"""
Basic usage examples for Polvo v2.

This demonstrates the key features of the new simplified API.
"""

import asyncio
import polvo


def basic_example():
    """Simple API usage example."""
    print("=== Basic API Usage ===")
    
    # Simple usage - just like requests
    api = polvo.API("https://httpbin.org")
    
    # GET request
    response = api.get("/get", params={"key": "value"})
    print(f"GET status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # POST request
    response = api.post("/post", json={"name": "John", "age": 30})
    print(f"POST status: {response.status_code}")
    

def auth_example():
    """Authentication examples."""
    print("\n=== Authentication Examples ===")
    
    # Bearer token
    api = polvo.API("https://httpbin.org", auth=polvo.auth.bearer("fake_token"))
    response = api.get("/bearer")
    print(f"Bearer auth status: {response.status_code}")
    
    # Basic auth
    api = polvo.API("https://httpbin.org", auth=polvo.auth.basic("user", "pass"))
    response = api.get("/basic-auth/user/pass")
    print(f"Basic auth status: {response.status_code}")
    
    # API key
    api = polvo.API("https://httpbin.org", auth=polvo.auth.api_key("secret", "X-API-Key"))
    response = api.get("/get")
    print(f"API key auth status: {response.status_code}")


def oauth2_example():
    """OAuth2 with automatic token refresh example."""
    print("\n=== OAuth2 Example ===")
    
    # This would work with a real OAuth2 server
    # Using memory storage for this example
    storage = polvo.storage.memory()
    
    oauth = polvo.auth.oauth2(
        client_id="demo_client",
        client_secret="demo_secret",
        token_url="https://example.com/oauth/token",  # Fake URL for demo
        storage=storage
    )
    
    # In real usage, this would handle token refresh automatically
    api = polvo.API("https://httpbin.org", auth=oauth)
    
    # Multi-tenant usage
    tenant_a_api = api.for_tenant("tenant_a")
    tenant_b_api = api.for_tenant("tenant_b")
    
    print("OAuth2 setup complete (would work with real OAuth2 server)")
    print("Multi-tenant APIs created")


def resilience_example():
    """Production resilience patterns example."""
    print("\n=== Resilience Patterns ===")
    
    # Configure retry with exponential backoff
    retry_strategy = polvo.retry.exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=10.0
    )
    
    # Configure adaptive rate limiting
    rate_limiter = polvo.rate_limit.adaptive(initial_requests_per_second=2)
    
    # Create API with resilience patterns
    api = polvo.API(
        "https://httpbin.org",
        retry=retry_strategy,
        rate_limit=rate_limiter,
        timeout=30.0
    )
    
    # These requests will be automatically rate limited and retried on failure
    for i in range(3):
        response = api.get("/get", params={"request": i})
        print(f"Request {i}: {response.status_code}")


async def async_example():
    """Async API usage example."""
    print("\n=== Async Usage ===")
    
    async with polvo.AsyncAPI("https://httpbin.org") as api:
        # All the same methods, but async
        response = await api.get("/get")
        print(f"Async GET status: {response.status_code}")
        
        response = await api.post("/post", json={"async": True})
        print(f"Async POST status: {response.status_code}")


def storage_example():
    """Token storage examples."""
    print("\n=== Storage Examples ===")
    
    # Memory storage (for testing)
    memory_storage = polvo.storage.memory()
    print("Memory storage created")
    
    # Encrypted file storage (for production)
    file_storage = polvo.storage.encrypted_file("./demo_tokens.enc")
    print("Encrypted file storage created")
    
    # Redis storage would require Redis to be running
    # redis_storage = polvo.storage.redis(host="localhost", port=6379)
    
    # Use with OAuth2
    oauth = polvo.auth.oauth2(
        client_id="demo",
        client_secret="secret",
        token_url="https://example.com/token",
        storage=memory_storage
    )
    print("OAuth2 with custom storage configured")


if __name__ == "__main__":
    print("Polvo v2 - Basic Usage Examples")
    print("=" * 40)
    
    # Run sync examples
    basic_example()
    auth_example()
    oauth2_example()
    resilience_example()
    storage_example()
    
    # Run async example
    asyncio.run(async_example())
    
    print("\n=== Examples Complete ===")
    print("Check the code to see how each feature works!") 