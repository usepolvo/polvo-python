"""
Polvo v2 - Pythonic Usage Examples

This demonstrates the new pythonic API design that follows Python conventions
and provides progressive disclosure from simple to advanced use cases.
"""

import asyncio
import polvo


def simple_requests_style():
    """
    Simple usage - just like requests library.
    
    This is the 95% use case - dead simple for one-off requests.
    """
    print("=== Simple Requests-Style Usage ===")
    
    # Just like requests - no setup needed
    response = polvo.get("https://httpbin.org/get")
    print(f"GET status: {response.status_code}")
    
    # With parameters
    response = polvo.get("https://httpbin.org/get", params={"key": "value"})
    print(f"GET with params: {response.status_code}")
    
    # POST with JSON data  
    response = polvo.post(
        "https://httpbin.org/post", 
        json={"name": "John", "age": 30}
    )
    print(f"POST JSON status: {response.status_code}")
    
    # With authentication (directly in the call)
    response = polvo.get(
        "https://httpbin.org/bearer",
        auth=polvo.auth.bearer("fake_token_123")
    )
    print(f"Authenticated request: {response.status_code}")


def simple_auth_patterns():
    """
    Common authentication patterns - still simple.
    """
    print("\n=== Simple Authentication Patterns ===")
    
    # Bearer token - most common API auth
    response = polvo.get(
        "https://httpbin.org/bearer",
        auth=polvo.auth.bearer("your-bearer-token")
    )
    print(f"Bearer auth: {response.status_code}")
    
    # Basic auth
    response = polvo.get(
        "https://httpbin.org/basic-auth/user/pass",
        auth=polvo.auth.basic("user", "pass")
    )
    print(f"Basic auth: {response.status_code}")
    
    # API key in header
    response = polvo.get(
        "https://httpbin.org/get",
        auth=polvo.auth.api_key("secret123", "X-API-Key")
    )
    print(f"API key auth: {response.status_code}")


def session_for_advanced_usage():
    """
    Session for advanced usage - when you need shared configuration.
    
    This is the 5% use case - multiple requests to the same API.
    """
    print("\n=== Session for Advanced Usage ===")
    
    # Session with base URL and shared config
    with polvo.Session("https://httpbin.org") as session:
        session.auth = polvo.auth.bearer("shared-token")
        session.default_headers = {"User-Agent": "MyApp/1.0"}
        
        # All requests share the configuration
        response = session.get("/get")
        print(f"Session GET: {response.status_code}")
        
        response = session.post("/post", json={"session": True})
        print(f"Session POST: {response.status_code}")


def session_convenience_constructors():
    """
    Session convenience constructors for common patterns.
    """
    print("\n=== Session Convenience Constructors ===")
    
    # Quick session with auth
    session = polvo.Session.with_auth(
        "https://httpbin.org",
        polvo.auth.bearer("token123")
    )
    response = session.get("/bearer")
    print(f"Session with auth: {response.status_code}")
    session.close()
    
    # Quick session with retry
    session = polvo.Session.with_retry(
        "https://httpbin.org",
        max_retries=5
    )
    response = session.get("/get")
    print(f"Session with retry: {response.status_code}")
    session.close()
    
    # Quick session for API key
    session = polvo.Session.for_api(
        "https://httpbin.org",
        "my-api-key"
    )
    response = session.get("/get")
    print(f"API session: {response.status_code}")
    session.close()


def oauth2_with_explicit_storage():
    """
    OAuth2 with explicit storage configuration.
    
    No more magic - you choose exactly where tokens are stored.
    """
    print("\n=== OAuth2 with Explicit Storage ===")
    
    # Memory storage for testing
    oauth_memory = polvo.auth.oauth2(
        client_id="test_client",
        client_secret="test_secret",
        token_url="https://httpbin.org/post",  # Fake for demo
        storage=polvo.storage.memory()
    )
    print("OAuth2 with memory storage created")
    
    # Encrypted file storage for production - explicit path
    oauth_file = polvo.auth.oauth2_with_file_storage(
        client_id="prod_client",
        client_secret="prod_secret",
        token_url="https://api.example.com/oauth/token",
        token_file="~/.myapp/api-tokens.json",
        encrypt_tokens=True
    )
    print("OAuth2 with encrypted file storage created")
    
    # You can also be completely explicit
    oauth_explicit = polvo.auth.oauth2(
        client_id="explicit_client",
        client_secret="explicit_secret", 
        token_url="https://api.example.com/oauth/token",
        storage=polvo.storage.encrypted_file("~/.myapp/custom-tokens.enc")
    )
    print("OAuth2 with explicit storage created")


def production_resilience_patterns():
    """
    Production resilience patterns - but only when you need them.
    """
    print("\n=== Production Resilience Patterns ===")
    
    # Simple retry with session
    session = polvo.Session.with_retry(
        "https://httpbin.org",
        max_retries=3
    )
    
    # More advanced configuration
    retry_strategy = polvo.retry.exponential_backoff(
        max_retries=5,
        base_delay=1.0,
        max_delay=30.0
    )
    
    rate_limiter = polvo.rate_limit.adaptive(
        initial_requests_per_second=2
    )
    
    session_advanced = polvo.Session(
        "https://httpbin.org",
        retry=retry_strategy,
        rate_limit=rate_limiter,
        timeout=30.0
    )
    
    # These requests are automatically rate limited and retried
    for i in range(3):
        response = session_advanced.get("/get", params={"request": i})
        print(f"Resilient request {i}: {response.status_code}")
    
    session.close()
    session_advanced.close()


async def async_usage():
    """
    Async usage - same patterns, just async.
    """
    print("\n=== Async Usage ===")
    
    # Simple async requests work the same way
    async with polvo.AsyncSession("https://httpbin.org") as session:
        response = await session.get("/get")
        print(f"Async GET: {response.status_code}")
        
        response = await session.post("/post", json={"async": True})
        print(f"Async POST: {response.status_code}")


def show_the_tradeoffs():
    """
    Demonstrate the tradeoffs between simple and robust solutions.
    """
    print("\n=== Tradeoffs: Simple vs Robust ===")
    
    print("SIMPLE (95% of use cases):")
    print("  response = polvo.get('https://api.example.com/data')")
    print("  ✓ Dead simple")
    print("  ✓ No configuration")
    print("  ✗ No connection reuse")
    print("  ✗ No retry/rate limiting")
    
    print("\nROBUST (5% of use cases):")
    print("  session = polvo.Session.with_retry('https://api.example.com', max_retries=5)")
    print("  response = session.get('/data')")
    print("  ✓ Connection reuse") 
    print("  ✓ Retry and rate limiting")
    print("  ✓ Shared configuration")
    print("  ✗ More setup required")
    
    print("\nPRODUCTION (OAuth2 + storage + resilience):")
    print("  oauth = polvo.auth.oauth2_with_file_storage(...)")
    print("  session = polvo.Session(base_url, auth=oauth, retry=retry_strategy)")
    print("  ✓ Automatic token refresh")
    print("  ✓ Secure token storage")
    print("  ✓ Production resilience")
    print("  ✗ Requires understanding of OAuth2")


if __name__ == "__main__":
    print("Polvo v2 - Pythonic Usage Examples")
    print("=" * 50)
    
    # Run examples showing progression from simple to advanced
    simple_requests_style()
    simple_auth_patterns()
    session_for_advanced_usage()
    session_convenience_constructors()
    oauth2_with_explicit_storage()
    production_resilience_patterns()
    
    # Show async usage
    asyncio.run(async_usage())
    
    # Show the design tradeoffs
    show_the_tradeoffs()
    
    print("\n" + "=" * 50)
    print("Key Principles Demonstrated:")
    print("1. Simple things are simple (module-level functions)")
    print("2. Complex things are possible (Session + explicit config)")
    print("3. Progressive disclosure (convenience constructors)")
    print("4. Explicit over implicit (storage, auth, configuration)")
    print("5. Pythonic patterns (requests-like, context managers)") 