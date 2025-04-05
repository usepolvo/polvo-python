# core/auth/utils/token_store.py

import json
from pathlib import Path
from typing import Dict, Optional

from cryptography.fernet import Fernet

from usepolvo.core.config import get_settings


class TokenStore:
    """Optional secure token storage utility."""

    def __init__(self, encryption_key: Optional[str] = None, storage_path: Optional[Path] = None):
        """Initialize token store."""
        self.settings = get_settings()
        self.storage_path = storage_path or Path.home() / ".usepolvo" / "tokens"

        # Create full directory path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize Fernet instance
        self.encryption_key = encryption_key or self.settings.ENCRYPTION_KEY
        if self.encryption_key:
            self.fernet = Fernet(self.encryption_key.encode())
        else:
            self.fernet = None

    def save_tokens(self, service_name: str, tokens: Dict[str, str]) -> None:
        """Save tokens for a service."""
        token_data = json.dumps(tokens).encode()

        if self.fernet:
            token_data = self.fernet.encrypt(token_data)

        token_file = self.storage_path / f"{service_name}.token"
        token_file.write_bytes(token_data)

    def load_tokens(self, service_name: str) -> Optional[Dict[str, str]]:
        """Load tokens for a service if they exist."""
        token_file = self.storage_path / f"{service_name}.token"

        if not token_file.exists():
            return None

        try:
            token_data = token_file.read_bytes()
            if self.fernet:
                token_data = self.fernet.decrypt(token_data)
            return json.loads(token_data)
        except Exception:
            return None

    def delete_tokens(self, service_name: str) -> None:
        """Delete stored tokens for a service."""
        token_file = self.storage_path / f"{service_name}.token"
        if token_file.exists():
            token_file.unlink()
