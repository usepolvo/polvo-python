# test-api-examples.py
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from usepolvo.brain.base import create_brain
from usepolvo.core.clients.rest import RESTClient
from usepolvo.core.rate_limiters.simple import SimpleRateLimiter
from usepolvo.core.tools.api import APITool
from usepolvo.core.tools.base import ToolDefinition


# User defines their models
class WeatherInput(BaseModel):
    operation: str = Field(..., description="Operation to perform: current or forecast")
    city: str = Field(..., description="City to get weather for")
    days: Optional[int] = Field(5, description="Number of days for forecast")


class WeatherOutput(BaseModel):
    city: str
    temperature: Optional[float]
    conditions: str
    humidity: Optional[float]
    wind_speed: Optional[float]
    forecast: Optional[List[Dict]] = None


# User implements their client
class WeatherClient(RESTClient):
    """Weather API client for Open-Meteo."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.open-meteo.com/v1"
        self.rate_limiter = SimpleRateLimiter(requests_per_second=10)

        # User maintains their own city data
        self.city_coordinates = {
            "San Francisco": (37.7749, -122.4194),
            "New York": (40.7128, -74.0060),
            "London": (51.5074, -0.1278),
            "Tokyo": (35.6762, 139.6503),
        }

    def get_current(self, city: str) -> Dict:
        """Get current weather for a city."""
        lat, lon = self.city_coordinates.get(city, (None, None))
        if not lat:
            raise ValueError(f"City {city} not found")

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        }

        response = self._request("GET", "/forecast", params=params)
        current = response.get("current", {})

        return {
            "city": city,
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "conditions": self._get_weather_condition(
                current.get("temperature_2m", 0), current.get("wind_speed_10m", 0)
            ),
        }

    def _get_weather_condition(self, temp: float, wind: float) -> str:
        if wind > 20:
            return "windy"
        if temp < 10:
            return "cold"
        if temp > 25:
            return "hot"
        return "mild"


class WeatherTool(APITool[WeatherInput, WeatherOutput]):
    """Weather information tool."""

    def __init__(self):
        self.client = WeatherClient()
        super().__init__(self.client)  # This will call _setup

    def _setup(self) -> None:
        """Set up the weather tool definition."""
        self._definition = ToolDefinition(
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

    async def execute(self, input: Union[WeatherInput, Dict[str, Any]]) -> WeatherOutput:
        """Execute weather tool logic."""
        # Convert dict to schema if needed
        if isinstance(input, dict):
            weather_input = WeatherInput(**input)
        else:
            weather_input = input

        if weather_input.operation == "current":
            data = self.client.get_current(weather_input.city)
            return WeatherOutput(**data)
        else:
            raise ValueError(f"Invalid operation: {weather_input.operation}")


# Usage example
async def example_usage():
    # Create tool
    weather = WeatherTool()

    # 1. Using schema input
    schema_result = await weather(WeatherInput(operation="current", city="San Francisco"))
    print(f"Temperature (schema): {schema_result.temperature}°C")

    # 2. Using dict input
    dict_result = await weather({"operation": "current", "city": "New York"})
    print(f"Temperature (dict): {dict_result.temperature}°C")

    # 3. Using keyword arguments
    kwargs_result = await weather(operation="current", city="London")
    print(f"Temperature (kwargs): {kwargs_result.temperature}°C")

    # 4. Using with Brain (which will use dict/kwargs format)
    brain = await create_brain(name="Weather Assistant", tools=[weather])
    response = await brain.process("What's the current weather in Tokyo?")
    print(f"Brain response: {response}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
