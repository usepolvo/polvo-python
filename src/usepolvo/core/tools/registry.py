# core/tools/registry.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Type

from usepolvo.brain.config import ModelProvider
from usepolvo.core.tools.base import BaseTool


class ToolRegistry:
    """
    Registry for managing and accessing available tools.
    Handles tool registration, lookup, and execution.
    """

    def __init__(self):
        """Initialize an empty registry."""
        self._tools: Dict[str, Type[BaseTool]] = {}
        self._instances: Dict[str, BaseTool] = {}
        self._executor = ThreadPoolExecutor()

    async def register(self, tool: BaseTool) -> None:
        """
        Register a tool instance.

        Args:
            tool: The initialized tool instance to register
        """
        definition = tool.definition

        # Store both the class and the instance
        self._tools[definition.name] = tool.__class__
        self._instances[definition.name] = tool

    async def get_tool(self, name: str) -> BaseTool:
        """
        Get an instance of a registered tool.

        Args:
            name: The name of the tool to retrieve

        Returns:
            An instance of the requested tool

        Raises:
            ToolNotFoundError: If no tool with the given name is registered
        """
        if name not in self._instances:
            raise Exception(f"Tool '{name}' not found")
        return self._instances[name]

    async def get_all_definitions(self) -> List[Dict[str, Any]]:
        """
        Get definitions for all registered tools.

        Returns:
            List of tool definitions
        """
        definitions = []
        for instance in self._instances.values():
            definitions.append(instance.definition.dict())
        return definitions

    async def to_anthropic_format(self) -> List[Dict[str, Any]]:
        """
        Get all tool definitions in Anthropic's format.

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
        Get all tool definitions in OpenAI's format.

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
        Get all tool definitions in the specified provider's format.

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

    async def execute_tool(
        self, name: str, inputs: Dict[str, Any], timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool with the given inputs.

        Args:
            name: The name of the tool to execute
            inputs: Input parameters for the tool
            timeout: Optional timeout in seconds

        Returns:
            The result of the tool execution

        Raises:
            ToolNotFoundError: If the tool is not found
            ExecutionError: If execution fails
        """
        try:
            tool = await self.get_tool(name)

            # Handle both async and sync execute methods
            if asyncio.iscoroutinefunction(tool.execute):
                if timeout:
                    return await asyncio.wait_for(tool.execute(**inputs), timeout=timeout)
                return await tool.execute(**inputs)
            else:
                return tool.execute(**inputs)

        except Exception as e:
            raise Exception(f"Tool '{name}' execution failed: {str(e)}")

    async def cleanup(self):
        """Clean up resources used by the registry."""
        self._executor.shutdown(wait=True)
        self._instances.clear()
        self._tools.clear()

    def __len__(self) -> int:
        """Get the number of registered tools."""
        return len(self._instances)

    async def list_tools(self) -> List[str]:
        """Get a list of registered tool names."""
        return list(self._instances.keys())
