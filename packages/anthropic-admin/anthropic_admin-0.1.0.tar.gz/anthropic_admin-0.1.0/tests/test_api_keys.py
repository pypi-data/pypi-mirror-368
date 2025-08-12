"""Tests for ApiKeysResource."""

import pytest
from anthropic_admin.models.api_keys import ApiKey, ApiKeyStatus
from anthropic_admin.exceptions import ValidationError


class TestApiKeysResource:
    """Test cases for ApiKeysResource."""
    
    def test_list_api_keys(self, client, sample_api_key_data):
        """Test listing API keys."""
        client._http_client.get.return_value = {"data": [sample_api_key_data]}
        
        api_keys = client.api_keys.list()
        
        assert len(api_keys) == 1
        assert isinstance(api_keys[0], ApiKey)
        assert api_keys[0].name == "Production API Key"
        assert api_keys[0].status == ApiKeyStatus.ACTIVE
        
        client._http_client.get.assert_called_once_with(
            "organizations/api_keys", params={}
        )
    
    def test_list_api_keys_with_filters(self, client, sample_api_key_data):
        """Test listing API keys with filters."""
        client._http_client.get.return_value = {"data": [sample_api_key_data]}
        
        client.api_keys.list(
            limit=10,
            status=ApiKeyStatus.ACTIVE,
            workspace_id="wrkspc_12345"
        )
        
        client._http_client.get.assert_called_once_with(
            "organizations/api_keys", 
            params={
                "limit": 10,
                "status": "active",
                "workspace_id": "wrkspc_12345"
            }
        )
    
    def test_list_api_keys_string_status(self, client, sample_api_key_data):
        """Test listing API keys with string status."""
        client._http_client.get.return_value = {"data": [sample_api_key_data]}
        
        client.api_keys.list(status="inactive")
        
        client._http_client.get.assert_called_once_with(
            "organizations/api_keys", params={"status": "inactive"}
        )
    
    def test_list_api_keys_invalid_workspace_id(self, client):
        """Test listing API keys with invalid workspace ID."""
        with pytest.raises(ValidationError, match="Workspace ID must start with 'wrkspc_'"):
            client.api_keys.list(workspace_id="invalid_id")
    
    def test_get_api_key(self, client, sample_api_key_data):
        """Test getting a specific API key."""
        client._http_client.get.return_value = sample_api_key_data
        
        api_key = client.api_keys.get("key_12345")
        
        assert isinstance(api_key, ApiKey)
        assert api_key.id == "key_12345"
        assert api_key.name == "Production API Key"
        
        client._http_client.get.assert_called_once_with("organizations/api_keys/key_12345")
    
    def test_get_api_key_invalid_id(self, client):
        """Test getting API key with invalid ID format."""
        with pytest.raises(ValidationError, match="API key ID must start with 'key_'"):
            client.api_keys.get("invalid_id")
    
    def test_update_api_key(self, client, sample_api_key_data):
        """Test updating an API key."""
        updated_data = sample_api_key_data.copy()
        updated_data["name"] = "Updated Key Name"
        updated_data["status"] = "inactive"
        client._http_client.post.return_value = updated_data
        
        api_key = client.api_keys.update(
            "key_12345",
            name="Updated Key Name",
            status=ApiKeyStatus.INACTIVE
        )
        
        assert isinstance(api_key, ApiKey)
        assert api_key.name == "Updated Key Name"
        assert api_key.status == ApiKeyStatus.INACTIVE
        
        client._http_client.post.assert_called_once_with(
            "organizations/api_keys/key_12345",
            data={"name": "Updated Key Name", "status": "inactive"}
        )
    
    def test_update_api_key_partial(self, client, sample_api_key_data):
        """Test updating API key with partial data."""
        updated_data = sample_api_key_data.copy()
        updated_data["status"] = "inactive"
        client._http_client.post.return_value = updated_data
        
        api_key = client.api_keys.update("key_12345", status="inactive")
        
        client._http_client.post.assert_called_once_with(
            "organizations/api_keys/key_12345",
            data={"status": "inactive"}
        )
    
    def test_update_api_key_invalid_id(self, client):
        """Test updating API key with invalid ID."""
        with pytest.raises(ValidationError, match="API key ID must start with 'key_'"):
            client.api_keys.update("invalid_id", name="New Name")
