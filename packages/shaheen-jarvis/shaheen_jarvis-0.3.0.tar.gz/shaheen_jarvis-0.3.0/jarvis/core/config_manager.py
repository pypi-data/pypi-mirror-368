"""
Configuration Manager for Shaheen-Jarvis framework.
Handles YAML configuration files and environment variables.
"""

import os
import yaml
from typing import Any, Optional, Dict


class ConfigManager:
    """Manages configuration from YAML files and environment variables."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. Defaults to 'jarvis_config.yaml'
        """
        self.config_path = config_path or 'jarvis_config.yaml'
        self.config_data = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error loading config file {self.config_path}: {e}")
                self.config_data = {}
        else:
            # Create default config if it doesn't exist
            self._create_default_config()
    
    def _create_default_config(self):
        """Create a default configuration file."""
        default_config = {
            'logging': {
                'level': 'INFO',
                'log_to_file': True
            },
            'voice': {
                'enable_voice': False,
                'stt_backend': 'whisper',
                'tts_backend': 'pyttsx3'
            },
            'api_keys': {
                'openai_api_key': '${OPENAI_API_KEY}',
                'weather_api_key': '${WEATHER_API_KEY}',
                'news_api_key': '${NEWS_API_KEY}'
            },
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'email_address': '${EMAIL_ADDRESS}',
                'email_password': '${EMAIL_PASSWORD}'
            },
            'plugins': {
                'auto_load': [],
                'plugin_directories': ['./jarvis/plugins']
            },
            'memory': {
                'notes_file': 'jarvis_notes.json',
                'todos_file': 'jarvis_todos.json',
                'store_context': True
            }
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            self.config_data = default_config
            print(f"Created default configuration file: {self.config_path}")
        except Exception as e:
            print(f"Error creating default config: {e}")
            self.config_data = default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key with support for nested keys.
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        # Handle environment variable substitution
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.getenv(env_var, default)
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key with support for nested keys.
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            value: Value to set
        """
        keys = key.split('.')
        data = self.config_data
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
    
    def save(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration data.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config_data.copy()
