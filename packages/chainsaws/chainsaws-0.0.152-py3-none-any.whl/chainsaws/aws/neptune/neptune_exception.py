"""Neptune-specific exceptions.

This module defines exceptions specific to Neptune operations.
"""

class NeptuneError(Exception):
    """Base exception for Neptune operations."""
    pass


class NeptuneConnectionError(NeptuneError):
    """Exception raised when connection to Neptune fails."""
    pass


class NeptuneQueryError(NeptuneError):
    """Exception raised when a query execution fails."""
    def __init__(self, message: str, query: str = None):
        self.query = query
        super().__init__(message)


class NeptuneModelError(NeptuneError):
    """Exception raised when there's an issue with graph models."""
    pass


class NeptuneTransactionError(NeptuneError):
    """Exception raised when a transaction operation fails."""
    pass


class NeptuneValidationError(NeptuneError):
    """Exception raised when validation of graph entities fails."""
    pass


class NeptuneSerializationError(NeptuneError):
    """Exception raised when serialization or deserialization fails."""
    pass


class NeptuneTimeoutError(NeptuneError):
    """Exception raised when a Neptune operation times out."""
    pass


class NeptuneResourceNotFoundError(NeptuneError):
    """Exception raised when a requested resource is not found."""
    pass 