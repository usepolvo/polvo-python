# brain/utils.py
from functools import wraps
from typing import Any, Callable, List, Type, TypeVar

from usepolvo.brain.base import Brain, BrainConfig

T = TypeVar("T")


def with_brain(
    name: str, tools: List[Type[Any]] = None, **config
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that provides a Brain instance to the decorated function.

    Args:
        name: Name of the brain
        tools: List of tools/tentacles to register
        **config: Additional brain configuration
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            brain_config = BrainConfig(
                name=name,
                description=config.pop("description", f"{name} - Powered by Polvo"),
                system_prompt=config.pop("system_prompt", f"You are {name}, an AI assistant."),
                tools_enabled=bool(tools),
                **config,
            )

            brain = Brain(config=brain_config, tools=tools)
            try:
                return func(brain, *args, **kwargs)
            finally:
                brain.cleanup()

        return wrapper

    return decorator


def store_in_memory(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that automatically stores function results in brain's memory.

    Args:
        func: Function whose results should be stored
    """

    @wraps(func)
    def wrapper(brain: Brain, *args, **kwargs) -> T:
        result = func(brain, *args, **kwargs)
        brain.memory.store(
            content={"function": func.__name__, "args": args, "kwargs": kwargs, "result": result},
            metadata={"type": "function_call"},
            importance=0.8,  # High importance for function results
        )
        return result

    return wrapper


class BrainContext:
    """
    Context manager for using Brain instances.
    Ensures proper initialization and cleanup of brain resources.
    """

    def __init__(self, name: str, tools: List[Type[Any]] = None, **config):
        """
        Initialize brain context.

        Args:
            name: Name of the brain
            tools: List of tools/tentacles to register
            **config: Additional brain configuration
        """
        self.config = BrainConfig(
            name=name,
            description=config.pop("description", f"{name} - Powered by Polvo"),
            system_prompt=config.pop("system_prompt", f"You are {name}, an AI assistant."),
            tools_enabled=bool(tools),
            **config,
        )
        self.tools = tools
        self.brain = None

    def __aenter__(self) -> Brain:
        """Set up and return brain instance."""
        self.brain = Brain(config=self.config, tools=self.tools)
        return self.brain

    def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up brain resources."""
        if self.brain:
            self.brain.cleanup()


# Example usage:
"""
# Using the brain decorator
@with_brain("Research Assistant", tools=[SearchTool(), CalculatorTool()])
def analyze_data(brain: Brain, data: Dict[str, Any]):
    result = brain.process(f"Analyze this data: {data}")
    return result

# Using the memory storage decorator
@store_in_memory
def calculate_metrics(brain: Brain, numbers: List[float]):
    result = sum(numbers) / len(numbers)
    return result

# Using the context manager
with BrainContext("Data Processor", tools=[ProcessingTool()]) as brain:
    result =  brain.process("Process the dataset")
"""
