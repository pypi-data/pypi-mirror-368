"""Redshift Data Plane operations.

This module provides functionality for interacting with Redshift data operations:
- Query execution and management
- Table and schema operations
- Data manipulation (CRUD)
- Performance analysis
"""

from chainsaws.aws.redshift.data_plane.api import RedshiftAPI
from chainsaws.aws.redshift.data_plane.models import (
    RedshiftAPIConfig,
    QueryResult,
    QueryState,
    QueryStatistics,
    TypedQueryResult,
    Column,
    Table,
    Schema,
    Database,
    QueryPerformanceReport,
)
from chainsaws.aws.redshift.data_plane.query_builder import (
    QueryBuilder,
    InsertBuilder,
    UpdateBuilder,
    DeleteBuilder,
    ComparisonOperator,
    JoinType,
    OrderDirection,
)
from chainsaws.aws.redshift.data_plane.exception import (
    RedshiftError,
    QueryExecutionError,
    QueryTimeoutError,
    QueryCancellationError,
    InvalidQueryError,
    ResultError,
    ConnectionError,
    ResourceNotFoundError,
    ValidationError,
    TransactionError,
    DataError,
)

__all__ = [
    # Main API
    "RedshiftAPI",
    "RedshiftAPIConfig",

    # Query builders
    "QueryBuilder",
    "InsertBuilder",
    "UpdateBuilder",
    "DeleteBuilder",
    "ComparisonOperator",
    "JoinType",
    "OrderDirection",

    # Models
    "Column",
    "Table",
    "Schema",
    "Database",
    "QueryResult",
    "QueryState",
    "QueryStatistics",
    "TypedQueryResult",
    "QueryPerformanceReport",

    # Exceptions
    "RedshiftError",
    "QueryExecutionError",
    "QueryTimeoutError",
    "QueryCancellationError",
    "InvalidQueryError",
    "ResultError",
    "ConnectionError",
    "ResourceNotFoundError",
    "ValidationError",
    "TransactionError",
    "DataError",
]
