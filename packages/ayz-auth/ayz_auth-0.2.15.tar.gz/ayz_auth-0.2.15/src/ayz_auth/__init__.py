"""
ayz-auth: FastAPI middleware for Stytch B2B authentication with Redis caching.

This package provides a clean, reusable authentication middleware for FastAPI
applications using Stytch B2B authentication services with Redis caching for
optimal performance.
"""

from .middleware import create_auth_dependency, verify_auth, verify_auth_optional
from .models.context import StytchContext
from .utils.exceptions import (
    AuthenticationError,
    StytchAPIError,
    TokenExtractionError,
    TokenVerificationError,
)

__version__ = "0.1.0"
__all__ = [
    "verify_auth",
    "verify_auth_optional",
    "create_auth_dependency",
    "StytchContext",
    "AuthenticationError",
    "TokenExtractionError",
    "TokenVerificationError",
    "StytchAPIError",
]
