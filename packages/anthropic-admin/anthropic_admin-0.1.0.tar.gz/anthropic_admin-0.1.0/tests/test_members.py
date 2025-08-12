"""Tests for MembersResource."""

import pytest
from anthropic_admin.models.members import OrganizationMember, MemberRole
from anthropic_admin.exceptions import ValidationError


class TestMembersResource:
    """Test cases for MembersResource."""
    
    def test_list_members(self, client, sample_member_data):
        """Test listing organization members."""
        # Mock response
        client._http_client.get.return_value = {"data": [sample_member_data]}
        
        members = client.members.list()
        
        assert len(members) == 1
        assert isinstance(members[0], OrganizationMember)
        assert members[0].email == "john.doe@company.com"
        assert members[0].role == MemberRole.DEVELOPER
        
        client._http_client.get.assert_called_once_with(
            "organizations/users", params={}
        )
    
    def test_list_members_with_limit(self, client, sample_member_data):
        """Test listing members with limit parameter."""
        client._http_client.get.return_value = {"data": [sample_member_data]}
        
        client.members.list(limit=10)
        
        client._http_client.get.assert_called_once_with(
            "organizations/users", params={"limit": 10}
        )
    
    def test_get_member(self, client, sample_member_data):
        """Test getting a specific member."""
        client._http_client.get.return_value = sample_member_data
        
        member = client.members.get("user_12345")
        
        assert isinstance(member, OrganizationMember)
        assert member.id == "user_12345"
        assert member.email == "john.doe@company.com"
        
        client._http_client.get.assert_called_once_with("organizations/users/user_12345")
    
    def test_get_member_invalid_id(self, client):
        """Test getting member with invalid ID format."""
        with pytest.raises(ValidationError, match="User ID must start with 'user_'"):
            client.members.get("invalid_id")
    
    def test_update_member_role(self, client, sample_member_data):
        """Test updating member role."""
        updated_data = sample_member_data.copy()
        updated_data["role"] = "admin"
        client._http_client.post.return_value = updated_data
        
        member = client.members.update("user_12345", MemberRole.ADMIN)
        
        assert isinstance(member, OrganizationMember)
        assert member.role == MemberRole.ADMIN
        
        client._http_client.post.assert_called_once_with(
            "organizations/users/user_12345", data={"role": "admin"}
        )
    
    def test_update_member_role_string(self, client, sample_member_data):
        """Test updating member role with string value."""
        updated_data = sample_member_data.copy()
        updated_data["role"] = "billing"
        client._http_client.post.return_value = updated_data
        
        member = client.members.update("user_12345", "billing")
        
        assert member.role == MemberRole.BILLING
        
        client._http_client.post.assert_called_once_with(
            "organizations/users/user_12345", data={"role": "billing"}
        )
    
    def test_remove_member(self, client):
        """Test removing a member."""
        client._http_client.delete.return_value = {}
        
        client.members.remove("user_12345")
        
        client._http_client.delete.assert_called_once_with("organizations/users/user_12345")
    
    def test_remove_member_invalid_id(self, client):
        """Test removing member with invalid ID."""
        with pytest.raises(ValidationError, match="User ID must start with 'user_'"):
            client.members.remove("invalid_id")
