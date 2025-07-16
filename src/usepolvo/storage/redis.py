"""
Redis storage for tokens.

Stores tokens in Redis for sharing across multiple application instances.
Recommended for production deployments with multiple servers.
"""

import json
from typing import Dict, Any, Optional

from .base import TokenStorage

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisStorage(TokenStorage):
    """
    Redis storage for tokens.
    
    Stores tokens in Redis, allowing them to be shared across multiple
    application instances. This is ideal for production deployments
    where you have multiple servers or containers.
    
    Requires the 'redis' package: pip install redis
    """
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 6379, 
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "polvo:tokens:",
        **kwargs
    ):
        """
        Initialize Redis storage.
        
        Args:
            host: Redis host (default: localhost)
            port: Redis port (default: 6379)
            db: Redis database number (default: 0)
            password: Redis password (optional)
            prefix: Key prefix for token storage (default: polvo:tokens:)
            **kwargs: Additional arguments passed to Redis client
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis storage requires the 'redis' package. "
                "Install it with: pip install redis"
            )
        
        self.prefix = prefix
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,  # Automatically decode responses to strings
            **kwargs
        )
        
        # Test connection
        try:
            self.client.ping()
        except Exception as e:
            raise Exception(f"Failed to connect to Redis: {str(e)}")
    
    def _get_key(self, key: str) -> str:
        """Get the full Redis key with prefix."""
        return f"{self.prefix}{key}"
    
    def store_token(self, key: str, token_data: Dict[str, Any]) -> None:
        """
        Store token data in Redis.
        
        Args:
            key: Unique key to identify the token
            token_data: Token data dictionary
        """
        redis_key = self._get_key(key)
        json_data = json.dumps(token_data)
        
        # Store with optional TTL based on expires_in
        expires_in = token_data.get('expires_in')
        if expires_in and isinstance(expires_in, (int, float)):
            # Set TTL to expires_in + 10% buffer
            ttl = int(expires_in * 1.1)
            self.client.setex(redis_key, ttl, json_data)
        else:
            self.client.set(redis_key, json_data)
    
    def get_token(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve token data from Redis.
        
        Args:
            key: Unique key to identify the token
            
        Returns:
            Token data dictionary or None if not found
        """
        redis_key = self._get_key(key)
        json_data = self.client.get(redis_key)
        
        if json_data is None:
            return None
        
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            # If data is corrupted, delete it
            self.client.delete(redis_key)
            return None
    
    def delete_token(self, key: str) -> None:
        """
        Delete token data from Redis.
        
        Args:
            key: Unique key to identify the token
        """
        redis_key = self._get_key(key)
        self.client.delete(redis_key)
    
    def clear_all(self) -> None:
        """
        Clear all stored tokens from Redis.
        
        This deletes all keys matching the prefix pattern.
        """
        pattern = f"{self.prefix}*"
        keys = self.client.keys(pattern)
        
        if keys:
            self.client.delete(*keys)
    
    def get_all_keys(self) -> list:
        """
        Get all token keys (without prefix).
        
        Returns:
            List of token keys
        """
        pattern = f"{self.prefix}*"
        keys = self.client.keys(pattern)
        
        # Remove prefix from keys
        prefix_len = len(self.prefix)
        return [key[prefix_len:] for key in keys]
    
    def get_ttl(self, key: str) -> int:
        """
        Get the time-to-live for a token in seconds.
        
        Args:
            key: Unique key to identify the token
            
        Returns:
            TTL in seconds, -1 if key exists but has no TTL, -2 if key doesn't exist
        """
        redis_key = self._get_key(key)
        return self.client.ttl(redis_key)
    
    def extend_ttl(self, key: str, ttl: int) -> bool:
        """
        Extend the TTL for a token.
        
        Args:
            key: Unique key to identify the token
            ttl: New TTL in seconds
            
        Returns:
            True if successful, False if key doesn't exist
        """
        redis_key = self._get_key(key)
        return self.client.expire(redis_key, ttl) 