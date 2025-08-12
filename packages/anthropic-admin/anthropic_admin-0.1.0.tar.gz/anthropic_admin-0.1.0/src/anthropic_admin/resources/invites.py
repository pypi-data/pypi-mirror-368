"""Organization invites resource."""

from typing import List, Optional
from ..models.invites import OrganizationInvite
from ..models.members import MemberRole
from ..utils.validation import validate_email, validate_invite_id
from .base import BaseResource


class InvitesResource(BaseResource):
    """Resource for managing organization invites."""
    
    def list(self, limit: Optional[int] = None) -> List[OrganizationInvite]:
        """List organization invites.
        
        Args:
            limit: Maximum number of invites to return
            
        Returns:
            List of organization invites
        """
        params = self._build_params(limit=limit)
        response = self._http_client.get("organizations/invites", params=params)
        return self._parse_list_response(response, OrganizationInvite)
    
    def create(self, email: str, role: MemberRole) -> OrganizationInvite:
        """Create organization invite.
        
        Args:
            email: Email address to invite
            role: Role to assign when invite is accepted
            
        Returns:
            Created organization invite
        """
        validate_email(email)
        data = {
            "email": email,
            "role": role.value if isinstance(role, MemberRole) else role
        }
        response = self._http_client.post("organizations/invites", data=data)
        return self._parse_single_response(response, OrganizationInvite)
    
    def get(self, invite_id: str) -> OrganizationInvite:
        """Get a specific organization invite.
        
        Args:
            invite_id: The invite ID to retrieve
            
        Returns:
            Organization invite details
        """
        validate_invite_id(invite_id)
        response = self._http_client.get(f"organizations/invites/{invite_id}")
        return self._parse_single_response(response, OrganizationInvite)
    
    def delete(self, invite_id: str) -> None:
        """Delete organization invite.
        
        Args:
            invite_id: The invite ID to delete
        """
        validate_invite_id(invite_id)
        self._http_client.delete(f"organizations/invites/{invite_id}")
