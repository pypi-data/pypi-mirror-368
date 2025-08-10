"""Exceptions used within aioldata."""


class LDATAException(Exception):
    """Base exception for Leviton Load Data."""


class AuthError(LDATAException):
    """Base exception for authentication."""


class ExceededMaximumRetries(LDATAException):
    """Data unable to be sent after hitting retry limit."""


class InvalidAuth(AuthError):
    """Invalid auth data provided to login."""


class InvalidResidences(LDATAException):
    """No residence data available."""


class InvalidResponse(AuthError):
    """Unexpected response type from API."""


class UnknownAuthError(AuthError):
    """Error occurred when performing auth."""
