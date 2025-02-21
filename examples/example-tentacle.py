from typing import Any, Dict, Union

from pydantic import BaseModel, Field

from usepolvo.arms.tentacles import BaseTentacle, TentacleDefinition
from usepolvo.brain.base import create_brain
from usepolvo.tentacles.compute import MathInput, MathTentacle


# Sentiment Analysis Tentacle Implementation
class SentimentInput(BaseModel):
    text: str = Field(..., description="Text to analyze")
    model: str = Field("default", description="Model to use for analysis")


class SentimentOutput(BaseModel):
    sentiment: str
    confidence: float
    language: str


class MySentimentTentacle(BaseTentacle[SentimentInput, SentimentOutput]):
    """User implementation of a sentiment analysis tentacle."""

    def _setup(self) -> None:
        self._definition = TentacleDefinition(
            name="analyze_sentiment",
            description="Analyze the sentiment of text and return the emotional tone",
            input_schema=SentimentInput.model_json_schema(),
            output_schema=SentimentOutput.model_json_schema(),
        )

    async def execute(self, input: Union[SentimentInput, Dict[str, Any]]) -> SentimentOutput:
        # Convert dict to schema if needed
        if isinstance(input, dict):
            sentiment_input = SentimentInput(**input)
        else:
            sentiment_input = input

        # User's implementation of sentiment analysis
        return SentimentOutput(sentiment="positive", confidence=0.89, language="en")


# Usage example
async def example_usage():
    # Initialize tentacles
    math = MathTentacle()
    sentiment = MySentimentTentacle()

    # Use math tentacle - with schema
    math_result = await math(MathInput(operation="add", numbers="1, 2, 3, 4, 5"))
    print(f"Math Result (schema): {math_result.result}")

    # Use math tentacle - with dict
    math_result_dict = await math({"operation": "multiply", "numbers": "2, 3, 4"})
    print(f"Math Result (dict): {math_result_dict.result}")

    # Use math tentacle - with kwargs
    math_result_kwargs = await math(operation="add", numbers="10, 20, 30")
    print(f"Math Result (kwargs): {math_result_kwargs.result}")

    # Use sentiment tentacle - with schema
    sentiment_result = await sentiment(SentimentInput(text="I love this product!"))
    print(f"Sentiment (schema): {sentiment_result.sentiment}")

    # Use sentiment tentacle - with dict
    sentiment_result_dict = await sentiment({"text": "This is amazing!", "model": "default"})
    print(f"Sentiment (dict): {sentiment_result_dict.sentiment}")

    # Use brain
    brain = await create_brain(name="Smart Assistant", tentacles=[math, sentiment])
    response = await brain.process(
        "What is the sum of 5, 10, and 15, and how do people feel about math?"
    )
    print(f"Brain Response: {response}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
