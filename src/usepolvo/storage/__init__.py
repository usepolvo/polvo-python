"""
Token storage backends for Polvo v2.

Provides secure, production-ready token storage with encryption support.
"""

from .base import TokenStorage
from .encrypted_file import EncryptedFileStorage
from .memory import MemoryStorage
from .redis import RedisStorage

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
    Create in-memory storage (useful for testing).
    
    Tokens are stored in memory and lost when the process exits.
    
    Returns:
        MemoryStorage instance
        
    Example:
        storage = polvo.storage.memory()
        oauth = polvo.auth.oauth2(..., storage=storage)
    """
    return MemoryStorage()

def redis(host: str = "localhost", port: int = 6379, db: int = 0, **kwargs) -> RedisStorage:
    """
    Create Redis storage (recommended for production with multiple instances).
    
    Stores tokens in Redis for sharing across multiple application instances.
    
    Args:
        host: Redis host (default: localhost)
        port: Redis port (default: 6379)
        db: Redis database number (default: 0)
        **kwargs: Additional arguments passed to Redis client
        
    Returns:
        RedisStorage instance
        
    Example:
        storage = polvo.storage.redis(host="redis.example.com", port=6379)
        oauth = polvo.auth.oauth2(..., storage=storage)
    """
    return RedisStorage(host, port, db, **kwargs)

__all__ = [
    "TokenStorage",
    "EncryptedFileStorage", 
    "MemoryStorage",
    "RedisStorage",
    "encrypted_file",
    "memory",
    "redis"
] 