import asyncio
from typing import List

from usepolvo.brain.base import create_brain
from usepolvo.brain.config import BrainConfig, ModelProvider


async def test_model(
    name: str,
    provider: ModelProvider,
    model: str,
    questions: List[str],
    tentacles=None,
    **config_kwargs,
):
    """Test a specific model configuration."""
    print(f"\n=== Testing {name} ===")

    brain_config = {
        "name": name,
        "provider": provider,
        "model": model,
        "system_prompt": f"You are {name}, an AI assistant powered by {model}.",
        **config_kwargs,
    }

    brain = await create_brain(tentacles=tentacles, **brain_config)

    for question in questions:
        print(f"\nQ: {question}")
        response = await brain.process(question)
        print(f"A: {response}")


async def main():
    """Demonstrate using different AI models."""

    # Sample questions to test with each model
    basic_questions = [
        "What is the capital of France?",
        "Write a haiku about programming.",
    ]

    # Test Anthropic Models
    await test_model(
        name="Claude Assistant",
        provider=ModelProvider.ANTHROPIC,
        model="claude-3-opus-20240229",
        questions=basic_questions,
        temperature=0.7,
    )

    # Test OpenAI Models
    await test_model(
        name="GPT Assistant",
        provider=ModelProvider.OPENAI,
        model="gpt-4-turbo-preview",
        questions=basic_questions,
        temperature=0.7,
    )


async def test_custom_config():
    """Demonstrate using custom configuration."""

    # Custom configuration for specialized use case
    config = BrainConfig(
        name="Precise Calculator",
        description="A brain specialized for mathematical calculations",
        system_prompt="You are a mathematical assistant. Always verify calculations carefully.",
        provider=ModelProvider.ANTHROPIC,
        model="claude-3-opus-20240229",
        temperature=0.1,  # Lower temperature for more deterministic responses
        max_tokens=2000,
        memory_limit=50,
        provider_config={
            "top_k": 1,
            "top_p": 0.9,
        },
    )

    brain = await create_brain(**config.model_dump())

    question = "What is the square root of 256 multiplied by 1.5?"
    print(f"\n=== Testing Custom Configuration ===")
    print(f"Q: {question}")
    response = await brain.process(question)
    print(f"A: {response}")


if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(test_custom_config())
