# core/tools/base.py
from abc import abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar, Union

from pydantic import BaseModel


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class BaseTool(Generic[InputT, OutputT]):
    """Base class for all tools."""

    def __init__(self):
        self._definition: Optional[ToolDefinition] = None
        self._setup()

        if not self._definition:
            raise ValueError("Tool definition not set")

    @abstractmethod
    def _setup(self) -> None:
        """Set up tool definition."""
        raise NotImplementedError("Must implement _setup")

    @abstractmethod
    async def execute(self, input: Union[InputT, Dict[str, Any]]) -> OutputT:
        """Execute core tool logic."""
        raise NotImplementedError("Must implement execute")

    async def __call__(self, *args, **kwargs) -> OutputT:
        """Make tool callable, handling both dict and schema inputs."""
        # Handle different input scenarios
        if len(args) == 1 and isinstance(args[0], BaseModel):
            # Input is already a schema: WeatherTool(WeatherInput(...))
            input_data = args[0]
        elif len(args) == 1 and isinstance(args[0], dict):
            # Input is a dict: WeatherTool({"operation": "current", ...})
            input_data = args[0]
        elif kwargs:
            # Input is keyword arguments: WeatherTool(operation="current", ...)
            input_data = kwargs
        else:
            raise ValueError("Invalid input format")

        return await self.execute(input_data)

    @property
    def definition(self) -> ToolDefinition:
        """Get the tool definition."""
        if not self._definition:
            raise ValueError("Tool definition not set")
        return self._definition
