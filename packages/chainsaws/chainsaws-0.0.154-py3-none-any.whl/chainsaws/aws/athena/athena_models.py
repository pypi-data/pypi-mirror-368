"""Type definitions for Athena API."""
from enum import Enum
from typing import Any, Dict, List, TypedDict, NotRequired, Optional, Type
from dataclasses import dataclass
from typing import TypeVar, Generic
from datetime import datetime


from chainsaws.aws.shared.config import APIConfig


@dataclass
class AthenaAPIConfig(APIConfig):
    """Configuration for AthenaAPI."""

    workgroup: str = "primary"  # Workgroup to execute queries
    result_store_bucket: str  # S3 bucket name for storing Athena query results and metadata
    database: str  # Default database name
    output_location: Optional[str] = None  # S3 location to store query results

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.result_store_bucket:
            raise ValueError("result_store_bucket is required")
        if not self.database:
            raise ValueError("database is required")

    def get_output_location(self) -> str:
        """Get the S3 output location for query results.

        Returns:
            str: S3 URI for query results
        """
        if self.output_location:
            return self.output_location
        return f"s3://{self.result_store_bucket}/chainsaws-athena-results/"


class QueryExecutionState(str, Enum):
    """State of query execution."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class QueryExecutionStatistics(TypedDict):
    """Statistics about query execution."""
    EngineExecutionTimeInMillis: int
    DataScannedInBytes: int
    TotalExecutionTimeInMillis: int
    QueryQueueTimeInMillis: int
    ServiceProcessingTimeInMillis: int


class QueryExecutionStatus(TypedDict):
    """Status information about query execution."""
    State: QueryExecutionState
    StateChangeReason: NotRequired[str]
    SubmissionDateTime: str
    CompletionDateTime: NotRequired[str]


class QueryExecution(TypedDict):
    """Information about query execution."""
    QueryExecutionId: str
    Query: str
    StatementType: str
    ResultConfiguration: Dict[str, str]
    QueryExecutionContext: Dict[str, str]
    Status: QueryExecutionStatus
    Statistics: NotRequired[QueryExecutionStatistics]
    WorkGroup: str


class ColumnInfo(TypedDict):
    """Information about a column in the result set."""
    CatalogName: str
    SchemaName: str
    TableName: str
    Name: str
    Label: str
    Type: str
    Precision: int
    Scale: int
    Nullable: str
    CaseSensitive: bool


class ResultSet(TypedDict):
    """Query result set."""
    Rows: List[Dict[str, Any]]
    ResultSetMetadata: Dict[str, List[ColumnInfo]]


class QueryResult(TypedDict):
    """Complete query execution result."""
    QueryExecutionId: str
    Query: str
    State: QueryExecutionState
    StateChangeReason: NotRequired[str]
    Statistics: NotRequired[QueryExecutionStatistics]
    ResultSet: NotRequired[ResultSet]


class DatabaseProperties(TypedDict, total=False):
    """Properties of an Athena database."""

    Comment: str
    LocationUri: str
    Parameters: Dict[str, str]


class Database(TypedDict):
    """Represents an Athena database."""

    Name: str
    Description: Optional[str]
    Properties: Optional[DatabaseProperties]


class ListDatabasesResponse(TypedDict):
    """Response from list_databases operation."""

    DatabaseList: List[Database]
    NextToken: Optional[str]


class TableColumn(TypedDict):
    """Column in a table."""
    Name: str
    Type: str
    Comment: NotRequired[str]


class TableProperties(TypedDict, total=False):
    """Properties of a table."""
    Comment: str
    Parameters: Dict[str, str]
    TableType: str
    Location: str


class Table(TypedDict):
    """Represents an Athena table."""
    Name: str
    DatabaseName: str
    Description: NotRequired[str]
    Columns: List[TableColumn]
    Properties: NotRequired[TableProperties]


class ListTablesResponse(TypedDict):
    """Response from list_tables operation."""
    TableList: List[Table]
    NextToken: Optional[str]


class WorkGroupConfiguration(TypedDict):
    """Configuration for a workgroup."""
    ResultConfiguration: NotRequired[Dict[str, str]]
    EnforceWorkGroupConfiguration: NotRequired[bool]
    PublishCloudWatchMetricsEnabled: NotRequired[bool]
    RequesterPaysEnabled: NotRequired[bool]
    EngineVersion: NotRequired[Dict[str, str]]


class WorkGroupState(str, Enum):
    """State of a workgroup."""
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class WorkGroup(TypedDict):
    """Represents an Athena workgroup."""
    Name: str
    State: WorkGroupState
    Description: NotRequired[str]
    Configuration: WorkGroupConfiguration


class ListWorkGroupsResponse(TypedDict):
    """Response from list_workgroups operation."""
    WorkGroups: List[WorkGroup]
    NextToken: Optional[str]


class WorkGroupSummary(TypedDict):
    """Summary information about a workgroup."""
    Name: str
    State: WorkGroupState
    Description: NotRequired[str]
    CreationTime: str


class QueryAnalysis(TypedDict):
    """Analysis of a query execution."""
    ExecutionTime: float
    DataScanned: float
    CostEstimate: float
    EngineVersion: str
    Statistics: QueryExecutionStatistics
    RecommendedOptimizations: List[str]


class PartitionValue(TypedDict):
    """Represents a partition value."""
    Values: List[str]
    StorageLocation: str


class PartitionResponse(TypedDict):
    """Response from partition operations."""
    Partitions: List[PartitionValue]
    NextToken: Optional[str]


T = TypeVar('T')


@dataclass
class TypedQueryResult(Generic[T]):
    """Typed query result with metadata."""

    data: List[T]
    execution_time: float
    scanned_bytes: int
    row_count: int
    execution_id: str
    completed_at: datetime

    @classmethod
    def from_query_result(cls, result: Dict[str, Any], output_type: Type[T]) -> 'TypedQueryResult[T]':
        """Create TypedQueryResult from raw query result."""
        stats = result.get("Statistics", {})
        rows = result.get("ResultSet", {}).get("Rows", [])

        # Convert raw rows to typed objects
        column_info = result.get("ResultSet", {}).get(
            "ResultSetMetadata", {}).get("ColumnInfo", [])
        column_names = [col.get("Name") for col in column_info]

        # Skip header row
        data_rows = rows[1:] if rows else []

        # Convert each row to the output type
        typed_data = []
        for row in data_rows:
            row_data = {}
            for i, value in enumerate(row.get("Data", [])):
                if i < len(column_names):
                    row_data[column_names[i]] = value.get("VarCharValue")
            typed_data.append(output_type(**row_data))

        return cls(
            data=typed_data,
            execution_time=float(
                stats.get("TotalExecutionTimeInMillis", 0)) / 1000,
            scanned_bytes=int(stats.get("DataScannedInBytes", 0)),
            row_count=len(data_rows),
            execution_id=result.get("QueryExecutionId", ""),
            completed_at=datetime.now()
        )


@dataclass
class QueryPerformanceReport:
    """Query performance analysis report."""

    execution_time: float
    data_scanned: int
    cost_estimate: float
    engine_version: str
    suggestions: List[str]
    risk_level: str  # 'LOW', 'MEDIUM', 'HIGH'
    bottlenecks: List[str]
    optimization_tips: List[str]
    partition_info: Optional[Dict[str, Any]] = None
    join_info: Optional[Dict[str, Any]] = None


@dataclass
class DetailedError:
    """Detailed error information with suggestions."""

    error_code: str
    message: str
    details: Dict[str, Any]
    suggestions: List[str]
    query_stage: str
    error_location: Optional[str] = None
    error_type: str = "UNKNOWN"

    @property
    def is_recoverable(self) -> bool:
        """Check if the error is recoverable."""
        unrecoverable_codes = {
            "INVALID_INPUT", "PERMISSION_DENIED", "RESOURCE_NOT_FOUND"
        }
        return self.error_code not in unrecoverable_codes

    @property
    def has_quick_fix(self) -> bool:
        """Check if the error has a quick fix suggestion."""
        return len(self.suggestions) > 0
