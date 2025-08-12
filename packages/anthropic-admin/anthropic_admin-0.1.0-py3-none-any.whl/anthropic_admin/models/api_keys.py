"""API key models."""

from enum import Enum
from typing import Optional
from pydantic import Field

from .base import TimestampedModel


class ApiKeyStatus(str, Enum):
    """API key status."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class ApiKey(TimestampedModel):
    """API key model."""
    
    id: str = Field(..., description="Unique API key identifier")
    name: str = Field(..., description="API key name")
    status: ApiKeyStatus = Field(..., description="API key status")
    workspace_id: Optional[str] = Field(None, description="Associated workspace ID")
    workspace_name: Optional[str] = Field(None, description="Associated workspace name")
    key_preview: Optional[str] = Field(None, description="Partial key for identification")
    usage_count: Optional[int] = Field(None, description="Number of API calls made")
    last_used_at: Optional[str] = Field(None, description="Last usage timestamp")
    created_by: Optional[str] = Field(None, description="ID of user who created the key")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "key_12345",
                "name": "Production API Key",
                "status": "active",
                "workspace_id": "wrkspc_67890",
                "workspace_name": "Production",
                "key_preview": "sk-ant-api03-***-xyz",
                "usage_count": 1543,
                "last_used_at": "2024-01-20T14:45:00Z",
                "created_by": "user_12345",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z"
            }
        }
