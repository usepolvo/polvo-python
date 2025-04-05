# polvo-python

Version: 1.1.0

Polvo is an open-source Python library designed to streamline the process of integrating multiple APIs into your applications. With a focus on developer experience, Polvo provides a suite of tools and abstractions that make it easy to interact with third-party services, both within and outside the context of Large Language Models (LLMs).

## Features

- **Core**: The foundation of Polvo providing shared functionality:
  - **Auth**: Flexible authentication handlers for various API protocols
  - **Clients**: Templated API clients for quick integration development
  - **Rate Limiters**: Smart strategies to manage API quotas and prevent throttling
  - **Base Tentacles**: Core components for building integrations
  - **Webhooks**: Secure webhook processing with signature validation, event handling, and an integrated server for receiving callbacks
- **Brain**: A high-level abstraction for building AI-powered applications. The Brain manages cognitive processing, memory, and communication between components.
- **Tentacles**: Ready-to-use API integrations and tools that provide a unified interface. Tentacles handle authentication, rate limiting, caching, and more.
- **LLM Tools**: Seamlessly integrate Tentacles into LLM tools, enabling AI agents to interact with external services.
- **Async Support**: Built from the ground up with asynchronous programming for optimal performance.
- **Developer Experience**: Clear abstractions, powerful utilities, and comprehensive documentation.

## Project Structure

```
usepolvo/
├── core/                       # Shared functionality
│   ├── auth/                  # Authentication handlers
│   ├── clients/               # API client templates
│   ├── rate_limiters/         # Rate limiting strategies
│   ├── tentacles/             # Base integration components
│   └── webhooks/              # Webhook processing and server
├── brain/                      # High-level LLM abstractions
└── tentacles/                  # Tools and integrations
```

## Installation

```bash
pip install usepolvo
```

## Quick Start

### 1. HubSpot Integration Example

```python
from usepolvo.tentacles.integrations.hubspot import HubSpotContactsTentacle
from usepolvo.brain import create_brain

async def main():
    # Initialize HubSpot contacts integration
    contacts = HubSpotContactsTentacle()

    # Create a new contact
    result = await contacts.execute({
        "operation": "create",
        "email": "john@example.com",
        "firstname": "John",
        "lastname": "Smith"
    })

    # Use with Brain for AI-powered operations
    brain = await create_brain(
        name="HubSpot Assistant",
        tentacles=[contacts],
        system_prompt="You are a HubSpot CRM management assistant."
    )

    response = await brain.process(
        "Create a new contact with email jane@example.com and name Jane Doe"
    )
```

### 2. Custom API Integration Example

```python
from pydantic import BaseModel, Field
from usepolvo.core.clients.rest import RESTClient
from usepolvo.core.tentacles.api import APITentacle

# Define your models
class WeatherInput(BaseModel):
    operation: str = Field(..., description="Operation: current or forecast")
    city: str = Field(..., description="City to get weather for")

class WeatherOutput(BaseModel):
    city: str
    temperature: float
    conditions: str

# Create API client
class WeatherClient(RESTClient):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.weather.com/v1"

    def get_current(self, city: str):
        return self._request("GET", f"/weather/{city}")

# Create your integration
class WeatherTentacle(APITentacle[WeatherInput, WeatherOutput]):
    def __init__(self):
        self.client = WeatherClient()
        super().__init__(self.client)

    def _setup(self) -> None:
        """Set up the weather tentacle definition."""
        self._definition = TentacleDefinition(
            name="weather",
            description="""
            Get weather information for cities.
            Available cities: San Francisco, New York, London, Tokyo.

            Operations:
            - current: Get current weather conditions
            - forecast: Get multi-day forecast
            """,
            input_schema=WeatherInput.model_json_schema(),
            output_schema=WeatherOutput.model_json_schema(),
        )

    async def execute(self, input: WeatherInput) -> WeatherOutput:
        if input.operation == "current":
            data = self.client.get_current(input.city)
            return WeatherOutput(**data)

# Usage
async def main():
    weather = WeatherTentacle()

    # Direct usage
    result = await weather({
        "operation": "current",
        "city": "San Francisco"
    })

    # Use with Brain
    brain = await create_brain(
        name="Weather Assistant",
        tentacles=[weather]
    )

    response = await brain.process(
        "What's the current weather in San Francisco?"
    )
```

## Configuration

Create a `.env` file with your API credentials:

```env
# HubSpot Configuration
POLVO_HUBSPOT_CLIENT_ID=your_client_id
POLVO_HUBSPOT_CLIENT_SECRET=your_client_secret
POLVO_HUBSPOT_REDIRECT_URI=your_redirect_uri

# Custom API Configuration
POLVO_WEATHER_API_KEY=your_api_key
```

## Documentation

For detailed documentation and examples, visit [docs.usepolvo.com](https://docs.usepolvo.com)

## License

MIT License
