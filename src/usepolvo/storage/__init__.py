"""
Token storage backends for Polvo v2.

Provides secure, production-ready token storage with encryption support.
Focus on simplicity and security - memory for development/testing,
encrypted file for production.
"""

from .base import TokenStorage
from .encrypted_file import EncryptedFileStorage
from .memory import MemoryStorage

# Convenience functions for common storage patterns
def encrypted_file(file_path: str = "~/.polvo/tokens.enc", password: str = None) -> EncryptedFileStorage:
    """
    Create encrypted file storage (recommended for production).
    
    Stores tokens in an encrypted file on disk. Secure by default.
    
    Args:
        file_path: Path to store the encrypted file (default: ~/.polvo/tokens.enc)
        password: Encryption password (if None, will derive from system)
        
    Returns:
        EncryptedFileStorage instance
        
    Example:
        storage = polvo.storage.encrypted_file("./my-tokens.enc")
        oauth = polvo.auth.oauth2(..., storage=storage)
    """
    return EncryptedFileStorage(file_path, password)

def memory() -> MemoryStorage:
    """
    Create in-memory storage (useful for testing and development).
    
    Tokens are stored in memory and lost when the process exits.
    NOT recommended for production use.
    
    Returns:
        MemoryStorage instance
        
    Example:
        storage = polvo.storage.memory()
        oauth = polvo.auth.oauth2(..., storage=storage)
    """
    return MemoryStorage()

__all__ = [
    "TokenStorage",
    "EncryptedFileStorage", 
    "MemoryStorage",
    "encrypted_file",
    "memory"
] 