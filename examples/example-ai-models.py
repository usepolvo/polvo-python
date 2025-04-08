#!/usr/bin/env python3
"""
Example usage of AI model tentacles (Anthropic, OpenAI, and Google Gemini).
This demonstrates how to use each model with both:
1. The unified interface (BaseTentacle) that works across all models
2. Provider-specific APIs for specialized functionality
"""

import asyncio
import os
from typing import Any, Dict, List

from dotenv import load_dotenv

from usepolvo.tentacles.anthropic import AnthropicTentacle
from usepolvo.tentacles.base import BaseTentacle
from usepolvo.tentacles.gemini import GeminiTentacle
from usepolvo.tentacles.openai import OpenAITentacle

# Load environment variables from .env file
load_dotenv()


def extract_text(response: Dict[str, Any]) -> str:
    """Extract the response text from different AI model formats."""
    # Anthropic format
    if "content" in response and isinstance(response["content"], list):
        for item in response["content"]:
            if "text" in item:
                return item["text"]

    # OpenAI format
    if "choices" in response and len(response["choices"]) > 0:
        if "message" in response["choices"][0]:
            return response["choices"][0]["message"].get("content", "")

    # Gemini format
    if "candidates" in response and len(response["candidates"]) > 0:
        if "content" in response["candidates"][0]:
            parts = response["candidates"][0]["content"].get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"]

    # Fallback - return stringified response
    return str(response)


async def example_unified_interface():
    """Example usage of the unified interface that works with any model."""
    print("\n=== Unified Interface Example ===")
    print("This demonstrates how to use the same code with any AI model provider")

    # Initialize all models
    anthropic = AnthropicTentacle()
    openai = OpenAITentacle()
    gemini = GeminiTentacle()

    # Basic prompt with the same interface for all models
    messages = [{"role": "user", "content": "What's the capital of France?"}]
    system_message = "You are a helpful assistant that provides concise answers."

    # Run with all three models using the same exact code
    for model, name in [
        (anthropic, "Anthropic Claude"),
        (openai, "OpenAI"),
        (gemini, "Google Gemini"),
    ]:
        response = model.generate(
            messages=messages,
            system_message=system_message,
            max_tokens=100,
            temperature=0.7,
        )
        print(f"{name}: {extract_text(response)}")


async def example_anthropic():
    """Example usage of Anthropic Claude API (provider-specific)."""
    print("\n=== Anthropic Claude Provider-Specific Example ===")

    # Initialize the Anthropic tentacle
    anthropic = AnthropicTentacle()

    # Using the unified interface
    print("Using unified interface:")
    messages = [{"role": "user", "content": "Explain quantum computing in simple terms."}]
    response = anthropic.generate(messages=messages, max_tokens=500, temperature=0.7)
    print(f"Claude response: {extract_text(response)[:150]}...\n")

    # Using provider-specific APIs
    print("Using provider-specific API:")
    response = anthropic.messages.create(messages=messages, max_tokens=500, temperature=0.7)
    print(f"Claude response: {response['content'][0]['text'][:150]}...\n")

    # Streaming example using provider-specific API
    print("Streaming example (provider-specific):")
    stream = anthropic.messages.with_streaming(
        messages=[{"role": "user", "content": "Write a short poem about technology."}],
        max_tokens=300,
    )

    print("Claude streaming response:")
    for chunk in stream:
        if chunk.type == "content_block_delta" and hasattr(chunk.delta, "text"):
            print(chunk.delta.text, end="", flush=True)
    print("\n")


async def example_openai():
    """Example usage of OpenAI API (provider-specific)."""
    print("\n=== OpenAI Provider-Specific Example ===")

    # Initialize the OpenAI tentacle
    openai = OpenAITentacle()

    # Using the unified interface
    print("Using unified interface:")
    system_message = "You are a helpful assistant."
    messages = [
        {"role": "user", "content": "Explain the concept of machine learning in simple terms."}
    ]

    response = openai.generate(
        messages=messages, system_message=system_message, temperature=0.7, max_tokens=500
    )
    print(f"OpenAI response: {extract_text(response)[:150]}...\n")

    # Using provider-specific API for embeddings
    print("Using provider-specific API for embeddings:")
    text = "This is a sample text for embedding."
    embeddings = openai.embeddings.create(input=text, model="text-embedding-3-small")
    embedding_length = len(embeddings["data"][0]["embedding"])
    print(f"OpenAI embedding generated with {embedding_length} dimensions\n")


async def example_gemini():
    """Example usage of Google Gemini API (provider-specific)."""
    print("\n=== Google Gemini Provider-Specific Example ===")

    # Initialize the Gemini tentacle
    gemini = GeminiTentacle()

    # Using the unified interface
    print("Using unified interface:")
    messages = [
        {"role": "user", "content": "Explain three interesting facts about space exploration."}
    ]

    response = gemini.generate(messages=messages, max_tokens=500)
    print(f"Gemini response: {extract_text(response)[:150]}...\n")

    # Using provider-specific API with system instruction
    print("Using provider-specific API:")
    response = gemini.generation.generate_content(
        "What are the best practices for sustainable gardening?",
        system_instruction="You are a professional gardener with 20 years of experience.",
    )
    content_text = response["candidates"][0]["content"]["parts"][0]["text"]
    print(f"Gemini with system instruction: {content_text[:150]}...\n")

    # Embeddings example using provider-specific API
    print("Using provider-specific API for embeddings:")
    embedding_response = gemini.embeddings.batch_embed_contents(
        contents=["This is a sample text for embedding with Gemini."],
        task_type="RETRIEVAL_DOCUMENT",
    )

    if "embeddings" in embedding_response and embedding_response["embeddings"]:
        embedding_length = len(embedding_response["embeddings"][0].get("values", []))
        print(f"Gemini embedding generated with {embedding_length} dimensions\n")


async def main():
    """Run all examples."""
    # First demonstrate the unified interface
    await example_unified_interface()

    # Then show provider-specific examples
    await example_anthropic()
    await example_openai()
    await example_gemini()


if __name__ == "__main__":
    asyncio.run(main())
