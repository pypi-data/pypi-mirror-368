"""HTTP client utilities for Anthropic Admin SDK."""

import time
from typing import Optional, Dict, Any, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..exceptions import (
    AnthropicAdminError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)


class HTTPClient:
    """HTTP client for Anthropic Admin API with retry logic and error handling."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anthropic.com/v1",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
            "User-Agent": "anthropic-admin-sdk/0.1.0",
        })
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        try:
            response_data = response.json() if response.content else {}
        except ValueError:
            response_data = {"detail": "Invalid JSON response"}
        
        if response.status_code == 200 or response.status_code == 201:
            return response_data
        elif response.status_code == 400:
            raise ValidationError(
                response_data.get("detail", "Bad request"),
                response_data=response_data,
            )
        elif response.status_code == 401:
            raise AuthenticationError(
                response_data.get("detail", "Invalid or missing admin API key"),
                response_data=response_data,
            )
        elif response.status_code == 403:
            raise PermissionError(
                response_data.get("detail", "Insufficient permissions"),
                response_data=response_data,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                response_data.get("detail", "Resource not found"),
                response_data=response_data,
            )
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                response_data.get("detail", "Rate limit exceeded"),
                retry_after=retry_after,
            )
        elif response.status_code >= 500:
            raise ServerError(
                response_data.get("detail", "Internal server error"),
                status_code=response.status_code,
                response_data=response_data,
            )
        else:
            raise AnthropicAdminError(
                f"Unexpected status code {response.status_code}: {response_data.get('detail', 'Unknown error')}",
                status_code=response.status_code,
                response_data=response_data,
            )
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make GET request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        return self._handle_response(response)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make POST request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(
            url, json=data, params=params, timeout=self.timeout
        )
        return self._handle_response(response)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make PUT request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.put(
            url, json=data, params=params, timeout=self.timeout
        )
        return self._handle_response(response)
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make DELETE request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.delete(url, params=params, timeout=self.timeout)
        return self._handle_response(response)
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
