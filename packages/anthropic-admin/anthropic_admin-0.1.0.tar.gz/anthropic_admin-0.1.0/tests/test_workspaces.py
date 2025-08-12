"""Tests for WorkspacesResource."""

import pytest
from anthropic_admin.models.workspaces import Workspace, WorkspaceMember, WorkspaceRole
from anthropic_admin.exceptions import ValidationError


class TestWorkspacesResource:
    """Test cases for WorkspacesResource."""
    
    def test_list_workspaces(self, client, sample_workspace_data):
        """Test listing workspaces."""
        client._http_client.get.return_value = {"data": [sample_workspace_data]}
        
        workspaces = client.workspaces.list()
        
        assert len(workspaces) == 1
        assert isinstance(workspaces[0], Workspace)
        assert workspaces[0].name == "Production"
        assert not workspaces[0].is_archived
        
        client._http_client.get.assert_called_once_with(
            "organizations/workspaces", params={"include_archived": False}
        )
    
    def test_list_workspaces_with_archived(self, client, sample_workspace_data):
        """Test listing workspaces including archived."""
        client._http_client.get.return_value = {"data": [sample_workspace_data]}
        
        client.workspaces.list(include_archived=True, limit=5)
        
        client._http_client.get.assert_called_once_with(
            "organizations/workspaces", params={"include_archived": True, "limit": 5}
        )
    
    def test_create_workspace(self, client, sample_workspace_data):
        """Test creating a workspace."""
        client._http_client.post.return_value = sample_workspace_data
        
        workspace = client.workspaces.create("Production", "Prod environment")
        
        assert isinstance(workspace, Workspace)
        assert workspace.name == "Production"
        assert workspace.description == "Production environment workspace"
        
        client._http_client.post.assert_called_once_with(
            "organizations/workspaces", 
            data={"name": "Production", "description": "Prod environment"}
        )
    
    def test_create_workspace_minimal(self, client, sample_workspace_data):
        """Test creating workspace with minimal data."""
        client._http_client.post.return_value = sample_workspace_data
        
        workspace = client.workspaces.create("Test Workspace")
        
        client._http_client.post.assert_called_once_with(
            "organizations/workspaces", 
            data={"name": "Test Workspace"}
        )
    
    def test_get_workspace(self, client, sample_workspace_data):
        """Test getting a specific workspace."""
        client._http_client.get.return_value = sample_workspace_data
        
        workspace = client.workspaces.get("wrkspc_12345")
        
        assert isinstance(workspace, Workspace)
        assert workspace.id == "wrkspc_12345"
        
        client._http_client.get.assert_called_once_with("organizations/workspaces/wrkspc_12345")
    
    def test_get_workspace_invalid_id(self, client):
        """Test getting workspace with invalid ID."""
        with pytest.raises(ValidationError, match="Workspace ID must start with 'wrkspc_'"):
            client.workspaces.get("invalid_id")
    
    def test_archive_workspace(self, client, sample_workspace_data):
        """Test archiving a workspace."""
        archived_data = sample_workspace_data.copy()
        archived_data["is_archived"] = True
        client._http_client.post.return_value = archived_data
        
        workspace = client.workspaces.archive("wrkspc_12345")
        
        assert workspace.is_archived
        
        client._http_client.post.assert_called_once_with(
            "organizations/workspaces/wrkspc_12345/archive"
        )


class TestWorkspaceMembersResource:
    """Test cases for WorkspaceMembersResource."""
    
    def test_workspace_members_factory(self, client):
        """Test workspace members factory method."""
        members_resource = client.workspaces.members("wrkspc_12345")
        
        assert members_resource is not None
        assert members_resource.workspace_id == "wrkspc_12345"
    
    def test_workspace_members_invalid_id(self, client):
        """Test workspace members with invalid workspace ID."""
        with pytest.raises(ValidationError, match="Workspace ID must start with 'wrkspc_'"):
            client.workspaces.members("invalid_id")
    
    def test_list_workspace_members(self, client):
        """Test listing workspace members."""
        sample_member_data = {
            "user_id": "user_67890",
            "workspace_id": "wrkspc_12345", 
            "workspace_role": "workspace_developer",
            "user_email": "dev@company.com",
            "user_name": "Jane Developer",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-20T14:45:00Z"
        }
        
        client._http_client.get.return_value = {"data": [sample_member_data]}
        
        members_resource = client.workspaces.members("wrkspc_12345")
        members = members_resource.list()
        
        assert len(members) == 1
        assert isinstance(members[0], WorkspaceMember)
        assert members[0].user_email == "dev@company.com"
        assert members[0].workspace_role == WorkspaceRole.WORKSPACE_DEVELOPER
        
        client._http_client.get.assert_called_once_with(
            "organizations/workspaces/wrkspc_12345/members", params={}
        )
    
    def test_add_workspace_member(self, client):
        """Test adding member to workspace."""
        sample_member_data = {
            "user_id": "user_123",
            "workspace_id": "wrkspc_12345",
            "workspace_role": "workspace_admin",
            "user_email": "admin@company.com",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        client._http_client.post.return_value = sample_member_data
        
        members_resource = client.workspaces.members("wrkspc_12345")
        member = members_resource.add("user_123", WorkspaceRole.WORKSPACE_ADMIN)
        
        assert isinstance(member, WorkspaceMember)
        assert member.workspace_role == WorkspaceRole.WORKSPACE_ADMIN
        
        client._http_client.post.assert_called_once_with(
            "organizations/workspaces/wrkspc_12345/members",
            data={"user_id": "user_123", "workspace_role": "workspace_admin"}
        )
    
    def test_update_workspace_member_role(self, client):
        """Test updating workspace member role."""
        sample_member_data = {
            "user_id": "user_123",
            "workspace_id": "wrkspc_12345",
            "workspace_role": "workspace_admin",
            "user_email": "member@company.com",
            "updated_at": "2024-01-20T14:45:00Z"
        }
        
        client._http_client.post.return_value = sample_member_data
        
        members_resource = client.workspaces.members("wrkspc_12345")
        member = members_resource.update_role("user_123", WorkspaceRole.WORKSPACE_ADMIN)
        
        assert member.workspace_role == WorkspaceRole.WORKSPACE_ADMIN
        
        client._http_client.post.assert_called_once_with(
            "organizations/workspaces/wrkspc_12345/members/user_123",
            data={"workspace_role": "workspace_admin"}
        )
    
    def test_remove_workspace_member(self, client):
        """Test removing member from workspace."""
        client._http_client.delete.return_value = {}
        
        members_resource = client.workspaces.members("wrkspc_12345")
        members_resource.remove("user_123")
        
        client._http_client.delete.assert_called_once_with(
            "organizations/workspaces/wrkspc_12345/members/user_123"
        )
