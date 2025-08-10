"""Configuration management for ReqNinja."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from .exceptions import ConfigError, ProfileNotFoundError


class Config:
    """Manages ReqNinja configuration including profiles and global settings."""
    
    DEFAULT_CONFIG_DIR = Path.home() / '.reqninja'
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / 'config.yml'
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_FILE
        self._config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config_data = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise ConfigError(f"Invalid YAML in config file: {e}")
            except IOError as e:
                raise ConfigError(f"Error reading config file: {e}")
        else:
            self._config_data = self._get_default_config()
            self._create_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'default_retries': 3,
            'default_timeout': 30,
            'default_headers': {
                'User-Agent': 'ReqNinja/1.0'
            },
            'retry_policy': {
                'total': 3,
                'status_forcelist': [429, 500, 502, 503, 504],
                'backoff_factor': 0.5,
                'max_backoff': 120
            },
            'profiles': {}
        }
    
    def _create_default_config(self) -> None:
        """Create default config file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config_data, f, default_flow_style=False, 
                         sort_keys=False, indent=2)
        except IOError as e:
            # Silently fail if we can't create config
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split('.')
        data = self._config_data
        
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        
        return data
    
    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """Get a specific profile configuration."""
        profiles = self.get('profiles', {})
        if profile_name not in profiles:
            raise ProfileNotFoundError(f"Profile '{profile_name}' not found")
        
        profile = profiles[profile_name].copy()
        
        # Expand environment variables in values
        profile = self._expand_env_vars(profile)
        
        return profile
    
    def _expand_env_vars(self, data: Any) -> Any:
        """Recursively expand environment variables in configuration."""
        if isinstance(data, dict):
            return {k: self._expand_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._expand_env_vars(item) for item in data]
        elif isinstance(data, str):
            return os.path.expandvars(data)
        else:
            return data
    
    def list_profiles(self) -> List[str]:
        """List available profiles."""
        return list(self.get('profiles', {}).keys())
    
    def add_profile(self, name: str, config: Dict[str, Any]) -> None:
        """Add or update a profile."""
        if 'profiles' not in self._config_data:
            self._config_data['profiles'] = {}
        
        self._config_data['profiles'][name] = config
        self._save_config()
    
    def remove_profile(self, name: str) -> None:
        """Remove a profile."""
        profiles = self._config_data.get('profiles', {})
        if name in profiles:
            del profiles[name]
            self._save_config()
        else:
            raise ProfileNotFoundError(f"Profile '{name}' not found")
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config_data, f, default_flow_style=False,
                         sort_keys=False, indent=2)
        except IOError as e:
            raise ConfigError(f"Error saving config file: {e}")
    
    def merge_profile_config(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """Merge profile configuration with defaults."""
        base_config = {
            'retries': self.get('default_retries', 3),
            'timeout': self.get('default_timeout', 30),
            'headers': self.get('default_headers', {}),
            'retry_policy': self.get('retry_policy', {})
        }
        
        if profile_name:
            profile_config = self.get_profile(profile_name)
            
            # Merge headers
            if 'headers' in profile_config:
                base_config['headers'].update(profile_config['headers'])
            
            # Override other settings
            for key in ['base_url', 'retries', 'timeout', 'auth']:
                if key in profile_config:
                    base_config[key] = profile_config[key]
            
            # Merge retry policy
            if 'retry_policy' in profile_config:
                base_config['retry_policy'].update(profile_config['retry_policy'])
        
        return base_config
