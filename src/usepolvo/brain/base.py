# brain/base.py
import os
from typing import Any, Dict, List, Optional

from usepolvo.brain.config import BrainConfig, ModelProvider
from usepolvo.brain.memory import Memory
from usepolvo.brain.synapse import Synapse
from usepolvo.core.tools import BaseTool
from usepolvo.core.tools.registry import ToolRegistry


class Brain:
    """
    Base class for AI Brains in the Polvo system.
    Manages cognitive processing, memory, and communication.
    """

    def __init__(
        self,
        config: BrainConfig,
        memory: Optional[Memory] = None,
        synapse: Optional[Synapse] = None,
        tools: Optional[ToolRegistry] = None,
    ):
        self.config = config
        # Initialize appropriate client based on provider
        self.client = self._initialize_client()
        self.memory = memory or Memory(config.memory_limit)
        self.synapse = synapse or Synapse()
        self.tools = tools or ToolRegistry()

        # Cognitive state
        self.last_plan = None
        self.last_reasoning = None

        # Register handlers
        self._setup_event_handlers()

    def _initialize_client(self) -> Any:
        """Initialize the appropriate client based on provider configuration."""
        if self.config.provider == ModelProvider.ANTHROPIC:
            from anthropic import Anthropic

            return Anthropic(api_key=os.getenv("POLVO_ANTHROPIC_API_KEY"))
        elif self.config.provider == ModelProvider.OPENAI:
            from openai import OpenAI

            return OpenAI(api_key=os.getenv("POLVO_OPENAI_API_KEY"))
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def _setup_event_handlers(self):
        """Set up default signal processors for the brain."""
        # Handle memory signals
        self.synapse.connect(signal_type="memory_update", processor=self._handle_memory_update)

        # Handle tool use signals
        self.synapse.connect(signal_type="tool_use", processor=self._handle_tool_use)

        # Handle error signals
        self.synapse.connect(signal_type="error", processor=self._handle_error)

    def _handle_memory_update(self, event: Dict[str, Any]):
        """Handle memory update events."""
        # To this:
        self.memory.store(
            content=event["content"], metadata={"type": "conversation"}, importance=0.8
        )

    async def _handle_tool_use(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool use request events."""
        if not self.config.tools_enabled:
            return {"status": "error", "error": "Tools are disabled"}

        try:
            import json

            tool = await self.tools.get_tool(event["tool_name"])
            # Parse the tool input if it's a string (OpenAI sends JSON string)
            tool_input = (
                json.loads(event["tool_input"])
                if isinstance(event["tool_input"], str)
                else event["tool_input"]
            )
            result = await tool(**tool_input)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _handle_error(self, event: Dict[str, Any]):
        """Handle error events."""
        # Log error
        print(f"Error in brain {self.config.name}: {event['error']}")

    async def process(self, input: str) -> Dict[str, Any]:
        """Process an incoming input through the brain's components."""
        try:
            # Add input to memory
            self.synapse.transmit("memory_update", {"content": {"role": "user", "content": input}})

            # Get relevant memories
            context = self.memory.recall_relevant(input)

            # Get tools if enabled
            tools = (
                await self.tools.to_provider_format(self.config.provider)
                if self.config.tools_enabled
                else []
            )

            # Build message history
            messages = [{"role": "user", "content": input}]

            # Process with appropriate model
            response = await self._process_with_provider(messages, tools)

            # Handle tool uses
            while self._has_tool_use(response):
                tool_use = self._extract_tool_use(response)
                tool_result = await self._handle_tool_use(
                    {"tool_name": tool_use["name"], "tool_input": tool_use["input"]}
                )
                messages.extend(self._format_tool_interaction(response, tool_result, tool_use))
                response = await self._process_with_provider(messages, tools)

            # Extract final response
            final_response = self._extract_final_response(response)

            # Add response to memory
            self.synapse.transmit(
                "memory_update", {"content": {"role": "assistant", "content": final_response}}
            )

            return final_response

        except Exception as e:
            self.synapse.transmit("error", {"error": str(e)})
            return {"status": "error", "error": str(e)}

    async def _process_with_provider(
        self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]
    ) -> Any:
        """Process messages using the configured provider."""
        if self.config.provider == ModelProvider.ANTHROPIC:
            return self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=messages,
                tools=tools if tools else None,
            )
        elif self.config.provider == ModelProvider.OPENAI:
            params = {
                "model": self.config.model,
                "messages": messages,
                **self.config.provider_config,
            }
            if tools:  # Only add tools if there are any
                params["tools"] = tools

            return self.client.chat.completions.create(**params)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def _has_tool_use(self, response: Any) -> bool:
        """Check if response contains tool use request."""
        if self.config.provider == ModelProvider.ANTHROPIC:
            return any(block.type == "tool_use" for block in response.content)
        elif self.config.provider == ModelProvider.OPENAI:
            return response.choices[0].message.tool_calls is not None
        # Add other provider implementations
        return False

    def _extract_tool_use(self, response: Any) -> Dict[str, Any]:
        """Extract tool use information from the response."""
        if self.config.provider == ModelProvider.ANTHROPIC:
            tool_use = next(block for block in response.content if block.type == "tool_use")
            return {
                "name": tool_use.name,
                "input": tool_use.input,
                "id": tool_use.id,  # Extract the tool_use_id
            }
        elif self.config.provider == ModelProvider.OPENAI:
            tool_use = response.choices[0].message.tool_calls[0]
            return {
                "name": tool_use.function.name,
                "input": tool_use.function.arguments,
                "id": tool_use.id,
            }
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def _format_tool_interaction(
        self, response: Any, tool_result: Any, tool_use: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Format tool interaction as a message history."""
        if self.config.provider == ModelProvider.ANTHROPIC:
            return [
                {"role": "assistant", "content": response.content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use["id"],
                            "content": str(tool_result),
                        }
                    ],
                },
            ]
        elif self.config.provider == ModelProvider.OPENAI:
            # First message is the assistant's tool call
            assistant_message = {
                "role": "assistant",
                "content": None,  # OpenAI expects null content when using tool_calls
                "tool_calls": [
                    {
                        "id": tool_use["id"],
                        "type": "function",
                        "function": {
                            "name": tool_use["name"],
                            "arguments": tool_use["input"],
                        },
                    }
                ],
            }

            # Second message is the tool response
            tool_message = {
                "role": "tool",
                "tool_call_id": tool_use["id"],
                "name": tool_use["name"],
                "content": str(tool_result),
            }

            return [assistant_message, tool_message]
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def _extract_final_response(self, response: Any) -> str:
        """Extract the final text response from the response."""
        if self.config.provider == ModelProvider.ANTHROPIC:
            return next(
                (block.text for block in response.content if hasattr(block, "text")),
                None,
            )
        elif self.config.provider == ModelProvider.OPENAI:
            message = response.choices[0].message
            # If there are tool calls, this is not the final response
            if message.tool_calls:
                return None
            # Return the actual content for final responses
            return message.content
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def cleanup(self):
        """Clean up brain resources."""
        self.memory.cleanup()
        self.synapse.cleanup()
        self.tools.cleanup()


async def create_brain(
    name: str, description: str = "", tools: List[BaseTool] = None, **kwargs
) -> Brain:
    """Create a new brain with default or custom configuration."""
    # Set tools_enabled based on whether tools were provided
    has_tools = bool(tools)

    # Remove tools_enabled from kwargs if it exists to avoid conflicts
    kwargs.pop("tools_enabled", None)

    config = BrainConfig(
        name=name,
        description=description or f"{name} - Powered by Polvo",
        system_prompt=kwargs.pop("system_prompt", f"You are {name}, an AI assistant."),
        tools_enabled=has_tools,  # Set based on tools parameter
        **kwargs,
    )

    # Set up tool registry if tools provided
    tool_registry = None
    if tools:
        tool_registry = ToolRegistry()
        for tool in tools:
            await tool_registry.register(tool)

    return Brain(config=config, tools=tool_registry)
