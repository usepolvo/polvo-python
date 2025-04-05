#!/usr/bin/env python3
"""
Example usage of AI model tentacles (Anthropic, OpenAI, and Google Gemini).
This demonstrates how to use each model with their respective APIs.
"""

import asyncio
import os
from typing import Any, Dict, List

from dotenv import load_dotenv

from usepolvo.tentacles.anthropic import AnthropicTentacle
from usepolvo.tentacles.gemini import GeminiTentacle
from usepolvo.tentacles.openai import OpenAITentacle

# Load environment variables from .env file
load_dotenv()


async def example_anthropic():
    """Example usage of Anthropic Claude API."""
    print("\n=== Anthropic Claude Example ===")

    # Initialize the Anthropic tentacle
    # API key can be provided explicitly or via POLVO_ANTHROPIC_API_KEY env var
    anthropic = AnthropicTentacle()

    # Basic message creation
    messages = [{"role": "user", "content": "Explain quantum computing in simple terms."}]

    response = anthropic.messages.create(messages=messages, max_tokens=500, temperature=0.7)

    print(f"Claude response: {response['content'][0]['text'][:150]}...\n")

    # With system instructions
    system_prompt = (
        "You are a helpful AI assistant that specializes in explaining complex topics to children."
    )

    response = anthropic.messages.create(
        messages=[{"role": "user", "content": "What is photosynthesis?"}],
        system=system_prompt,
        max_tokens=500,
    )

    print(f"Claude with system prompt: {response['content'][0]['text'][:150]}...\n")

    # Streaming example (commented out as it requires special handling)
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
    """Example usage of OpenAI API."""
    print("\n=== OpenAI Example ===")

    # Initialize the OpenAI tentacle
    # API key can be provided explicitly or via POLVO_OPENAI_API_KEY env var
    openai = OpenAITentacle()

    # Chat completion
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the concept of machine learning in simple terms."},
    ]

    response = openai.chat.create(messages=messages, temperature=0.7, max_tokens=500)

    print(f"OpenAI chat response: {response['choices'][0]['message']['content'][:150]}...\n")

    # Embeddings example
    text = "This is a sample text for embedding."

    embeddings = openai.embeddings.create(input=text, model="text-embedding-3-small")

    embedding_length = len(embeddings["data"][0]["embedding"])
    print(f"OpenAI embedding generated with {embedding_length} dimensions\n")


async def example_gemini():
    """Example usage of Google Gemini API."""
    print("\n=== Google Gemini Example ===")

    # Initialize the Gemini tentacle
    # API key can be provided explicitly or via POLVO_GEMINI_API_KEY env var
    gemini = GeminiTentacle()

    # Simple text generation
    response = gemini.generation.generate_content(
        "Explain three interesting facts about space exploration."
    )

    print(f"Gemini response: {response['candidates'][0]['content']['parts'][0]['text'][:150]}...\n")

    # With system instruction
    response = gemini.generation.generate_content(
        "What are the best practices for sustainable gardening?",
        system_instruction="You are a professional gardener with 20 years of experience.",
    )

    print(
        f"Gemini with system instruction: {response['candidates'][0]['content']['parts'][0]['text'][:150]}...\n"
    )

    # Embeddings example
    embedding_response = gemini.embeddings.batch_embed_contents(
        contents=["This is a sample text for embedding with Gemini."],
        task_type="RETRIEVAL_DOCUMENT",
    )

    if "embeddings" in embedding_response and embedding_response["embeddings"]:
        embedding_length = len(embedding_response["embeddings"][0].get("values", []))
        print(f"Gemini embedding generated with {embedding_length} dimensions\n")


async def main():
    """Run all examples."""
    await example_anthropic()
    await example_openai()
    await example_gemini()


if __name__ == "__main__":
    asyncio.run(main())
