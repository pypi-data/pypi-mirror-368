"""Test cases for ReqNinja client functionality."""

import pytest
import json
from unittest.mock import patch, Mock

from reqninja import get, post, ReqNinjaClient
from reqninja.exceptions import ReqNinjaError, InvalidURLError


class TestReqNinjaClient:
    """Test the main ReqNinja client."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = ReqNinjaClient()
        assert client is not None
        assert client.session is not None
        assert client.config is not None
    
    def test_prepare_url_absolute(self):
        """Test URL preparation with absolute URL."""
        client = ReqNinjaClient()
        url = client._prepare_url("https://example.com/api")
        assert url == "https://example.com/api"
    
    def test_prepare_url_with_base(self):
        """Test URL preparation with base URL."""
        client = ReqNinjaClient()
        url = client._prepare_url("/users", "https://api.example.com")
        assert url == "https://api.example.com/users"
    
    def test_prepare_url_localhost(self):
        """Test URL preparation defaulting to localhost."""
        client = ReqNinjaClient()
        url = client._prepare_url("/api/users")
        assert url == "http://localhost/api/users"
    
    def test_prepare_url_invalid(self):
        """Test URL preparation with invalid URL."""
        client = ReqNinjaClient()
        with pytest.raises(InvalidURLError):
            client._prepare_url("invalid-url")
    
    @patch('requests.Session.request')
    def test_request_success(self, mock_request):
        """Test successful request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.text = '{"result": "success"}'
        mock_request.return_value = mock_response
        
        client = ReqNinjaClient()
        response = client.get("https://example.com/api")
        
        assert response is not None
        assert response.status_code == 200
        assert hasattr(response, 'elapsed_ms')
    
    @patch('requests.Session.request')
    def test_request_with_headers(self, mock_request):
        """Test request with custom headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        client = ReqNinjaClient()
        headers = {'Custom-Header': 'test-value'}
        client.get("https://example.com/api", headers=headers)
        
        # Verify headers were passed
        call_kwargs = mock_request.call_args[1]
        assert 'Custom-Header' in call_kwargs['headers']
        assert call_kwargs['headers']['Custom-Header'] == 'test-value'
    
    @patch('requests.Session.request')
    def test_request_with_auth(self, mock_request):
        """Test request with authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        client = ReqNinjaClient()
        auth = {'type': 'bearer', 'token': 'test-token'}
        client.get("https://example.com/api", auth=auth)
        
        # Verify auth header was added
        call_kwargs = mock_request.call_args[1]
        assert 'Authorization' in call_kwargs['headers']
        assert call_kwargs['headers']['Authorization'] == 'Bearer test-token'
    
    @patch('requests.Session.request')
    def test_request_failure(self, mock_request):
        """Test request failure handling."""
        from requests.exceptions import ConnectionError
        mock_request.side_effect = ConnectionError("Connection failed")
        
        client = ReqNinjaClient()
        with pytest.raises(ReqNinjaError):
            client.get("https://example.com/api")


class TestModuleFunctions:
    """Test module-level convenience functions."""
    
    @patch('reqninja.client._default_client.get')
    def test_get_function(self, mock_get):
        """Test get convenience function."""
        mock_response = Mock()
        mock_get.return_value = mock_response
        
        response = get("https://example.com/api")
        
        mock_get.assert_called_once_with("https://example.com/api")
        assert response == mock_response
    
    @patch('reqninja.client._default_client.post')
    def test_post_function(self, mock_post):
        """Test post convenience function."""
        mock_response = Mock()
        mock_post.return_value = mock_response
        
        data = {"key": "value"}
        response = post("https://example.com/api", json=data)
        
        mock_post.assert_called_once_with("https://example.com/api", json=data)
        assert response == mock_response


class TestHTTPMethods:
    """Test all HTTP methods."""
    
    @patch('requests.Session.request')
    def test_all_methods(self, mock_request):
        """Test all HTTP methods work."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        client = ReqNinjaClient()
        url = "https://example.com/api"
        
        # Test all methods
        methods = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']
        for method in methods:
            method_func = getattr(client, method)
            response = method_func(url)
            assert response.status_code == 200
            
            # Verify correct method was called
            assert mock_request.call_args[0][0].upper() == method.upper()
