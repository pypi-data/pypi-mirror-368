"""Authentication handling for ReqNinja."""

import base64
from typing import Dict, Any, Optional
from .exceptions import AuthenticationError


class AuthHandler:
    """Handles various authentication methods."""
    
    def get_auth_headers(self, auth_config: Dict[str, Any]) -> Dict[str, str]:
        """Get authentication headers based on configuration."""
        if not auth_config:
            return {}
        
        auth_type = auth_config.get('type', '').lower()
        
        if auth_type == 'bearer':
            return self._bearer_auth(auth_config)
        elif auth_type == 'basic':
            return self._basic_auth(auth_config)
        elif auth_type == 'api_key':
            return self._api_key_auth(auth_config)
        else:
            raise AuthenticationError(f"Unsupported auth type: {auth_type}")
    
    def _bearer_auth(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Handle Bearer token authentication."""
        token = config.get('token')
        if not token:
            raise AuthenticationError("Bearer token is required")
        
        return {'Authorization': f'Bearer {token}'}
    
    def _basic_auth(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Handle Basic authentication."""
        username = config.get('username')
        password = config.get('password', '')
        
        if not username:
            raise AuthenticationError("Username is required for basic auth")
        
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {'Authorization': f'Basic {encoded_credentials}'}
    
    def _api_key_auth(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Handle API key authentication."""
        key = config.get('key')
        header_name = config.get('header', 'X-API-Key')
        
        if not key:
            raise AuthenticationError("API key is required")
        
        return {header_name: key}


def parse_auth_string(auth_string: str) -> Dict[str, Any]:
    """Parse authentication string from CLI."""
    if not auth_string:
        return {}
    
    parts = auth_string.split(' ', 1)
    if len(parts) != 2:
        raise AuthenticationError(f"Invalid auth format: {auth_string}")
    
    auth_type, credentials = parts
    auth_type = auth_type.lower()
    
    if auth_type == 'bearer':
        return {'type': 'bearer', 'token': credentials}
    elif auth_type == 'basic':
        if ':' in credentials:
            username, password = credentials.split(':', 1)
            return {'type': 'basic', 'username': username, 'password': password}
        else:
            return {'type': 'basic', 'username': credentials, 'password': ''}
    else:
        raise AuthenticationError(f"Unsupported auth type: {auth_type}")
