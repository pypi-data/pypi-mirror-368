"""Main client for Anthropic Admin SDK."""

from typing import Optional
from .utils.http import HTTPClient
from .utils.validation import validate_api_key
from .resources.members import MembersResource
from .resources.invites import InvitesResource
from .resources.workspaces import WorkspacesResource
from .resources.api_keys import ApiKeysResource


class AnthropicAdminClient:
    """Main client for Anthropic Admin API.
    
    This client provides access to all Admin API functionality including:
    - Organization member management
    - Organization invite management
    - Workspace management
    - API key management
    
    Example:
        >>> client = AnthropicAdminClient(api_key="sk-ant-admin-...")
        >>> members = client.members.list()
        >>> workspace = client.workspaces.create(name="Production")
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """Initialize Anthropic Admin client.
        
        Args:
            api_key: Admin API key (must start with 'sk-ant-admin-')
            base_url: Base URL for API requests (default: https://api.anthropic.com/v1)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
            
        Raises:
            ValidationError: If API key format is invalid
        """
        validate_api_key(api_key)
        
        self._http_client = HTTPClient(
            api_key=api_key,
            base_url=base_url or "https://api.anthropic.com/v1",
            timeout=timeout,
            max_retries=max_retries,
        )
        
        # Initialize resources
        self._members = MembersResource(self._http_client)
        self._invites = InvitesResource(self._http_client)
        self._workspaces = WorkspacesResource(self._http_client)
        self._api_keys = ApiKeysResource(self._http_client)
    
    @property
    def members(self) -> MembersResource:
        """Access organization members resource.
        
        Returns:
            MembersResource instance for managing organization members
        """
        return self._members
    
    @property
    def invites(self) -> InvitesResource:
        """Access organization invites resource.
        
        Returns:
            InvitesResource instance for managing organization invites
        """
        return self._invites
    
    @property
    def workspaces(self) -> WorkspacesResource:
        """Access workspaces resource.
        
        Returns:
            WorkspacesResource instance for managing workspaces
        """
        return self._workspaces
    
    @property
    def api_keys(self) -> ApiKeysResource:
        """Access API keys resource.
        
        Returns:
            ApiKeysResource instance for managing API keys
        """
        return self._api_keys
    
    def close(self):
        """Close the HTTP client session.
        
        Call this method when you're done using the client to clean up resources.
        """
        self._http_client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
