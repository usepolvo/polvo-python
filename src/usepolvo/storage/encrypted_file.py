"""
Encrypted file storage for tokens.

Stores tokens in an encrypted file on disk. Secure by default for production use.
"""

import json
import os
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass

from .base import TokenStorage


class EncryptedFileStorage(TokenStorage):
    """
    Encrypted file storage for tokens.
    
    Stores tokens in an encrypted file on disk using Fernet encryption.
    The encryption key is derived from a password using PBKDF2.
    
    This is the recommended storage backend for production use.
    """
    
    def __init__(self, file_path: str = "~/.polvo/tokens.enc", password: Optional[str] = None):
        """
        Initialize encrypted file storage.
        
        Args:
            file_path: Path to the encrypted file (default: ~/.polvo/tokens.enc)
            password: Encryption password (if None, will derive from system)
        """
        self.file_path = Path(file_path).expanduser()
        self.password = password or self._get_system_password()
        self._fernet = None
        
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self._init_encryption()
    
    def _get_system_password(self) -> str:
        """
        Derive a system-specific password for encryption.
        
        This creates a password based on the system and user context,
        providing reasonable security without requiring user input.
        """
        # Use system hostname + username as base
        import socket
        base = f"{socket.gethostname()}:{getpass.getuser()}:polvo-v2"
        
        # Create a hash for consistent length
        return hashlib.sha256(base.encode()).hexdigest()
    
    def _init_encryption(self):
        """Initialize the encryption cipher."""
        # Create salt based on file path for consistency
        salt = hashlib.sha256(str(self.file_path).encode()).digest()[:16]
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        self._fernet = Fernet(key)
    
    def _load_data(self) -> Dict[str, Dict[str, Any]]:
        """Load and decrypt data from file."""
        if not self.file_path.exists():
            return {}
        
        try:
            with open(self.file_path, 'rb') as f:
                encrypted_data = f.read()
            
            if not encrypted_data:
                return {}
            
            # Decrypt and parse JSON
            decrypted_data = self._fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
            
        except Exception:
            # If decryption fails, start fresh
            return {}
    
    def _save_data(self, data: Dict[str, Dict[str, Any]]):
        """Encrypt and save data to file."""
        try:
            # Convert to JSON and encrypt
            json_data = json.dumps(data, indent=2).encode()
            encrypted_data = self._fernet.encrypt(json_data)
            
            # Write to file atomically
            temp_path = self.file_path.with_suffix('.tmp')
            with open(temp_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Atomic move
            temp_path.replace(self.file_path)
            
            # Set restrictive permissions
            os.chmod(self.file_path, 0o600)
            
        except Exception as e:
            # Clean up temp file if it exists
            temp_path = self.file_path.with_suffix('.tmp')
            if temp_path.exists():
                temp_path.unlink()
            raise Exception(f"Failed to save encrypted tokens: {str(e)}")
    
    def store_token(self, key: str, token_data: Dict[str, Any]) -> None:
        """
        Store token data in encrypted file.
        
        Args:
            key: Unique key to identify the token
            token_data: Token data dictionary
        """
        data = self._load_data()
        data[key] = token_data.copy()
        self._save_data(data)
    
    def get_token(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve token data from encrypted file.
        
        Args:
            key: Unique key to identify the token
            
        Returns:
            Token data dictionary or None if not found
        """
        data = self._load_data()
        return data.get(key)
    
    def delete_token(self, key: str) -> None:
        """
        Delete token data from encrypted file.
        
        Args:
            key: Unique key to identify the token
        """
        data = self._load_data()
        if key in data:
            del data[key]
            self._save_data(data)
    
    def clear_all(self) -> None:
        """Clear all stored tokens by removing the file."""
        if self.file_path.exists():
            self.file_path.unlink()
    
    def change_password(self, new_password: str):
        """
        Change the encryption password.
        
        This will decrypt with the old password and re-encrypt with the new one.
        
        Args:
            new_password: New encryption password
        """
        # Load data with current password
        data = self._load_data()
        
        # Update password and re-initialize encryption
        self.password = new_password
        self._init_encryption()
        
        # Save data with new encryption
        self._save_data(data) 