# tentacles/registry.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Type

from usepolvo.arms.tentacles.base import BaseTentacle
from usepolvo.brain.config import ModelProvider


class TentacleRegistry:
    """
    Registry for managing and accessing available tentacles.
    Handles tentacle registration, lookup, and execution.
    """

    def __init__(self):
        """Initialize an empty registry."""
        self._tentacles: Dict[str, Type[BaseTentacle]] = {}
        self._instances: Dict[str, BaseTentacle] = {}
        self._executor = ThreadPoolExecutor()

    async def register(self, tentacle: BaseTentacle) -> None:
        """
        Register a tentacle instance.

        Args:
            tentacle: The initialized tentacle instance to register
        """
        definition = tentacle.definition

        # Store both the class and the instance
        self._tentacles[definition.name] = tentacle.__class__
        self._instances[definition.name] = tentacle

    async def get_tentacle(self, name: str) -> BaseTentacle:
        """
        Get an instance of a registered tentacle.

        Args:
            name: The name of the tentacle to retrieve

        Returns:
            An instance of the requested tentacle

        Raises:
            TentacleNotFoundError: If no tentacle with the given name is registered
        """
        if name not in self._instances:
            raise Exception(f"Tentacle '{name}' not found")
        return self._instances[name]

    async def get_all_definitions(self) -> List[Dict[str, Any]]:
        """
        Get definitions for all registered tentacles.

        Returns:
            List of tentacle definitions
        """
        definitions = []
        for instance in self._instances.values():
            definitions.append(instance.definition.dict())
        return definitions

    async def to_anthropic_format(self) -> List[Dict[str, Any]]:
        """
        Get all tentacle definitions in Anthropic's format.

        Returns:
            List of tool definitions for Anthropic's API
        """
        tools = []
        for instance in self._instances.values():
            definition = instance.definition
            tools.append(
                {
                    "name": definition.name,
                    "description": definition.description,
                    "input_schema": definition.input_schema,
                }
            )
        return tools

    async def to_openai_format(self) -> List[Dict[str, Any]]:
        """
        Get all tentacle definitions in OpenAI's format.

        Returns:
            List of function definitions for OpenAI's API
        """
        functions = []
        for instance in self._instances.values():
            definition = instance.definition
            functions.append(
                {
                    "type": "function",  # Required by OpenAI
                    "function": {  # Function details must be nested
                        "name": definition.name,
                        "description": definition.description,
                        "parameters": definition.input_schema,
                    },
                }
            )
        return functions

    async def to_provider_format(self, provider: ModelProvider) -> List[Dict[str, Any]]:
        """
        Get all tentacle definitions in the specified provider's format.

        Args:
            provider: The ModelProvider enum value

        Returns:
            List of tool/function definitions in provider-specific format
        """
        if provider == ModelProvider.ANTHROPIC:
            return await self.to_anthropic_format()
        elif provider == ModelProvider.OPENAI:
            return await self.to_openai_format()
        else:
            raise ValueError(f"Unsupported provider format: {provider}")

    async def execute_tentacle(
        self, name: str, inputs: Dict[str, Any], timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute a tentacle with the given inputs.

        Args:
            name: The name of the tentacle to execute
            inputs: Input parameters for the tentacle
            timeout: Optional timeout in seconds

        Returns:
            The result of the tentacle execution

        Raises:
            TentacleNotFoundError: If the tentacle is not found
            ExecutionError: If execution fails
        """
        try:
            tentacle = await self.get_tentacle(name)

            # Handle both async and sync execute methods
            if asyncio.iscoroutinefunction(tentacle.execute):
                if timeout:
                    return await asyncio.wait_for(tentacle.execute(**inputs), timeout=timeout)
                return await tentacle.execute(**inputs)
            else:
                return tentacle.execute(**inputs)

        except Exception as e:
            raise Exception(f"Tentacle '{name}' execution failed: {str(e)}")

    async def cleanup(self):
        """Clean up resources used by the registry."""
        self._executor.shutdown(wait=True)
        self._instances.clear()
        self._tentacles.clear()

    def __len__(self) -> int:
        """Get the number of registered tentacles."""
        return len(self._instances)

    async def list_tentacles(self) -> List[str]:
        """Get a list of registered tentacle names."""
        return list(self._instances.keys())
