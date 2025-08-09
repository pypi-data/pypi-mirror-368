"""
API key manager for the Metis Agent Framework.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from .secure_storage import SecureStorage

class APIKeyManager:
    """
    Manages API keys for various services used by the agent.
    Provides secure storage and retrieval of keys.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the API key manager.
        
        Args:
            config_dir: Directory to store configuration files. If None, uses ~/.metis_agent
        """
        if config_dir is None:
            self.config_dir = os.path.expanduser("~/.metis_agent")
        else:
            self.config_dir = config_dir
            
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Initialize secure storage
        self.secure_storage = SecureStorage(self.config_dir)
        
        # Load existing keys
        self.keys = self._load_keys()
        
    def _load_keys(self) -> Dict[str, Any]:
        """Load API keys from secure storage"""
        try:
            return self.secure_storage.load_data("api_keys") or {}
        except Exception as e:
            print(f"Warning: Could not load API keys: {e}")
            return {}
            
    def _save_keys(self):
        """Save API keys to secure storage"""
        try:
            self.secure_storage.save_data("api_keys", self.keys)
        except Exception as e:
            print(f"Warning: Could not save API keys: {e}")
            
    def set_key(self, service: str, key: str):
        """
        Set an API key for a service.
        
        Args:
            service: Service name (e.g., 'openai', 'groq', 'google')
            key: API key
        """
        self.keys[service] = key
        self._save_keys()
        
    def get_key(self, service: str) -> Optional[str]:
        """
        Get an API key for a service.
        
        Args:
            service: Service name
            
        Returns:
            API key or None if not found
        """
        # First check environment variables
        env_var = f"{service.upper()}_API_KEY"
        if env_var in os.environ:
            return os.environ[env_var]
            
        # Then check stored keys
        return self.keys.get(service)
        
    def has_key(self, service: str) -> bool:
        """
        Check if an API key exists for a service.
        
        Args:
            service: Service name
            
        Returns:
            True if key exists, False otherwise
        """
        return self.get_key(service) is not None
        
    def list_services(self) -> list:
        """
        List all services with stored API keys.
        
        Returns:
            List of service names
        """
        return list(self.keys.keys())
        
    def remove_key(self, service: str):
        """
        Remove an API key for a service.
        
        Args:
            service: Service name
        """
        if service in self.keys:
            del self.keys[service]
            self._save_keys()