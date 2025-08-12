"""
Exception classes for ZKAuth SDK
"""


class ZKAuthError(Exception):
    """Base exception for ZKAuth SDK"""
    pass


class ValidationError(ZKAuthError):
    """Raised when input validation fails"""
    pass


class AuthenticationError(ZKAuthError):
    """Raised when authentication fails"""
    pass


class NetworkError(ZKAuthError):
    """Raised when network requests fail"""
    pass


class CircuitError(ZKAuthError):
    """Raised when ZK circuit operations fail"""
    pass


class APIError(ZKAuthError):
    """Raised when API returns an error"""
    def __init__(self, message: str, status_code: int = 0, error_code: str = "UNKNOWN"):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
