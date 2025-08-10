"""AWS Athena client wrapper.

This module provides a high-level interface to AWS Athena service.
It includes functionality for:
- Query execution and result retrieval
- Database management
- Table management
- Workgroup management
- Partition management
- Query analysis and optimization
"""

from chainsaws.aws.athena.athena import AthenaAPI
from chainsaws.aws.athena.athena_models import (
    AthenaAPIConfig,
    QueryExecution,
    QueryExecutionState,
    QueryExecutionStatistics,
    QueryResult,
    Database,
    Table,
    TableColumn,
    TableProperties,
    WorkGroup,
    WorkGroupConfiguration,
    WorkGroupState,
    PartitionValue,
    QueryAnalysis,
    TypedQueryResult,
    QueryPerformanceReport,
    DetailedError,
)
from chainsaws.aws.athena.athena_exception import (
    QueryExecutionError,
    QueryTimeoutError,
    QueryCancellationError,
    InvalidQueryError,
    ResultError,
)
from chainsaws.aws.athena.template import QueryTemplate
from chainsaws.aws.athena.query_builder import QueryBuilder
from chainsaws.aws.athena.session import QuerySession
from chainsaws.aws.athena.async_session import AsyncSession, AsyncQueryExecution

__all__ = [
    # Main API
    "AthenaAPI",
    "AthenaAPIConfig",

    # Query related
    "QueryExecution",
    "QueryExecutionState",
    "QueryExecutionStatistics",
    "QueryResult",
    "TypedQueryResult",

    # Database and Table related
    "Database",
    "Table",
    "TableColumn",
    "TableProperties",

    # Workgroup related
    "WorkGroup",
    "WorkGroupConfiguration",
    "WorkGroupState",

    # Partition related
    "PartitionValue",

    # Analysis related
    "QueryAnalysis",
    "QueryPerformanceReport",

    # Exceptions
    "QueryExecutionError",
    "QueryTimeoutError",
    "QueryCancellationError",
    "InvalidQueryError",
    "ResultError",
    "DetailedError",

    # Query Building
    "QueryTemplate",
    "QueryBuilder",

    # Sessions
    "QuerySession",
    "AsyncSession",
    "AsyncQueryExecution",
]
