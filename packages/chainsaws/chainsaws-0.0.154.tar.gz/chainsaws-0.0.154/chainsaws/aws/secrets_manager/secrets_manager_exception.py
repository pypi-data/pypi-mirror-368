class SecretsManagerException(Exception):
    """Base exception for the secrets manager."""


class SecretNotFoundException(SecretsManagerException):
    """Exception raised when a secret is not found."""


class SecretAlreadyExistsException(SecretsManagerException):
    """Exception raised when a secret already exists."""


class SecretsManagerDeletionAlreadyScheduledException(SecretsManagerException):
    """Exception raised when a secret is already scheduled for deletion."""
