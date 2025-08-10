"""Exceptions for Athena API."""


class AthenaError(Exception):
    """Base exception for Athena API."""
    pass


class QueryExecutionError(AthenaError):
    """Raised when query execution fails."""
    pass


class QueryTimeoutError(QueryExecutionError):
    """Raised when query execution exceeds timeout."""
    pass


class QueryCancellationError(QueryExecutionError):
    """Raised when query is cancelled."""
    pass


class InvalidQueryError(QueryExecutionError):
    """Raised when query syntax is invalid."""
    pass


class ResultError(AthenaError):
    """Raised when failed to get query results."""
    pass
