"""
Custom exceptions for the DoorDash client.
"""

from typing import Any, Dict, Optional


class DoorDashClientError(Exception):
    """Base exception for all DoorDash client errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(DoorDashClientError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(DoorDashClientError):
    """Raised when the user is not authorized to perform an action."""
    pass


class SessionError(DoorDashClientError):
    """Raised when session management fails."""
    pass


class APIError(DoorDashClientError):
    """Raised when the API returns an error response."""
    pass


class ValidationError(DoorDashClientError):
    """Raised when input validation fails."""
    pass


class NetworkError(DoorDashClientError):
    """Raised when network requests fail."""
    pass


class TimeoutError(DoorDashClientError):
    """Raised when requests timeout."""
    pass


class RateLimitError(DoorDashClientError):
    """Raised when rate limits are exceeded."""
    pass


class NotFoundError(DoorDashClientError):
    """Raised when a resource is not found."""
    pass


class OrderError(DoorDashClientError):
    """Raised when order operations fail."""
    pass


class CartError(DoorDashClientError):
    """Raised when cart operations fail."""
    pass


class PaymentError(DoorDashClientError):
    """Raised when payment operations fail."""
    pass