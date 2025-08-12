"""
ZKAuth Python SDK

Zero-knowledge proof authentication SDK for Python applications.
"""

from .client import ZKAuthSDK
from .models import User, AuthResult, DeviceInfo, SessionInfo
from .exceptions import (
    ZKAuthError,
    ValidationError,
    AuthenticationError,
    NetworkError,
    CircuitError,
)

__version__ = "1.0.0"
__author__ = "ZKAuth Team"
__email__ = "support@zkauth.com"

__all__ = [
    "ZKAuthSDK",
    "User",
    "AuthResult",
    "DeviceInfo",
    "SessionInfo",
    "ZKAuthError",
    "ValidationError",
    "AuthenticationError",
    "NetworkError",
    "CircuitError",
]
