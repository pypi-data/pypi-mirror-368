"""Workspaces resource."""

from typing import List, Optional
from ..models.workspaces import Workspace, WorkspaceMember, WorkspaceRole
from ..utils.validation import validate_workspace_id, validate_user_id
from .base import BaseResource


class WorkspaceMembersResource(BaseResource):
    """Resource for managing workspace members."""
    
    def __init__(self, http_client, workspace_id: str):
        super().__init__(http_client)
        self.workspace_id = workspace_id
    
    def list(self, limit: Optional[int] = None) -> List[WorkspaceMember]:
        """List workspace members.
        
        Args:
            limit: Maximum number of members to return
            
        Returns:
            List of workspace members
        """
        params = self._build_params(limit=limit)
        response = self._http_client.get(
            f"organizations/workspaces/{self.workspace_id}/members",
            params=params
        )
        return self._parse_list_response(response, WorkspaceMember)
    
    def add(self, user_id: str, workspace_role: WorkspaceRole) -> WorkspaceMember:
        """Add member to workspace.
        
        Args:
            user_id: User ID to add
            workspace_role: Role to assign in workspace
            
        Returns:
            Added workspace member
        """
        validate_user_id(user_id)
        data = {
            "user_id": user_id,
            "workspace_role": workspace_role.value if isinstance(workspace_role, WorkspaceRole) else workspace_role
        }
        response = self._http_client.post(
            f"organizations/workspaces/{self.workspace_id}/members",
            data=data
        )
        return self._parse_single_response(response, WorkspaceMember)
    
    def update_role(self, user_id: str, workspace_role: WorkspaceRole) -> WorkspaceMember:
        """Update workspace member role.
        
        Args:
            user_id: User ID to update
            workspace_role: New workspace role
            
        Returns:
            Updated workspace member
        """
        validate_user_id(user_id)
        data = {
            "workspace_role": workspace_role.value if isinstance(workspace_role, WorkspaceRole) else workspace_role
        }
        response = self._http_client.post(
            f"organizations/workspaces/{self.workspace_id}/members/{user_id}",
            data=data
        )
        return self._parse_single_response(response, WorkspaceMember)
    
    def remove(self, user_id: str) -> None:
        """Remove member from workspace.
        
        Args:
            user_id: User ID to remove
        """
        validate_user_id(user_id)
        self._http_client.delete(f"organizations/workspaces/{self.workspace_id}/members/{user_id}")


class WorkspacesResource(BaseResource):
    """Resource for managing workspaces."""
    
    def list(self, limit: Optional[int] = None, include_archived: bool = False) -> List[Workspace]:
        """List workspaces.
        
        Args:
            limit: Maximum number of workspaces to return
            include_archived: Whether to include archived workspaces
            
        Returns:
            List of workspaces
        """
        params = self._build_params(limit=limit, include_archived=include_archived)
        response = self._http_client.get("organizations/workspaces", params=params)
        return self._parse_list_response(response, Workspace)
    
    def create(self, name: str, description: Optional[str] = None) -> Workspace:
        """Create workspace.
        
        Args:
            name: Workspace name
            description: Optional workspace description
            
        Returns:
            Created workspace
        """
        data = self._build_params(name=name, description=description)
        response = self._http_client.post("organizations/workspaces", data=data)
        return self._parse_single_response(response, Workspace)
    
    def get(self, workspace_id: str) -> Workspace:
        """Get a specific workspace.
        
        Args:
            workspace_id: The workspace ID to retrieve
            
        Returns:
            Workspace details
        """
        validate_workspace_id(workspace_id)
        response = self._http_client.get(f"organizations/workspaces/{workspace_id}")
        return self._parse_single_response(response, Workspace)
    
    def archive(self, workspace_id: str) -> Workspace:
        """Archive workspace.
        
        Args:
            workspace_id: Workspace ID to archive
            
        Returns:
            Archived workspace
        """
        validate_workspace_id(workspace_id)
        response = self._http_client.post(f"organizations/workspaces/{workspace_id}/archive")
        return self._parse_single_response(response, Workspace)
    
    @property
    def members(self):
        """Access workspace members for a specific workspace.
        
        Note: This returns a factory function. Call it with workspace_id to get the members resource.
        
        Example:
            members_resource = client.workspaces.members(workspace_id="wrkspc_123")
            members = members_resource.list()
        """
        def _get_members_resource(workspace_id: str) -> WorkspaceMembersResource:
            validate_workspace_id(workspace_id)
            return WorkspaceMembersResource(self._http_client, workspace_id)
        
        return _get_members_resource
