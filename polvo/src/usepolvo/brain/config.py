from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ModelProvider(Enum):
    """Supported AI model providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class BrainConfig(BaseModel):
    """Configuration for a Brain."""

    name: str
    description: str
    system_prompt: str
    provider: ModelProvider = ModelProvider.ANTHROPIC
    model: str = "claude-3-opus-20240229"
    max_tokens: int = 4096
    temperature: float = 0.7
    memory_limit: int = 100
    provider_config: Dict[str, Any] = {}
    tentacles_enabled: Optional[bool] = None
