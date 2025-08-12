"""
Secure storage for sensitive data like API keys.
"""

import os
import json
import base64
from typing import Dict, Any, Optional
from pathlib import Path
import hashlib

class SecureStorage:
    """
    Provides secure storage for sensitive data like API keys.
    Uses simple encryption for basic security.
    """
    
    def __init__(self, storage_dir: str):
        """
        Initialize secure storage.
        
        Args:
            storage_dir: Directory to store encrypted data
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        # Create or load encryption key
        self.key = self._get_encryption_key()
        
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = os.path.join(self.storage_dir, ".key")
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            # Generate a new key
            import secrets
            key = secrets.token_bytes(32)
            
            # Save the key
            with open(key_file, "wb") as f:
                f.write(key)
                
            return key
            
    def _encrypt(self, data: str) -> str:
        """Simple encryption for data"""
        if not data:
            return ""
            
        # Use XOR encryption with key cycling
        data_bytes = data.encode('utf-8')
        key_bytes = self.key
        encrypted = bytearray()
        
        for i, b in enumerate(data_bytes):
            key_byte = key_bytes[i % len(key_bytes)]
            encrypted.append(b ^ key_byte)
            
        return base64.b64encode(encrypted).decode('utf-8')
        
    def _decrypt(self, encrypted_data: str) -> str:
        """Simple decryption for data"""
        if not encrypted_data:
            return ""
            
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            key_bytes = self.key
            decrypted = bytearray()
            
            for i, b in enumerate(encrypted_bytes):
                key_byte = key_bytes[i % len(key_bytes)]
                decrypted.append(b ^ key_byte)
                
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return ""
            
    def save_data(self, name: str, data: Any):
        """
        Save data securely.
        
        Args:
            name: Data identifier
            data: Data to save (will be JSON serialized)
        """
        # Convert data to JSON
        json_data = json.dumps(data)
        
        # Encrypt the data
        encrypted_data = self._encrypt(json_data)
        
        # Save to file
        file_path = os.path.join(self.storage_dir, f"{name}.enc")
        with open(file_path, "w") as f:
            f.write(encrypted_data)
            
    def load_data(self, name: str) -> Optional[Any]:
        """
        Load data securely.
        
        Args:
            name: Data identifier
            
        Returns:
            Loaded data or None if not found
        """
        file_path = os.path.join(self.storage_dir, f"{name}.enc")
        
        if not os.path.exists(file_path):
            return None
            
        # Read encrypted data
        with open(file_path, "r") as f:
            encrypted_data = f.read()
            
        # Decrypt the data
        json_data = self._decrypt(encrypted_data)
        
        if not json_data:
            return None
            
        # Parse JSON
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            return None