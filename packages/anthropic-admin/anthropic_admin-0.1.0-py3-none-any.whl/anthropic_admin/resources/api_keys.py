"""API keys resource."""

from typing import List, Optional
from ..models.api_keys import ApiKey, ApiKeyStatus
from ..utils.validation import validate_api_key_id, validate_workspace_id
from .base import BaseResource


class ApiKeysResource(BaseResource):
    """Resource for managing API keys."""
    
    def list(
        self,
        limit: Optional[int] = None,
        status: Optional[ApiKeyStatus] = None,
        workspace_id: Optional[str] = None,
    ) -> List[ApiKey]:
        """List API keys.
        
        Args:
            limit: Maximum number of API keys to return
            status: Filter by API key status
            workspace_id: Filter by workspace ID
            
        Returns:
            List of API keys
        """
        if workspace_id:
            validate_workspace_id(workspace_id)
        
        params = self._build_params(
            limit=limit,
            status=status.value if isinstance(status, ApiKeyStatus) else status,
            workspace_id=workspace_id,
        )
        response = self._http_client.get("organizations/api_keys", params=params)
        return self._parse_list_response(response, ApiKey)
    
    def get(self, api_key_id: str) -> ApiKey:
        """Get a specific API key.
        
        Args:
            api_key_id: The API key ID to retrieve
            
        Returns:
            API key details
        """
        validate_api_key_id(api_key_id)
        response = self._http_client.get(f"organizations/api_keys/{api_key_id}")
        return self._parse_single_response(response, ApiKey)
    
    def update(
        self,
        api_key_id: str,
        name: Optional[str] = None,
        status: Optional[ApiKeyStatus] = None,
    ) -> ApiKey:
        """Update API key.
        
        Args:
            api_key_id: API key ID to update
            name: New name for the API key
            status: New status for the API key
            
        Returns:
            Updated API key
        """
        validate_api_key_id(api_key_id)
        data = self._build_params(
            name=name,
            status=status.value if isinstance(status, ApiKeyStatus) else status,
        )
        response = self._http_client.post(f"organizations/api_keys/{api_key_id}", data=data)
        return self._parse_single_response(response, ApiKey)
