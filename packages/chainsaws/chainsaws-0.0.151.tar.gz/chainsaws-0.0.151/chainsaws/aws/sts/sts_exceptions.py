"""Exceptions for AWS STS operations."""


class STSError(Exception):
    """Base exception for STS-related errors."""
    pass


class RoleAssumptionError(STSError):
    """Raised when role assumption fails."""
    pass


class FederationTokenError(STSError):
    """Raised when federation token retrieval fails."""
    pass


class CallerIdentityError(STSError):
    """Raised when caller identity retrieval fails."""
    pass


class SessionTokenError(STSError):
    """Raised when session token retrieval fails."""
    pass


class AuthorizationMessageError(STSError):
    """Raised when authorization message decoding fails."""
    pass


class AccessKeyInfoError(STSError):
    """Raised when access key info retrieval fails."""
    pass 