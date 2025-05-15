# Polvo Core - A requests-style SDK for APIs

Polvo-Core is a Python library providing a simple, ergonomic interface for interacting with various API protocols (REST, GraphQL, SOAP) while maintaining the familiar feel of the Python 'requests' library.

## Features

- **Simple, Pythonic API**: Easy to use with sensible defaults, inspired by the popular `requests` library
- **Protocol Adapters**: Support for multiple API protocols with a consistent interface
- **Authentication**: Built-in support for common authentication methods (Basic, Bearer, API Key, OAuth2)
- **Middleware**: Extensible middleware system for customizing request/response processing
- **Sync and Async Support**: Use the same API for both synchronous and asynchronous code
- **Strong Typing**: Full type annotations for better IDE support and static analysis
- **Resilient by Default**: Strict timeouts, connection verification, and error handling

## Installation

```bash
pip install usepolvo-core
```

## Quick Start

### Basic Usage

```python
import usepolvo_core as pv

# Create a client
client = pv.Client()

# Make a GET request
response = client.get("https://api.example.com/users", params={"page": 1})
print(response.json())

# Make a POST request with JSON data
response = client.post(
    "https://api.example.com/users",
    json={"name": "John Doe", "email": "john@example.com"}
)
print(f"Status: {response.status_code}")
```

### Async Support

```python
import asyncio
import usepolvo_core as pv

async def main():
    async with pv.AsyncClient() as client:
        response = await client.get("https://api.example.com/users")
        print(response.json())

asyncio.run(main())
```

### Authentication

```python
import usepolvo_core as pv
from usepolvo_core.auth import BearerAuth

# Create a client with token authentication
client = pv.Client(
    base_url="https://api.example.com",
    auth=BearerAuth(token="your_access_token")
)

# All requests will include the Authorization header
response = client.get("/users/me")
```

### Middleware

```python
import usepolvo_core as pv
from usepolvo_core.middleware import RetryMiddleware, LoggingMiddleware

# Create a client with middleware
client = pv.Client(
    middlewares=[
        RetryMiddleware(retries=3),
        LoggingMiddleware()
    ]
)

# Requests will automatically retry on failure and be logged
response = client.get("https://api.example.com/data")
```

### Resource Pattern for REST APIs

```python
import usepolvo_core as pv

# Create a REST client
client = pv.RestClient(base_url="https://api.example.com")

# Create a resource
users = client.resource("users")

# Get all users
all_users = users.get()

# Get a specific user
user = users(123).get()

# Create a user
new_user = users.post(json={"name": "Jane Doe"})

# Update a user
updated_user = users(123).put(json={"name": "Jane Smith"})

# Delete a user
users(123).delete()
```

## Documentation

For more detailed documentation, see the [examples](./examples) directory.

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/usepolvo/usepolvo-core.git
cd usepolvo-core

# Install development dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

## License

MIT

## Credits

Developed and maintained by the Polvo team.
