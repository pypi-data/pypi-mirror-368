"""AWS Redshift API.

This module provides a high-level Python API for AWS Redshift.
It supports both Data Plane operations for database tasks and Control Plane operations for cluster management.

Key Features:
- Query execution and result processing
- Batch operations and bulk data loading
- Performance monitoring and analysis
- Security and access control
- Cluster management
- Parameter group management
- NoSQL-style interface for simplified operations
"""

from chainsaws.aws.redshift.data_plane.api import RedshiftAPI
from chainsaws.aws.redshift.data_plane.models import (
    RedshiftAPIConfig,
    QueryState,
    QueryStatistics,
    QueryResult,
    TypedQueryResult,
    QueryPerformanceReport,
    BatchOperationResult,
    ConnectionPoolStatus,
    DetailedError,
)
from chainsaws.aws.redshift.data_plane.query_builder import (
    QueryBuilder,
    QueryType,
    ComparisonOperator,
    JoinType,
    WindowFunction,
    OrderDirection,
    AggregateFunction,
    SetOperation,
)
from chainsaws.aws.redshift.data_plane.monitoring import (
    QueryMonitor,
    ResourceMonitor,
    PerformanceAnalyzer,
    QueryMetrics,
)
from chainsaws.aws.redshift.data_plane.batch import (
    BatchConfig,
    BatchProcessor,
    BulkLoader,
)
from chainsaws.aws.redshift.data_plane.security import (
    ConnectionCredentials,
    CredentialManager,
    TokenManager,
    IAMAuthenticator,
    AccessController,
)
from chainsaws.aws.redshift.control_plane.control import RedshiftControlAPI
from chainsaws.aws.redshift.control_plane.models import (
    ClusterConfig,
    NetworkConfig,
    MaintenanceWindow,
    BackupConfig,
    ClusterStatus,
    IamRole,
    SecurityGroup,
    User,
    Group,
    Permission,
    ParameterGroupConfig,
)

__all__ = [
    # Data Plane - Core
    "RedshiftAPI",
    "RedshiftAPIConfig",

    # Data Plane - Models
    "QueryState",
    "QueryStatistics",
    "QueryResult",
    "TypedQueryResult",
    "QueryPerformanceReport",
    "BatchOperationResult",
    "ConnectionPoolStatus",
    "DetailedError",

    # Data Plane - Query Builder
    "QueryBuilder",
    "QueryType",
    "ComparisonOperator",
    "JoinType",
    "WindowFunction",
    "OrderDirection",
    "AggregateFunction",
    "SetOperation",

    # Data Plane - Monitoring
    "QueryMonitor",
    "ResourceMonitor",
    "PerformanceAnalyzer",
    "QueryMetrics",

    # Data Plane - Batch Operations
    "BatchConfig",
    "BatchProcessor",
    "BulkLoader",

    # Data Plane - Security
    "ConnectionCredentials",
    "CredentialManager",
    "TokenManager",
    "IAMAuthenticator",
    "AccessController",

    # Control Plane - Core
    "RedshiftControlAPI",

    # Control Plane - Models
    "ClusterConfig",
    "NetworkConfig",
    "MaintenanceWindow",
    "BackupConfig",
    "ClusterStatus",
    "IamRole",
    "SecurityGroup",
    "User",
    "Group",
    "Permission",
    "ParameterGroupConfig",
]
