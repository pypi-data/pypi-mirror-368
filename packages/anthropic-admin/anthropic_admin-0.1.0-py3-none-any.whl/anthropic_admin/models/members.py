"""Organization member models."""

from enum import Enum
from typing import Optional
from pydantic import Field, EmailStr

from .base import TimestampedModel


class MemberRole(str, Enum):
    """Organization member roles."""
    
    USER = "user"
    CLAUDE_CODE_USER = "claude_code_user" 
    DEVELOPER = "developer"
    BILLING = "billing"
    ADMIN = "admin"


class OrganizationMember(TimestampedModel):
    """Organization member model."""
    
    id: str = Field(..., description="Unique member identifier")
    email: EmailStr = Field(..., description="Member email address")
    role: MemberRole = Field(..., description="Member role in organization")
    name: Optional[str] = Field(None, description="Member display name")
    is_active: bool = Field(True, description="Whether member is active")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "user_12345",
                "email": "john.doe@company.com",
                "role": "developer", 
                "name": "John Doe",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z"
            }
        }
