"""Anthropic Admin SDK - Unofficial Python SDK for Anthropic Admin API."""

from .client import AnthropicAdminClient
from .exceptions import (
    AnthropicAdminError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

__version__ = "0.1.0"
__author__ = "Admin SDK Developer"
__email__ = "developer@example.com"

__all__ = [
    "AnthropicAdminClient",
    "AnthropicAdminError",
    "AuthenticationError",
    "PermissionError", 
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
]
