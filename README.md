# Polvo v2 🐙

**Production-ready HTTP client with OAuth2, rate limiting, and retries built-in**

The missing layer between `requests` and enterprise service meshes. Handle the hard parts of API integration without the complexity.

## 🚀 Quick Start

```python
import polvo

# Simple as requests
response = polvo.get('https://api.github.com/users/octocat')
print(response.json())

# With authentication
response = polvo.get(
    'https://api.example.com/users',
    auth=polvo.auth.bearer('your_token')
)

# For production workloads, use a session
with polvo.Session() as session:
    session.auth = polvo.auth.oauth2(
        client_id='your_id',
        client_secret='your_secret',
        token_url='https://auth.example.com/token'
    )
    response = session.get('https://api.example.com/protected')
```

## 🎯 Why Polvo?

**Simple things stay simple:**

```python
# Just like requests
data = polvo.get('https://api.example.com/data').json()
```

**Hard things become easy:**

```python
# OAuth2 with automatic token refresh
session = polvo.Session(
    auth=polvo.auth.OAuth2(
        flow='client_credentials',
        client_id='your_id',
        client_secret='your_secret',
        token_url='https://auth.example.com/token',
        token_cache='~/.polvo/tokens.json'  # Explicit, encrypted by default
    ),
    retry=True,  # Exponential backoff by default
    rate_limit='adaptive'  # Reads API headers automatically
)
```

## 🔐 OAuth2 Done Right

The crown jewel - production-ready OAuth2 that actually works:

```python
# Explicit token storage (encrypted by default)
oauth = polvo.auth.OAuth2(
    flow='client_credentials',
    client_id='your_id',
    client_secret='your_secret',
    token_url='https://auth.example.com/token',
    token_cache='~/.polvo/tokens.json',  # You know where tokens live
    cache_encryption=True  # Explicit choice
)

# Use it anywhere
response = polvo.get('https://api.example.com/data', auth=oauth)

# Or in a session for connection pooling
session = polvo.Session(auth=oauth)

# Multi-tenant support
session.set_tenant('customer_123')  # Switches token context
response = session.get('/tenant-specific-data')
```

## 🛡️ Production Patterns Built-In

```python
# Everything configured in one place
session = polvo.Session(
    base_url='https://api.example.com',
    auth=polvo.auth.bearer('token'),

    # Retry configuration (sensible defaults)
    retry=True,  # or retry=3 for max attempts
    retry_backoff='exponential',  # with jitter

    # Rate limiting
    rate_limit='adaptive',  # or rate_limit=10 for 10 req/s

    # Timeouts
    timeout=30,  # Same as requests

    # Circuit breaker
    circuit_breaker={'failure_threshold': 5, 'recovery_timeout': 60}
)
```

## 📦 Installation

```bash
pip install polvo

# With optional dependencies
pip install polvo[redis]  # For Redis token storage
pip install polvo[all]    # Everything
```

## 🔧 Common Patterns

### Simple One-off Requests

```python
import polvo

# GET
data = polvo.get('https://api.example.com/users').json()

# POST with JSON
response = polvo.post(
    'https://api.example.com/users',
    json={'name': 'Alice', 'email': 'alice@example.com'}
)

# With headers
response = polvo.get(
    'https://api.example.com/data',
    headers={'X-API-Key': 'secret'}
)

# Basic auth
response = polvo.get(url, auth=('username', 'password'))
```

### Production Sessions

```python
# Configure once, use everywhere
session = polvo.Session(
    base_url='https://api.example.com',
    headers={'User-Agent': 'MyApp/1.0'},
    auth=polvo.auth.bearer('token'),
    retry=True,
    rate_limit='adaptive'
)

# Clean URLs - no leading slash needed
users = session.get('users').json()
user = session.get(f'users/{user_id}').json()

# Full URL still works
response = session.get('https://other-api.com/data')
```

### Authentication Patterns

```python
# Bearer tokens (most common)
auth = polvo.auth.bearer('your_token')

# OAuth2 Client Credentials
auth = polvo.auth.OAuth2(
    flow='client_credentials',
    client_id='id',
    client_secret='secret',
    token_url='https://auth.example.com/token'
)

# OAuth2 with refresh tokens
auth = polvo.auth.OAuth2(
    flow='authorization_code',
    client_id='id',
    client_secret='secret',
    token_url='https://auth.example.com/token',
    refresh_token='your_refresh_token'
)

# API Key
auth = polvo.auth.api_key('key123', header='X-API-Key')

# Custom auth class
class CustomAuth(polvo.auth.AuthBase):
    def apply(self, request):
        request.headers['X-Custom'] = 'value'
        return request
```

### Multi-tenant SaaS

```python
# Explicit tenant management
oauth = polvo.auth.OAuth2(
    client_id='app_id',
    client_secret='app_secret',
    token_url='https://auth.example.com/token',
    token_cache='~/.polvo/tokens/{tenant}.json'  # Templated path
)

session = polvo.Session(auth=oauth)

# Switch tenants on the fly
for tenant_id in ['customer_a', 'customer_b']:
    session.set_tenant(tenant_id)
    data = session.get('data').json()
    process_tenant_data(tenant_id, data)
```

### Advanced Configuration

```python
# Fine-grained control when you need it
session = polvo.Session(
    # Retry configuration
    retry=polvo.retry.ExponentialBackoff(
        max_attempts=5,
        base_delay=1.0,
        max_delay=60.0,
        jitter=True,
        retry_on=[500, 502, 503, 504]  # Specific status codes
    ),

    # Rate limiting
    rate_limit=polvo.ratelimit.TokenBucket(
        rate=10,  # requests per second
        capacity=100  # burst capacity
    ),

    # Custom storage backend
    token_storage=polvo.storage.Redis(
        host='localhost',
        port=6379,
        prefix='myapp:tokens:'
    )
)
```

## 🏗️ Design Principles

1. **Requests compatibility**: If you know `requests`, you know `polvo`
2. **Progressive disclosure**: Simple by default, powerful when needed
3. **Explicit > Implicit**: You control where tokens are stored
4. **Production-first**: Secure defaults, observable behavior
5. **Stateless functions**: Module-level functions for simple cases

## 🔄 Migration from requests

```python
# Before (requests)
import requests
response = requests.get('https://api.example.com/data',
                       headers={'Authorization': 'Bearer token'})

# After (polvo) - it's the same!
import polvo
response = polvo.get('https://api.example.com/data',
                    auth=polvo.auth.bearer('token'))

# But now you get:
# - Automatic retries on network errors
# - Token refresh for OAuth2
# - Rate limiting protection
# - Encrypted token storage
```

## 📚 Documentation

- [Getting Started](https://docs.polvo.dev/quickstart)
- [Authentication Guide](https://docs.polvo.dev/auth)
- [API Reference](https://docs.polvo.dev/api)
- [Examples](https://docs.polvo.dev/examples)

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
