"""Base resource class for Anthropic Admin SDK."""

from typing import TYPE_CHECKING, List, Dict, Any, Optional

if TYPE_CHECKING:
    from ..utils.http import HTTPClient


class BaseResource:
    """Base resource class with common functionality."""
    
    def __init__(self, http_client: "HTTPClient"):
        self._http_client = http_client
    
    def _build_params(self, **kwargs) -> Dict[str, Any]:
        """Build query parameters, filtering out None values."""
        return {k: v for k, v in kwargs.items() if v is not None}
    
    def _parse_list_response(self, response: Dict[str, Any], model_class) -> List:
        """Parse a list response into model instances."""
        items = response.get("data", [])
        return [model_class(**item) for item in items]
    
    def _parse_single_response(self, response: Dict[str, Any], model_class):
        """Parse a single item response into model instance."""
        return model_class(**response)
