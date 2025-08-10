"""Main HTTP client for ReqNinja with enhanced features."""

import time
import json
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config
from .response import ReqNinjaResponse
from .exceptions import ReqNinjaError, InvalidURLError, RetryError
from .auth import AuthHandler


class ReqNinjaClient:
    """Enhanced HTTP client with retry logic, timing, and configuration."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.session = requests.Session()
        self.auth_handler = AuthHandler()
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Setup session with retry policy and adapters."""
        retry_policy = self.config.get('retry_policy', {})
        
        retry_strategy = Retry(
            total=retry_policy.get('total', 3),
            status_forcelist=retry_policy.get('status_forcelist', [429, 500, 502, 503, 504]),
            backoff_factor=retry_policy.get('backoff_factor', 0.5),
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def request(
        self,
        method: str,
        url: str,
        profile: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retries: Optional[int] = None,
        **kwargs
    ) -> ReqNinjaResponse:
        """Make an HTTP request with enhanced features."""
        
        # Merge configuration
        config = self.config.merge_profile_config(profile)
        
        # Prepare URL
        final_url = self._prepare_url(url, config.get('base_url'))
        
        # Prepare headers
        final_headers = config.get('headers', {}).copy()
        if headers:
            final_headers.update(headers)
        
        # Setup authentication
        if auth or config.get('auth'):
            auth_config = auth or config.get('auth')
            final_headers.update(self.auth_handler.get_auth_headers(auth_config))
        
        # Setup timeout and retries
        final_timeout = timeout or config.get('timeout', 30)
        
        # Prepare request kwargs
        request_kwargs = {
            'headers': final_headers,
            'timeout': final_timeout,
            **kwargs
        }
        
        # Make the request with timing
        start_time = time.time()
        try:
            response = self.session.request(method, final_url, **request_kwargs)
        except requests.exceptions.RequestException as e:
            raise ReqNinjaError(f"Request failed: {e}")
        
        end_time = time.time()
        
        # Check for HTTP errors
        if response.status_code >= 400:
            # Don't raise by default, let user handle
            pass
        
        return ReqNinjaResponse(response, start_time, end_time)
    
    def _prepare_url(self, url: str, base_url: Optional[str] = None) -> str:
        """Prepare the final URL, handling relative paths and base URLs."""
        if not url:
            raise InvalidURLError("URL cannot be empty")
        
        # If URL is already absolute, return as-is
        parsed = urlparse(url)
        if parsed.scheme:
            return url
        
        # If we have a base URL, join them
        if base_url:
            return urljoin(base_url.rstrip('/') + '/', url.lstrip('/'))
        
        # If URL starts with /, assume localhost
        if url.startswith('/'):
            return f"http://localhost{url}"
        
        raise InvalidURLError(f"Invalid URL: {url}. Provide absolute URL or set base_url in profile")
    
    def get(self, url: str, **kwargs) -> ReqNinjaResponse:
        """Make a GET request."""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> ReqNinjaResponse:
        """Make a POST request."""
        return self.request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> ReqNinjaResponse:
        """Make a PUT request."""
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> ReqNinjaResponse:
        """Make a DELETE request."""
        return self.request('DELETE', url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> ReqNinjaResponse:
        """Make a PATCH request."""
        return self.request('PATCH', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> ReqNinjaResponse:
        """Make a HEAD request."""
        return self.request('HEAD', url, **kwargs)
    
    def options(self, url: str, **kwargs) -> ReqNinjaResponse:
        """Make an OPTIONS request."""
        return self.request('OPTIONS', url, **kwargs)


# Global client instance
_default_client = ReqNinjaClient()


def request(method: str, url: str, **kwargs) -> ReqNinjaResponse:
    """Make an HTTP request using the default client."""
    return _default_client.request(method, url, **kwargs)


def get(url: str, **kwargs) -> ReqNinjaResponse:
    """Make a GET request using the default client."""
    return _default_client.get(url, **kwargs)


def post(url: str, **kwargs) -> ReqNinjaResponse:
    """Make a POST request using the default client."""
    return _default_client.post(url, **kwargs)


def put(url: str, **kwargs) -> ReqNinjaResponse:
    """Make a PUT request using the default client."""
    return _default_client.put(url, **kwargs)


def delete(url: str, **kwargs) -> ReqNinjaResponse:
    """Make a DELETE request using the default client."""
    return _default_client.delete(url, **kwargs)


def patch(url: str, **kwargs) -> ReqNinjaResponse:
    """Make a PATCH request using the default client."""
    return _default_client.patch(url, **kwargs)


def head(url: str, **kwargs) -> ReqNinjaResponse:
    """Make a HEAD request using the default client."""
    return _default_client.head(url, **kwargs)


def options(url: str, **kwargs) -> ReqNinjaResponse:
    """Make an OPTIONS request using the default client."""
    return _default_client.options(url, **kwargs)
