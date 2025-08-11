"""Base client for the Dotloop API wrapper."""

import os
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    DotloopError,
    NotFoundError,
    RateLimitError,
    RedirectError,
    ServerError,
    ValidationError,
)

# Load environment variables
load_dotenv()


class BaseClient:
    """Base client for Dotloop API endpoints."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the base client.

        Args:
            api_key: API access token for authentication
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self._api_key = api_key or os.getenv("DOTLOOP_API_KEY")
        self._base_url = base_url or "https://api-gateway.dotloop.com/public/v2"
        self._timeout = timeout

        if not self._api_key:
            raise AuthenticationError(
                "API key is required. Set DOTLOOP_API_KEY environment variable or pass api_key parameter."
            )

    @property
    def headers(self) -> Dict[str, str]:
        """Get default headers for API requests.

        Returns:
            Dictionary of headers
        """
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for an endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Full URL for the endpoint
        """
        # Ensure base URL ends with slash for proper joining
        base_url = self._base_url.rstrip("/") + "/"
        return urljoin(base_url, endpoint.lstrip("/"))

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response data

        Raises:
            DotloopError: For various API errors
        """
        try:
            response_data = response.json() if response.content else {}
        except ValueError:
            response_data = {}

        if response.status_code == 200:
            return response_data
        elif response.status_code == 201:
            return response_data
        elif response.status_code == 301:
            location = response.headers.get("Location")
            raise RedirectError(
                f"Resource has been moved to: {location}",
                status_code=response.status_code,
                response_data=response_data,
                location=location,
            )
        elif response.status_code == 400:
            raise ValidationError(
                f"Bad request: {response_data.get('message', 'Invalid request parameters')}",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 401:
            raise AuthenticationError(
                f"Authentication failed: {response_data.get('message', 'Invalid or expired token')}",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 403:
            raise AuthorizationError(
                f"Authorization failed: {response_data.get('message', 'Insufficient permissions')}",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                f"Resource not found: {response_data.get('message', 'The requested resource was not found')}",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 429:
            raise RateLimitError(
                f"Rate limit exceeded: {response_data.get('message', 'Too many requests')}",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code >= 500:
            raise ServerError(
                f"Server error: {response_data.get('message', 'Internal server error')}",
                status_code=response.status_code,
                response_data=response_data,
            )
        else:
            raise DotloopError(
                f"Unexpected error: {response_data.get('message', 'Unknown error occurred')}",
                status_code=response.status_code,
                response_data=response_data,
            )

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a GET request to the API.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Additional headers

        Returns:
            Parsed JSON response data

        Raises:
            DotloopError: For API errors
        """
        url = self._build_url(endpoint)
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = requests.get(
                url, params=params, headers=request_headers, timeout=self._timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            raise DotloopError(f"Request failed: {str(e)}")

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request to the API.

        Args:
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers

        Returns:
            Parsed JSON response data

        Raises:
            DotloopError: For API errors
        """
        url = self._build_url(endpoint)
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = requests.post(
                url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=self._timeout,
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            raise DotloopError(f"Request failed: {str(e)}")

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a PATCH request to the API.

        Args:
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers

        Returns:
            Parsed JSON response data

        Raises:
            DotloopError: For API errors
        """
        url = self._build_url(endpoint)
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = requests.patch(
                url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=self._timeout,
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            raise DotloopError(f"Request failed: {str(e)}")

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a DELETE request to the API.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Additional headers

        Returns:
            Parsed JSON response data

        Raises:
            DotloopError: For API errors
        """
        url = self._build_url(endpoint)
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = requests.delete(
                url, params=params, headers=request_headers, timeout=self._timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            raise DotloopError(f"Request failed: {str(e)}")
