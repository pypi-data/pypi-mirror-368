"""Workspace models."""

from enum import Enum
from typing import Optional
from pydantic import Field

from .base import TimestampedModel


class WorkspaceRole(str, Enum):
    """Workspace member roles."""
    
    WORKSPACE_USER = "workspace_user"
    WORKSPACE_DEVELOPER = "workspace_developer"
    WORKSPACE_ADMIN = "workspace_admin"


class Workspace(TimestampedModel):
    """Workspace model."""
    
    id: str = Field(..., description="Unique workspace identifier")
    name: str = Field(..., description="Workspace name")
    is_archived: bool = Field(False, description="Whether workspace is archived")
    description: Optional[str] = Field(None, description="Workspace description")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "wrkspc_12345",
                "name": "Production",
                "is_archived": False,
                "description": "Production environment workspace",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z"
            }
        }


class WorkspaceMember(TimestampedModel):
    """Workspace member model."""
    
    user_id: str = Field(..., description="User identifier")
    workspace_id: str = Field(..., description="Workspace identifier") 
    workspace_role: WorkspaceRole = Field(..., description="Member role in workspace")
    user_email: Optional[str] = Field(None, description="User email address")
    user_name: Optional[str] = Field(None, description="User display name")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user_67890",
                "workspace_id": "wrkspc_12345",
                "workspace_role": "workspace_developer",
                "user_email": "dev@company.com",
                "user_name": "Jane Developer",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z"
            }
        }
