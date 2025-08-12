"""Organization invite models."""

from enum import Enum
from typing import Optional
from pydantic import Field, EmailStr

from .base import TimestampedModel
from .members import MemberRole


class InviteStatus(str, Enum):
    """Organization invite status."""
    
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class OrganizationInvite(TimestampedModel):
    """Organization invite model."""
    
    id: str = Field(..., description="Unique invite identifier")
    email: EmailStr = Field(..., description="Invitee email address")
    role: MemberRole = Field(..., description="Role to assign when invite is accepted")
    status: InviteStatus = Field(InviteStatus.PENDING, description="Current invite status")
    invited_by: Optional[str] = Field(None, description="ID of user who created invite")
    expires_at: Optional[str] = Field(None, description="Invite expiration timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "invite_67890",
                "email": "newdev@company.com",
                "role": "developer",
                "status": "pending",
                "invited_by": "user_12345", 
                "expires_at": "2024-02-15T10:30:00Z",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
