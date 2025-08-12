"""Organization members resource."""

from typing import List, Optional
from ..models.members import OrganizationMember, MemberRole
from ..utils.validation import validate_user_id
from .base import BaseResource


class MembersResource(BaseResource):
    """Resource for managing organization members."""
    
    def list(self, limit: Optional[int] = None) -> List[OrganizationMember]:
        """List organization members.
        
        Args:
            limit: Maximum number of members to return
            
        Returns:
            List of organization members
        """
        params = self._build_params(limit=limit)
        response = self._http_client.get("organizations/users", params=params)
        return self._parse_list_response(response, OrganizationMember)
    
    def get(self, user_id: str) -> OrganizationMember:
        """Get a specific organization member.
        
        Args:
            user_id: The user ID to retrieve
            
        Returns:
            Organization member details
        """
        validate_user_id(user_id)
        response = self._http_client.get(f"organizations/users/{user_id}")
        return self._parse_single_response(response, OrganizationMember)
    
    def update(self, user_id: str, role: MemberRole) -> OrganizationMember:
        """Update organization member role.
        
        Args:
            user_id: The user ID to update
            role: New role to assign
            
        Returns:
            Updated organization member
        """
        validate_user_id(user_id)
        data = {"role": role.value if isinstance(role, MemberRole) else role}
        response = self._http_client.post(f"organizations/users/{user_id}", data=data)
        return self._parse_single_response(response, OrganizationMember)
    
    def remove(self, user_id: str) -> None:
        """Remove member from organization.
        
        Args:
            user_id: The user ID to remove
        """
        validate_user_id(user_id)
        self._http_client.delete(f"organizations/users/{user_id}")
