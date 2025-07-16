# Polvo v2 🐙

**Simple, production-ready API client**

A requests-like library that handles the hard parts of API integration:

- OAuth2 with automatic token refresh and multi-tenant support
- Smart rate limiting and retry with exponential backoff
- Secure token storage with encryption
- Circuit breaker for cascading failure prevention

## 🚀 Quick Start

```python
import polvo

# Simple usage
api = polvo.API("https://api.example.com")
response = api.get("/users")
print(response.json())

# With authentication
api = polvo.API("https://api.example.com", auth=polvo.auth.bearer("your_token"))

# Multi-tenant OAuth2 (the crown jewel)
oauth = polvo.auth.oauth2(
    client_id="your_client_id",
    client_secret="your_secret",
    token_url="https://api.example.com/oauth/token"
)
api = polvo.API("https://api.example.com", auth=oauth)

# For different tenants
tenant_api = api.for_tenant("tenant_123")
```

## 🎯 Key Features

### 🔐 **OAuth2Flow** - The Crown Jewel

Handles complex OAuth2 flows transparently with automatic token refresh and multi-tenant support:

```python
# Set up once, use everywhere
oauth = polvo.auth.oauth2(
    client_id="your_client_id",
    client_secret="your_secret",
    token_url="https://api.example.com/oauth/token",
    scope="read write"
)

# Automatically handles token refresh
api = polvo.API("https://api.example.com", auth=oauth)

# Multi-tenant support
tenant_a_api = api.for_tenant("tenant_a")
tenant_b_api = api.for_tenant("tenant_b")  # Different tokens automatically
```

### 🛡️ **Production-Ready Resilience**

Built-in patterns that prevent production incidents:

```python
# Exponential backoff with jitter
retry_strategy = polvo.retry.exponential_backoff(max_retries=5)

# Adaptive rate limiting (reads API headers)
rate_limiter = polvo.rate_limit.adaptive()

# Circuit breaker prevents cascading failures
from polvo.resilience import CircuitBreaker
circuit_breaker = CircuitBreaker(failure_threshold=5)

api = polvo.API(
    "https://api.example.com",
    retry=retry_strategy,
    rate_limit=rate_limiter,
    circuit_breaker=circuit_breaker
)
```

### 🔒 **Secure Token Storage**

Multiple storage backends with encryption:

```python
# Encrypted file storage (default)
storage = polvo.storage.encrypted_file("~/.polvo/tokens.enc")

# Redis for multiple instances
storage = polvo.storage.redis(host="redis.example.com")

# Memory for testing
storage = polvo.storage.memory()

oauth = polvo.auth.oauth2(..., storage=storage)
```

## 📦 Installation

```bash
pip install polvo

# With Redis support
pip install polvo[redis]
```

## 🔧 Configuration Examples

### Basic API Client

```python
import polvo

# Simple requests-like interface
api = polvo.API("https://api.example.com")

# All standard HTTP methods
response = api.get("/users", params={"page": 1})
response = api.post("/users", json={"name": "John"})
response = api.put("/users/123", json={"name": "Jane"})
response = api.delete("/users/123")
```

### Authentication Strategies

```python
# Bearer token
auth = polvo.auth.bearer("your_token")

# Basic auth
auth = polvo.auth.basic("username", "password")

# API key
auth = polvo.auth.api_key("your_key", header_name="X-API-Key")

# OAuth2 (recommended for production)
auth = polvo.auth.oauth2(
    client_id="your_client_id",
    client_secret="your_secret",
    token_url="https://api.example.com/oauth/token"
)
```

### Rate Limiting Strategies

```python
# Fixed rate limit
rate_limiter = polvo.rate_limit.fixed(requests_per_second=10)

# Adaptive (reads API headers)
rate_limiter = polvo.rate_limit.adaptive(initial_requests_per_second=5)

# Conservative for strict APIs
rate_limiter = polvo.rate_limit.conservative(requests_per_second=1)

# Burst traffic
rate_limiter = polvo.rate_limit.burst(requests_per_second=5, burst_size=20)
```

### Retry Strategies

```python
# Exponential backoff (recommended)
retry = polvo.retry.exponential_backoff(max_retries=5)

# Linear backoff
retry = polvo.retry.linear_backoff(max_retries=3, delay=2.0)

# Immediate retry
retry = polvo.retry.immediate(max_retries=2)
```

## 🏗️ Architecture

Polvo v2 is designed around **progressive disclosure**:

- **Simple cases are simple**: `polvo.API("url").get("/endpoint")`
- **Complex cases are possible**: Full control over auth, retry, rate limiting
- **No magic**: Clear, understandable behavior
- **Single entry point**: `polvo.API()` - no hunting for the right class

### Core Components

1. **API**: Main client with requests-like interface
2. **Auth**: Authentication strategies (Bearer, OAuth2, etc.)
3. **Storage**: Token storage backends (encrypted file, Redis, memory)
4. **Resilience**: Retry, rate limiting, circuit breaker patterns

## 🆚 Migration from Polvo v1

Polvo v2 replaces the complex Brain/Tentacles architecture with a simple, familiar interface:

```python
# v1 (complex)
from usepolvo.brain import create_brain
from usepolvo.tentacles.integrations.api import APITentacle

brain = await create_brain(name="API Assistant", tentacles=[tentacle])
response = await brain.process("Make API call")

# v2 (simple)
import polvo

api = polvo.API("https://api.example.com", auth=polvo.auth.bearer("token"))
response = api.get("/endpoint")
```

## 🔍 Why Polvo v2?

We built Polvo v2 because existing solutions either:

- Are too simple (basic requests wrapper)
- Are too complex (enterprise service mesh)
- Don't handle real production problems (OAuth refresh, rate limiting, multi-tenancy)

Polvo v2 focuses on the patterns that cause **real pain in production**:

1. OAuth2 token refresh across multiple tenants
2. Smart rate limiting that adapts to API responses
3. Retry with proper backoff and jitter
4. Secure token storage and management
5. Circuit breakers for cascading failure prevention

## 📚 Documentation

- [Full Documentation](https://docs.usepolvo.com)
- [API Reference](https://docs.usepolvo.com/api)
- [Migration Guide](https://docs.usepolvo.com/migration)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
