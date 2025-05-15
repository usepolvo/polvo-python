# core/tools/api.py
from usepolvo.core.clients.base import BaseClient
from usepolvo.core.tools.base import BaseTool, InputT, OutputT


class APITool(BaseTool[InputT, OutputT]):
    """Base class for API-based tools."""

    def __init__(self, client: BaseClient):
        self.client = client
        super().__init__()  # This will call _setup in the child class
