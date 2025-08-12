"""Custom exceptions for Anthropic Admin SDK."""

from typing import Optional, Dict, Any


class AnthropicAdminError(Exception):
    """Base exception for all Anthropic Admin SDK errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(AnthropicAdminError):
    """Raised when authentication fails (401)."""
    
    def __init__(self, message: str = "Invalid or missing admin API key"):
        super().__init__(message, status_code=401)


class PermissionError(AnthropicAdminError):
    """Raised when insufficient permissions (403)."""
    
    def __init__(self, message: str = "Insufficient permissions for this operation"):
        super().__init__(message, status_code=403)


class NotFoundError(AnthropicAdminError):
    """Raised when a resource is not found (404)."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AnthropicAdminError):
    """Raised when request validation fails (400)."""
    
    def __init__(self, message: str = "Invalid request data"):
        super().__init__(message, status_code=400)


class RateLimitError(AnthropicAdminError):
    """Raised when rate limit is exceeded (429)."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class ServerError(AnthropicAdminError):
    """Raised when server returns 5xx error."""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)
