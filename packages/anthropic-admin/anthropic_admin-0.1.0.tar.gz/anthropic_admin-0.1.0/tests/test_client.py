"""Tests for AnthropicAdminClient."""

import pytest
from unittest.mock import patch
from anthropic_admin import AnthropicAdminClient
from anthropic_admin.exceptions import ValidationError


class TestAnthropicAdminClient:
    """Test cases for AnthropicAdminClient."""
    
    def test_client_initialization_with_valid_key(self, sample_api_key):
        """Test client initialization with valid admin API key."""
        with patch('anthropic_admin.client.HTTPClient'):
            client = AnthropicAdminClient(api_key=sample_api_key)
            assert client is not None
    
    def test_client_initialization_with_invalid_key(self):
        """Test client initialization fails with invalid API key."""
        with pytest.raises(ValidationError, match="Invalid admin API key format"):
            AnthropicAdminClient(api_key="sk-ant-api-invalid")
    
    def test_client_initialization_with_empty_key(self):
        """Test client initialization fails with empty API key."""
        with pytest.raises(ValidationError, match="API key cannot be empty"):
            AnthropicAdminClient(api_key="")
    
    def test_client_has_resources(self, client):
        """Test that client has all required resources."""
        assert hasattr(client, 'members')
        assert hasattr(client, 'invites')
        assert hasattr(client, 'workspaces')
        assert hasattr(client, 'api_keys')
    
    def test_client_context_manager(self, sample_api_key):
        """Test client as context manager."""
        with patch('anthropic_admin.client.HTTPClient') as mock_http_class:
            mock_http_client = mock_http_class.return_value
            
            with AnthropicAdminClient(api_key=sample_api_key) as client:
                assert client is not None
            
            # Verify close was called
            mock_http_client.close.assert_called_once()
    
    def test_client_close_method(self, client):
        """Test client close method."""
        client.close()
        client._http_client.close.assert_called_once()
    
    def test_client_custom_base_url(self, sample_api_key):
        """Test client with custom base URL."""
        custom_url = "https://custom.api.com/v1"
        
        with patch('anthropic_admin.client.HTTPClient') as mock_http_class:
            AnthropicAdminClient(api_key=sample_api_key, base_url=custom_url)
            
            # Verify HTTPClient was initialized with custom URL
            mock_http_class.assert_called_once()
            args, kwargs = mock_http_class.call_args
            assert kwargs['base_url'] == custom_url
    
    def test_client_custom_timeout(self, sample_api_key):
        """Test client with custom timeout."""
        custom_timeout = 60
        
        with patch('anthropic_admin.client.HTTPClient') as mock_http_class:
            AnthropicAdminClient(api_key=sample_api_key, timeout=custom_timeout)
            
            # Verify HTTPClient was initialized with custom timeout
            mock_http_class.assert_called_once()
            args, kwargs = mock_http_class.call_args
            assert kwargs['timeout'] == custom_timeout
