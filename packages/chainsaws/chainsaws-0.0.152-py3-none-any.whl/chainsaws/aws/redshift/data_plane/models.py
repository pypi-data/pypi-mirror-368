"""Model definitions for Redshift API."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union
from dataclasses import dataclass, field

from chainsaws.aws.shared.config import APIConfig


@dataclass
class RedshiftAPIConfig(APIConfig):
    """Configuration for RedshiftAPI."""

    database: str  # Default database name
    schema: str = "public"  # Default schema name
    port: int = 5439  # Redshift port
    max_pool_connections: int = 50  # Maximum number of connections in the pool
    ssl_mode: str = "verify-full"  # SSL mode for connections
    ssl_cert_path: Optional[str] = None  # Path to SSL certificate
    connection_timeout: int = 30  # Connection timeout in seconds

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 1 <= self.max_pool_connections <= 500:
            raise ValueError("max_pool_connections must be between 1 and 500")
        if not 1 <= self.connection_timeout <= 300:
            raise ValueError("connection_timeout must be between 1 and 300")


@dataclass
class ConnectionPoolStatus:
    """Status information about the connection pool."""

    total_connections: int  # Total number of connections in the pool
    active_connections: int  # Number of currently active connections
    available_connections: int  # Number of available connections
    connection_attempts: int  # Number of connection attempts made
    last_reset: datetime  # Timestamp of last pool reset
    max_connections: int  # Maximum allowed connections


@dataclass
class BatchOperationResult:
    """Result of a batch operation."""

    total_records: int  # Total number of records in the batch
    processed_records: int  # Number of successfully processed records
    failed_records: int  # Number of failed records
    execution_time: float  # Total execution time in seconds

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of the batch operation."""
        return self.processed_records / self.total_records if self.total_records > 0 else 0.0


@dataclass
class QueryConfig:
    """Configuration for query execution."""

    query: str  # SQL query to execute
    database: str  # Target database
    schema: str = "public"  # Target schema
    parameters: List[Dict[str, Any]] = field(
        default_factory=list)  # Query parameters
    timeout: int = 30  # Query timeout in seconds
    fetch_size: int = 1000  # Number of rows to fetch per batch


@dataclass
class TransactionConfig:
    """Configuration for transaction management."""

    database: str  # Target database
    schema: str = "public"  # Target schema
    isolation_level: str = "read committed"  # Transaction isolation level
    read_only: bool = False  # Whether transaction is read-only


@dataclass
class CopyConfig:
    """Configuration for COPY operations."""

    table_name: str  # Target table name
    data_source: str  # Data source (e.g., S3 path)
    database: str  # Target database
    schema: str = "public"  # Target schema
    columns: Optional[List[str]] = None  # Columns to copy
    options: Dict[str, Any] = field(
        default_factory=dict)  # COPY command options


@dataclass
class UnloadConfig:
    """Configuration for UNLOAD operations."""

    query: str  # Query to unload
    destination: str  # Destination path (e.g., S3 path)
    database: str  # Source database
    schema: str = "public"  # Source schema
    options: Dict[str, Any] = field(
        default_factory=dict)  # UNLOAD command options


class Column(TypedDict):
    """Column information."""
    name: str
    type: str
    nullable: bool
    default: Optional[str]
    encoding: Optional[str]
    distkey: bool
    sortkey: bool
    primary_key: bool


class Table(TypedDict):
    """Table information."""
    schema: str
    name: str
    type: str
    columns: List[Column]
    distribution_style: str
    sort_keys: List[str]
    encoded: bool


class Schema(TypedDict):
    """Schema information."""
    name: str
    owner: str
    tables: List[Table]


class Database(TypedDict):
    """Database information."""
    name: str
    owner: str
    schemas: List[Schema]
    created: datetime
    last_modified: datetime


class ClusterStatus(str, Enum):
    """Redshift cluster status."""
    AVAILABLE = "available"
    CREATING = "creating"
    DELETING = "deleting"
    FINAL_SNAPSHOT = "final-snapshot"
    HARDWARE_FAILURE = "hardware-failure"
    INCOMPATIBLE_HSM = "incompatible-hsm"
    INCOMPATIBLE_NETWORK = "incompatible-network"
    INCOMPATIBLE_PARAMETERS = "incompatible-parameters"
    INCOMPATIBLE_RESTORE = "incompatible-restore"
    MODIFYING = "modifying"
    REBOOTING = "rebooting"
    RENAMING = "renaming"
    RESIZING = "resizing"
    ROTATING_KEYS = "rotating-keys"
    STORAGE_FULL = "storage-full"
    UPDATING_HSM = "updating-hsm"


class ClusterInfo(TypedDict):
    """Redshift cluster information."""
    identifier: str
    status: ClusterStatus
    availability_zone: str
    node_type: str
    cluster_type: str
    number_of_nodes: int
    master_username: str
    database_name: str
    port: int
    cluster_version: str
    vpc_id: Optional[str]
    encrypted: bool
    maintenance_window: str
    automated_snapshot_retention_period: int
    preferred_maintenance_window: str
    availability_zone_relocation_status: str
    cluster_namespace_arn: str
    total_storage_capacity_in_mega_bytes: int
    aqua_configuration_status: str
    default_iam_role_arn: str
    expected_next_snapshot_schedule_time: datetime
    expected_next_snapshot_schedule_time_status: str
    next_maintenance_window_start_time: datetime
    resize_info: Optional[Dict[str, Any]]


class UserInfo(TypedDict):
    """Redshift user information."""
    name: str
    connection_limit: int
    created: datetime
    expires: Optional[datetime]
    system_user: bool
    super_user: bool


class GroupInfo(TypedDict):
    """Redshift group information."""
    name: str
    created: datetime
    users: List[str]


@dataclass
class QueryPerformanceReport:
    """Query performance analysis report."""

    execution_time: float  # Total execution time in seconds
    data_scanned: int  # Amount of data scanned in bytes
    cost_estimate: float  # Estimated cost of the query
    engine_version: str  # Redshift engine version
    suggestions: List[str]  # Optimization suggestions
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]  # Performance risk level
    bottlenecks: List[str]  # Identified bottlenecks
    optimization_tips: List[str]  # Tips for optimization
    # Partition-related information
    partition_info: Optional[Dict[str, Any]] = None
    join_info: Optional[Dict[str, Any]] = None  # Join-related information


@dataclass
class DetailedError:
    """Detailed error information with suggestions."""

    error_code: str  # Error code
    message: str  # Error message
    details: Dict[str, Any]  # Additional error details
    suggestions: List[str]  # Error resolution suggestions
    query_stage: str  # Stage where error occurred
    error_location: Optional[str] = None  # Location of the error
    error_type: str = "UNKNOWN"  # Type of error

    @property
    def is_recoverable(self) -> bool:
        """Check if the error is potentially recoverable."""
        return self.error_type not in ["FATAL", "SYSTEM"]


"""Data models for Redshift operations."""

# Basic value types that can be used in Redshift
RedshiftValue = Union[
    str,
    int,
    float,
    bool,
    datetime,
    None,
    List['RedshiftValue'],
    Dict[str, 'RedshiftValue']
]

# Parameter types for queries
QueryParams = Dict[str, RedshiftValue]

# Record types
RedshiftRecord = Dict[str, RedshiftValue]
RedshiftRecordList = List[RedshiftRecord]


class QueryState(str, Enum):
    """States of query execution."""
    QUEUED = "QUEUED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


@dataclass
class QueryResult:
    """Result of a query execution."""

    query_id: str  # Query ID
    state: QueryState  # Query state
    result_rows: list[RedshiftRecord]  # Result rows
    affected_rows: int  # Number of affected rows
    statistics: Optional['QueryStatistics'] = None  # Query statistics
    error: Optional['DetailedError'] = None  # Error details if any

    def __post_init__(self) -> None:
        """Validate query result after initialization."""
        if not self.query_id:
            raise ValueError("query_id is required")
        if not isinstance(self.result_rows, list):
            raise ValueError("result_rows must be a list")
        if self.affected_rows < 0:
            raise ValueError("affected_rows must be non-negative")


class QueryStatistics(TypedDict):
    """Statistics about query execution."""
    elapsed_time: float
    cpu_time: float
    queued_time: float
    bytes_scanned: int
    rows_produced: int
    rows_affected: int
