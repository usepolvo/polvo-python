# arms/tentacles/api.py
from usepolvo.arms.clients.base import BaseClient
from usepolvo.arms.tentacles.base import BaseTentacle, InputT, OutputT


class APITentacle(BaseTentacle[InputT, OutputT]):
    """Base class for API-based tentacles."""

    def __init__(self, client: BaseClient):
        self.client = client
        super().__init__()  # This will call _setup in the child class
