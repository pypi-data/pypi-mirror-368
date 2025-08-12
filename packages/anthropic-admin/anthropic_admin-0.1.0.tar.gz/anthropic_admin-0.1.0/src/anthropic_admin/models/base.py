"""Base model classes for Anthropic Admin SDK."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBaseModel, Field


class BaseModel(PydanticBaseModel):
    """Base model with common configuration."""
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"
        use_enum_values = True
        validate_assignment = True
        
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return self.model_dump(exclude_none=True)


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
