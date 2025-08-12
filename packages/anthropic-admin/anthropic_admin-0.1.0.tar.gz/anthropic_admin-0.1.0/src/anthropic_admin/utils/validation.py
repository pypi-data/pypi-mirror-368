"""Validation utilities for Anthropic Admin SDK."""

import re
from typing import Union
from ..exceptions import ValidationError


def validate_api_key(api_key: str) -> None:
    """Validate Anthropic admin API key format.
    
    Args:
        api_key: The API key to validate
        
    Raises:
        ValidationError: If API key format is invalid
    """
    if not api_key:
        raise ValidationError("API key cannot be empty")
    
    if not api_key.startswith("sk-ant-admin-"):
        raise ValidationError(
            "Invalid admin API key format. Admin keys must start with 'sk-ant-admin-'"
        )
    
    if len(api_key) < 20:
        raise ValidationError("API key appears to be too short")


def validate_email(email: str) -> None:
    """Validate email address format.
    
    Args:
        email: The email address to validate
        
    Raises:
        ValidationError: If email format is invalid
    """
    if not email:
        raise ValidationError("Email cannot be empty")
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")


def validate_user_id(user_id: str) -> None:
    """Validate user ID format.
    
    Args:
        user_id: The user ID to validate
        
    Raises:
        ValidationError: If user ID format is invalid
    """
    if not user_id:
        raise ValidationError("User ID cannot be empty")
    
    if not user_id.startswith("user_"):
        raise ValidationError("User ID must start with 'user_'")


def validate_workspace_id(workspace_id: str) -> None:
    """Validate workspace ID format.
    
    Args:
        workspace_id: The workspace ID to validate
        
    Raises:
        ValidationError: If workspace ID format is invalid
    """
    if not workspace_id:
        raise ValidationError("Workspace ID cannot be empty")
    
    if not workspace_id.startswith("wrkspc_"):
        raise ValidationError("Workspace ID must start with 'wrkspc_'")


def validate_api_key_id(api_key_id: str) -> None:
    """Validate API key ID format.
    
    Args:
        api_key_id: The API key ID to validate
        
    Raises:
        ValidationError: If API key ID format is invalid
    """
    if not api_key_id:
        raise ValidationError("API key ID cannot be empty")
    
    if not api_key_id.startswith("key_"):
        raise ValidationError("API key ID must start with 'key_'")


def validate_invite_id(invite_id: str) -> None:
    """Validate invite ID format.
    
    Args:
        invite_id: The invite ID to validate
        
    Raises:
        ValidationError: If invite ID format is invalid
    """
    if not invite_id:
        raise ValidationError("Invite ID cannot be empty")
    
    if not invite_id.startswith("invite_"):
        raise ValidationError("Invite ID must start with 'invite_'")
