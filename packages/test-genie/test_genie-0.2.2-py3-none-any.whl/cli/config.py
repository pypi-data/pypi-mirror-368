import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_DIR = Path.home() / ".testgenie"
CONFIG_FILE = CONFIG_DIR / "config.json"

class Config:
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self._config = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save(self):
        """Save configuration to file"""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
        print("Saved in Config!\n")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self._config[key] = value
        self.save()
    
    def delete(self, key: str):
        """Delete a configuration value"""
        if key in self._config:
            del self._config[key]
            self.save()
    
    @property
    def token(self) -> Optional[str]:
        """Get the authentication token"""
        return self.get('token')
    
    @property
    def email(self) -> Optional[str]:
        """Get the user email"""
        return self.get('email')
    
    @property
    def api_url(self) -> str:
        """Get the API URL"""
        return self.get('api_url', "https://testgenie-9ynz.onrender.com")

# Global config instance
config = Config() 