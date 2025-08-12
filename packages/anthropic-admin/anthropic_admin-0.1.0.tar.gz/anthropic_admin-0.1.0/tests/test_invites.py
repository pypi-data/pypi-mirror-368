"""Tests for InvitesResource."""

import pytest
from anthropic_admin.models.invites import OrganizationInvite, InviteStatus
from anthropic_admin.models.members import MemberRole
from anthropic_admin.exceptions import ValidationError


class TestInvitesResource:
    """Test cases for InvitesResource."""
    
    def test_list_invites(self, client, sample_invite_data):
        """Test listing organization invites."""
        client._http_client.get.return_value = {"data": [sample_invite_data]}
        
        invites = client.invites.list()
        
        assert len(invites) == 1
        assert isinstance(invites[0], OrganizationInvite)
        assert invites[0].email == "newdev@company.com"
        assert invites[0].status == InviteStatus.PENDING
        
        client._http_client.get.assert_called_once_with(
            "organizations/invites", params={}
        )
    
    def test_list_invites_with_limit(self, client, sample_invite_data):
        """Test listing invites with limit parameter."""
        client._http_client.get.return_value = {"data": [sample_invite_data]}
        
        client.invites.list(limit=5)
        
        client._http_client.get.assert_called_once_with(
            "organizations/invites", params={"limit": 5}
        )
    
    def test_create_invite(self, client, sample_invite_data):
        """Test creating an organization invite."""
        client._http_client.post.return_value = sample_invite_data
        
        invite = client.invites.create("newdev@company.com", MemberRole.DEVELOPER)
        
        assert isinstance(invite, OrganizationInvite)
        assert invite.email == "newdev@company.com"
        assert invite.role == MemberRole.DEVELOPER
        
        client._http_client.post.assert_called_once_with(
            "organizations/invites", 
            data={"email": "newdev@company.com", "role": "developer"}
        )
    
    def test_create_invite_string_role(self, client, sample_invite_data):
        """Test creating invite with string role."""
        client._http_client.post.return_value = sample_invite_data
        
        invite = client.invites.create("user@company.com", "claude_code_user")
        
        client._http_client.post.assert_called_once_with(
            "organizations/invites",
            data={"email": "user@company.com", "role": "claude_code_user"}
        )
    
    def test_create_invite_invalid_email(self, client):
        """Test creating invite with invalid email."""
        with pytest.raises(ValidationError, match="Invalid email format"):
            client.invites.create("invalid-email", MemberRole.DEVELOPER)
    
    def test_create_invite_empty_email(self, client):
        """Test creating invite with empty email."""
        with pytest.raises(ValidationError, match="Email cannot be empty"):
            client.invites.create("", MemberRole.DEVELOPER)
    
    def test_get_invite(self, client, sample_invite_data):
        """Test getting a specific invite."""
        client._http_client.get.return_value = sample_invite_data
        
        invite = client.invites.get("invite_67890")
        
        assert isinstance(invite, OrganizationInvite)
        assert invite.id == "invite_67890"
        assert invite.email == "newdev@company.com"
        
        client._http_client.get.assert_called_once_with("organizations/invites/invite_67890")
    
    def test_get_invite_invalid_id(self, client):
        """Test getting invite with invalid ID format."""
        with pytest.raises(ValidationError, match="Invite ID must start with 'invite_'"):
            client.invites.get("invalid_id")
    
    def test_delete_invite(self, client):
        """Test deleting an invite."""
        client._http_client.delete.return_value = {}
        
        client.invites.delete("invite_67890")
        
        client._http_client.delete.assert_called_once_with("organizations/invites/invite_67890")
    
    def test_delete_invite_invalid_id(self, client):
        """Test deleting invite with invalid ID."""
        with pytest.raises(ValidationError, match="Invite ID must start with 'invite_'"):
            client.invites.delete("invalid_id")
