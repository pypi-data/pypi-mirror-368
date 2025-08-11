"""Exception classes for Redshift API."""

from typing import Any, Dict, List, Optional


class RedshiftError(Exception):
    """Base exception class for all Redshift-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class QueryExecutionError(RedshiftError):
    """Raised when query execution fails."""

    def __init__(
        self,
        message: str,
        query: str,
        query_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.query = query
        self.query_id = query_id


class QueryTimeoutError(QueryExecutionError):
    """Raised when a query exceeds its timeout limit."""

    def __init__(
        self,
        query: str,
        timeout_seconds: int,
        query_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Query execution timed out after {timeout_seconds} seconds"
        super().__init__(message, query, query_id, details)
        self.timeout_seconds = timeout_seconds


class QueryCancellationError(QueryExecutionError):
    """Raised when a query is cancelled."""

    def __init__(
        self,
        query: str,
        reason: Optional[str] = None,
        query_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Query was cancelled{f': {reason}' if reason else ''}"
        super().__init__(message, query, query_id, details)
        self.reason = reason


class InvalidQueryError(QueryExecutionError):
    """Raised for invalid query syntax."""

    def __init__(
        self,
        query: str,
        error_position: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = "Invalid query syntax"
        if error_position:
            message += f" at {error_position}"
        super().__init__(message, query, None, details)
        self.error_position = error_position
        self.suggestions = suggestions or []


class ResultError(RedshiftError):
    """Raised when there is a failure in retrieving query results."""

    def __init__(
        self,
        message: str,
        query_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.query_id = query_id


class ConnectionError(RedshiftError):
    """Raised when there is a failure to connect to Redshift."""

    def __init__(
        self,
        message: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.host = host
        self.port = port
        self.database = database


class ClusterError(RedshiftError):
    """Raised for failed cluster operations."""

    def __init__(
        self,
        message: str,
        cluster_id: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.cluster_id = cluster_id
        self.operation = operation


class ResourceNotFoundError(RedshiftError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource_type} '{resource_id}' not found"
        super().__init__(message, details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ValidationError(RedshiftError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.field = field
        self.value = value


class TransactionError(RedshiftError):
    """Raised for transaction-related errors."""

    def __init__(
        self,
        message: str,
        transaction_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.transaction_id = transaction_id


class PermissionError(RedshiftError):
    """Raised when permission is denied for an operation."""

    def __init__(
        self,
        message: str,
        operation: str,
        resource: Optional[str] = None,
        user: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.operation = operation
        self.resource = resource
        self.user = user


class ConfigurationError(RedshiftError):
    """Raised when there is an error in configuration."""

    def __init__(
        self,
        message: str,
        parameter: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.parameter = parameter
        self.value = value


class ConcurrencyError(RedshiftError):
    """Raised when there are concurrency-related issues."""

    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.resource = resource


class QuotaExceededError(RedshiftError):
    """Raised when a quota or limit is exceeded."""

    def __init__(
        self,
        message: str,
        quota_name: str,
        current_value: Any,
        limit: Any,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.quota_name = quota_name
        self.current_value = current_value
        self.limit = limit


class MaintenanceError(RedshiftError):
    """Raised during maintenance operations."""

    def __init__(
        self,
        message: str,
        maintenance_type: str,
        estimated_duration: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.maintenance_type = maintenance_type
        self.estimated_duration = estimated_duration


class NetworkError(RedshiftError):
    """Raised for network-related issues."""

    def __init__(
        self,
        message: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.host = host
        self.port = port


class DataError(RedshiftError):
    """Raised for data-related errors."""

    def __init__(
        self,
        message: str,
        table: Optional[str] = None,
        column: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.table = table
        self.column = column
        self.value = value
