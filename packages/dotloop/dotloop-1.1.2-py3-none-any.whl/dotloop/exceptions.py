"""Custom exceptions for the Dotloop API wrapper."""

from typing import Any, Dict, Optional


class DotloopError(Exception):
    """Base exception for all Dotloop API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_data: Response data from the API if available
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(DotloopError):
    """Raised when authentication fails."""

    pass


class AuthorizationError(DotloopError):
    """Raised when authorization fails (insufficient permissions)."""

    pass


class ValidationError(DotloopError):
    """Raised when request validation fails."""

    pass


class NotFoundError(DotloopError):
    """Raised when a resource is not found."""

    pass


class RateLimitError(DotloopError):
    """Raised when rate limit is exceeded."""

    pass


class ServerError(DotloopError):
    """Raised when server returns 5xx errors."""

    pass


class RedirectError(DotloopError):
    """Raised when a resource has been moved (e.g., merged loops)."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        location: Optional[str] = None,
    ) -> None:
        """Initialize the redirect exception.

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Response data from the API
            location: New location URL from Location header
        """
        super().__init__(message, status_code, response_data)
        self.location = location
