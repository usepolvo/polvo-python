# polvo-python

Version: 1.0.0

Polvo is an open-source Python library designed to streamline the process of integrating multiple APIs into your applications. With a focus on developer experience, Polvo provides a suite of tools and abstractions that make it easy to interact with third-party services, both within and outside the context of Large Language Models (LLMs).

## Features

- **Brain**: A high-level abstraction for building AI-powered applications. The Brain manages cognitive processing, memory, and communication between components.
- **Tentacles**: A unified interface for API integrations. Tentacles handle authentication, rate limiting, caching, and more.
- **LLM Tools**: Seamlessly integrate Tentacles into LLM tools, enabling AI agents to interact with external services.
- **Async Support**: Built from the ground up with asynchronous programming for optimal performance.
- **Developer Experience**: Clear abstractions, powerful utilities, and comprehensive documentation.

## Project Structure

```
usepolvo/
├── arms/                       # Shared functionality
│   ├── auth/                  # Authentication handlers
│   ├── clients/               # API client templates
│   ├── rate_limiters/         # Rate limiting strategies
│   └── tentacles/             # Base integration components
├── brain/                      # High-level LLM abstractions
├── ink/                        # Utilities and helpers
└── tentacles/                  # Tools and integrations
```

## Installation

```bash
pip install usepolvo
```

## Quick Start

### Define Your Models

```python
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class ContactInput(BaseModel):
    operation: str
    email: Optional[EmailStr]

class ContactOutput(BaseModel):
    id: str
    properties: Dict[str, Any]
```

### Create Your Integration

```python
from usepolvo.tentacles import APITentacle
from usepolvo.tentacles.integration import HubSpotClient

class HubSpotContactsTentacle(APITentacle[ContactInput, ContactOutput]):
    def __init__(self):
        self.client = HubSpotClient()
        super().__init__(self.client)

    async def execute(self, input: ContactInput) -> ContactOutput:
        # Implement your integration logic
        pass
```

### Use with Brain or Standalone

```python
# With Brain
from usepolvo.brain import create_brain

brain = await create_brain(tentacles=[HubSpotContactsTentacle()])
response = await brain.process("Create a new contact for john@example.com")

# Standalone
tentacle = HubSpotContactsTentacle()
result = await tentacle(ContactInput(operation="create", email="john@example.com"))
```

## Configuration

Create a `.env` file:

```env
POLVO_HUBSPOT_CLIENT_ID=your_hubspot_client_id
POLVO_HUBSPOT_CLIENT_SECRET=your_hubspot_client_secret
POLVO_HUBSPOT_REDIRECT_URI=your_hubspot_redirect_uri
```

## Documentation

For detailed documentation and examples, visit [docs.usepolvo.com](https://docs.usepolvo.com)

## License

MIT License
