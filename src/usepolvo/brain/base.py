# brain/base.py
import os
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from pydantic import BaseModel

from usepolvo.arms.tentacles import BaseTentacle
from usepolvo.brain.memory import Memory
from usepolvo.brain.synapse import Synapse
from usepolvo.tentacles.registry import TentacleRegistry


class BrainConfig(BaseModel):
    """Configuration for a Brain."""

    name: str
    description: str
    system_prompt: str
    model: str = "claude-3-opus-20240229"
    max_tokens: int = 4096
    temperature: float = 0.7
    memory_limit: int = 100
    tentacles_enabled: bool = True


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
        tentacles: Optional[TentacleRegistry] = None,
    ):
        self.config = config
        self.client = Anthropic(api_key=os.getenv("POLVO_CLAUDE_API_KEY"))
        self.memory = memory or Memory(config.memory_limit)
        self.synapse = synapse or Synapse()
        self.tentacles = tentacles or TentacleRegistry()

        # Cognitive state
        self.last_plan = None
        self.last_reasoning = None

        # Register handlers
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Set up default signal processors for the brain."""
        # Handle memory signals
        self.synapse.connect(signal_type="memory_update", processor=self._handle_memory_update)

        # Handle tentacle use signals
        self.synapse.connect(signal_type="tentacle_use", processor=self._handle_tool_use)

        # Handle error signals
        self.synapse.connect(signal_type="error", processor=self._handle_error)

    def _handle_memory_update(self, event: Dict[str, Any]):
        """Handle memory update events."""
        # To this:
        self.memory.store(
            content=event["content"], metadata={"type": "conversation"}, importance=0.8
        )

    async def _handle_tool_use(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tentacle use request events."""
        if not self.config.tentacles_enabled:
            return {"status": "error", "error": "Tentacles are disabled"}

        try:
            tentacle = await self.tentacles.get_tentacle(event["tool_name"])
            result = await tentacle(**event["tool_input"])
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
                await self.tentacles.to_anthropic_format() if self.config.tentacles_enabled else []
            )

            # Build message history
            messages = [{"role": "user", "content": input}]

            # Process with Claude
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=messages,
                tools=tools,
            )

            # Handle multiple tool uses in sequence
            while any(block.type == "tool_use" for block in response.content):
                tool_use = next(block for block in response.content if block.type == "tool_use")

                # Execute the tool
                tool_result = await self._handle_tool_use(
                    {"tool_name": tool_use.name, "tool_input": tool_use.input}
                )

                # Add the interaction to message history
                messages.extend(
                    [
                        {"role": "assistant", "content": response.content},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use.id,
                                    "content": str(tool_result),
                                }
                            ],
                        },
                    ]
                )

                # Let Claude process tool result and potentially request more tools
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    messages=messages,
                    tools=tools,
                )

            # Extract the final text response
            final_response = next(
                (block.text for block in response.content if hasattr(block, "text")),
                None,
            )

            # Add response to memory
            self.synapse.transmit(
                "memory_update", {"content": {"role": "assistant", "content": final_response}}
            )

            return final_response

        except Exception as e:
            self.synapse.transmit("error", {"error": str(e)})
            return {"status": "error", "error": str(e)}

    def cleanup(self):
        """Clean up brain resources."""
        self.memory.cleanup()
        self.synapse.cleanup()
        self.tentacles.cleanup()


async def create_brain(
    name: str, description: str = "", tentacles: List[BaseTentacle] = None, **kwargs
) -> Brain:
    """Create a new brain with default or custom configuration."""
    config = BrainConfig(
        name=name,
        description=description or f"{name} - Powered by Polvo",
        system_prompt=kwargs.pop("system_prompt", f"You are {name}, an AI assistant."),
        tentacles_enabled=bool(tentacles),
        **kwargs,
    )

    # Set up tentacle registry if tentacles provided
    tentacle_registry = None
    if tentacles:
        tentacle_registry = TentacleRegistry()
        for tentacle in tentacles:
            await tentacle_registry.register(tentacle)

    return Brain(config=config, tentacles=tentacle_registry)


# Example usage:
"""
# Create brain configuration
config = BrainConfig(
    name="Support Brain",
    description="Customer support brain with access to documentation and ticketing",
    system_prompt="You are a helpful customer support assistant..."
)

# Initialize brain
brain = Brain(config)

# Add tentacles (tentacles)
brain.tentacles.register(DocumentationTool())
brain.tentacles.register(TicketingTool())

# Process input
response = brain.process("I'm having trouble with login")

# Clean up
brain.cleanup()

# Or use the factory function
support_brain = create_brain(
    name="Support Brain",
    tentacles=[DocumentationTool(), TicketingTool()],
    system_prompt="You are a helpful customer support assistant..."
)
"""
