"""Custom exceptions for ReqNinja."""


class ReqNinjaError(Exception):
    """Base exception for all ReqNinja errors."""
    pass


class ConfigError(ReqNinjaError):
    """Raised when there's an issue with configuration."""
    pass


class AuthenticationError(ReqNinjaError):
    """Raised when authentication fails."""
    pass


class RetryError(ReqNinjaError):
    """Raised when all retry attempts are exhausted."""
    pass


class ValidationError(ReqNinjaError):
    """Raised when request validation fails."""
    pass


class ProfileNotFoundError(ConfigError):
    """Raised when a requested profile is not found."""
    pass


class InvalidURLError(ReqNinjaError):
    """Raised when an invalid URL is provided."""
    pass
