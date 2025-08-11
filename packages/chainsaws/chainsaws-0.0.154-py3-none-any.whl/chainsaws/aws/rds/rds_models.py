from datetime import datetime
from enum import Enum
from typing import Any
from dataclasses import dataclass, field

from chainsaws.aws.shared.config import APIConfig


class DatabaseEngine(str, Enum):
    """Supported database engines."""

    AURORA_MYSQL = "aurora-mysql"
    AURORA_POSTGRESQL = "aurora-postgresql"
    MYSQL = "mysql"
    POSTGRESQL = "postgres"
    MARIADB = "mariadb"
    ORACLE_SE = "oracle-se"        # Oracle Standard Edition
    ORACLE_SE1 = "oracle-se1"      # Oracle Standard Edition One
    ORACLE_SE2 = "oracle-se2"      # Oracle Standard Edition Two
    ORACLE_EE = "oracle-ee"        # Oracle Enterprise Edition
    SQLSERVER_SE = "sqlserver-se"  # SQL Server Standard Edition
    SQLSERVER_EX = "sqlserver-ex"  # SQL Server Express Edition
    SQLSERVER_WEB = "sqlserver-web"  # SQL Server Web Edition
    SQLSERVER_EE = "sqlserver-ee"  # SQL Server Enterprise Edition


class InstanceClass(str, Enum):
    """Available RDS instance classes."""

    MICRO = "db.t3.micro"
    SMALL = "db.t3.small"
    MEDIUM = "db.t3.medium"
    LARGE = "db.t3.large"
    XLARGE = "db.t3.xlarge"
    XXLARGE = "db.t3.2xlarge"

    M5_LARGE = "db.m5.large"
    M5_XLARGE = "db.m5.xlarge"
    M5_2XLARGE = "db.m5.2xlarge"
    M5_4XLARGE = "db.m5.4xlarge"
    M5_8XLARGE = "db.m5.8xlarge"
    M5_12XLARGE = "db.m5.12xlarge"
    M5_16XLARGE = "db.m5.16xlarge"
    M5_24XLARGE = "db.m5.24xlarge"

    R5_LARGE = "db.r5.large"
    R5_XLARGE = "db.r5.xlarge"
    R5_2XLARGE = "db.r5.2xlarge"
    R5_4XLARGE = "db.r5.4xlarge"
    R5_8XLARGE = "db.r5.8xlarge"
    R5_12XLARGE = "db.r5.12xlarge"
    R5_16XLARGE = "db.r5.16xlarge"
    R5_24XLARGE = "db.r5.24xlarge"


@dataclass
class DatabaseInstance:
    """Database instance details."""

    instance_identifier: str  # Instance identifier
    engine: DatabaseEngine  # Database engine
    status: str  # Instance status
    port: int  # Database port
    allocated_storage: int  # Allocated storage in GB
    instance_class: InstanceClass  # Instance class
    creation_time: datetime  # Instance creation time
    publicly_accessible: bool  # Public accessibility status
    availability_zone: str  # Availability zone
    endpoint: str | None = None  # Instance endpoint
    vpc_id: str | None = None  # VPC ID
    tags: dict[str, str] = field(default_factory=dict)  # Tags


@dataclass
class QueryConfig:
    """Configuration for database queries."""

    resource_arn: str  # RDS cluster/instance ARN
    secret_arn: str  # Secrets Manager ARN containing credentials
    database: str  # Database name
    sql: str  # SQL query
    schema: str | None = None  # Schema name
    parameters: list[dict[str, Any]] = field(
        default_factory=list)  # Query parameters
    transaction_id: str | None = None  # Transaction ID for transaction operations


@dataclass
class QueryResult:
    """Query execution result."""

    columns: list[str]  # Column names
    rows: list[dict[str, Any]]  # Result rows
    row_count: int  # Number of affected rows
    generated_fields: list[Any] | None = None  # Auto-generated field values


@dataclass
class TransactionConfig:
    """Configuration for database transactions."""

    resource_arn: str  # RDS cluster/instance ARN
    secret_arn: str  # Secrets Manager ARN containing credentials
    database: str  # Database name
    schema: str | None = None  # Schema name
    isolation_level: str | None = None  # Transaction isolation level


@dataclass
class SnapshotConfig:
    """Configuration for DB snapshots."""

    snapshot_identifier: str  # Snapshot identifier
    instance_identifier: str  # Source instance identifier
    tags: dict[str, str] = field(default_factory=dict)  # Snapshot tags


@dataclass
class DBSnapshot:
    """Database snapshot details."""

    snapshot_identifier: str  # Snapshot identifier
    instance_identifier: str  # Source instance identifier
    creation_time: datetime  # Snapshot creation time
    status: str  # Snapshot status
    engine: DatabaseEngine  # Database engine
    allocated_storage: int  # Allocated storage in GB
    availability_zone: str  # Availability zone
    tags: dict[str, str] = field(default_factory=dict)  # Tags


@dataclass
class ParameterGroupConfig:
    """Configuration for DB parameter groups."""

    group_name: str  # Parameter group name
    family: str  # Parameter group family
    description: str  # Parameter group description
    parameters: dict[str, str] = field(
        default_factory=dict)  # Parameter name-value pairs
    tags: dict[str, str] = field(default_factory=dict)  # Tags


@dataclass
class MetricConfig:
    """Configuration for RDS metrics retrieval."""

    instance_identifier: str  # Instance identifier
    metric_name: str  # CloudWatch metric name
    start_time: datetime  # Start time for metrics
    end_time: datetime  # End time for metrics
    period: int = 60  # Period in seconds
    statistics: list[str] = field(
        default_factory=lambda: ["Average"])  # Statistics to retrieve


@dataclass
class ReadReplicaConfig:
    """Configuration for read replicas."""

    source_instance_identifier: str  # Source instance identifier
    replica_identifier: str  # Replica identifier
    availability_zone: str | None = None  # Target availability zone
    instance_class: InstanceClass | None = None  # Replica instance class
    port: int | None = None  # Database port
    tags: dict[str, str] = field(default_factory=dict)  # Tags


@dataclass
class BatchExecuteStatementConfig:
    """Configuration for batch SQL statement execution."""

    resource_arn: str  # RDS cluster/instance ARN
    secret_arn: str  # Secrets Manager ARN containing credentials
    database: str  # Database name
    sql: str  # SQL statement to execute
    # List of parameter sets for batch execution
    parameter_sets: list[list[dict[str, Any]]]
    schema: str | None = None  # Schema name
    transaction_id: str | None = None  # Transaction ID for transaction operations


@dataclass
class BatchExecuteResult:
    """Result of batch statement execution."""

    update_results: list[dict[str, Any]] = field(
        default_factory=list)  # Results for update operations
    generated_fields: list[list[Any]] = field(
        default_factory=list)  # Auto-generated field values for each statement


@dataclass
class ModifyInstanceConfig:
    """Configuration for modifying DB instance."""

    instance_identifier: str  # Instance identifier
    instance_class: InstanceClass | None = None  # New instance class
    allocated_storage: int | None = None  # New storage size in GB
    master_password: str | None = None  # New master password
    backup_retention_period: int | None = None  # Backup retention days
    preferred_backup_window: str | None = None  # Preferred backup window
    preferred_maintenance_window: str | None = None  # Preferred maintenance window
    multi_az: bool | None = None  # Enable Multi-AZ deployment
    auto_minor_version_upgrade: bool | None = None  # Auto minor version upgrade
    apply_immediately: bool = False  # Apply changes immediately


@dataclass
class PerformanceInsightConfig:
    """Configuration for Performance Insights."""

    instance_identifier: str  # Instance identifier
    start_time: datetime  # Start time for metrics
    end_time: datetime  # End time for metrics
    metric_queries: list[dict[str, Any]]  # Performance metric queries
    max_results: int | None = None  # Maximum number of results


class LogType(str, Enum):
    """Available RDS log types."""

    POSTGRESQL = "postgresql"
    POSTGRESQL_UPGRADE = "postgresql.log"
    UPGRADE = "upgrade"
    ERROR = "error"
    GENERAL = "general"
    SLOW = "slowquery"
    AUDIT = "audit"


class EventCategory(str, Enum):
    """RDS event categories."""

    AVAILABILITY = "availability"
    BACKUP = "backup"
    CONFIGURATION = "configuration"
    CREATION = "creation"
    DELETION = "deletion"
    FAILOVER = "failover"
    FAILURE = "failure"
    MAINTENANCE = "maintenance"
    NOTIFICATION = "notification"
    RECOVERY = "recovery"
    RESTORATION = "restoration"
    READ_REPLICA = "read-replica"


@dataclass
class BackupWindow:
    """Configuration for backup window."""

    instance_identifier: str  # Instance identifier
    preferred_window: str  # Preferred backup window (UTC)
    retention_period: int = 7  # Backup retention period in days


@dataclass
class EventSubscriptionConfig:
    """Configuration for event subscriptions."""

    subscription_name: str  # Subscription name
    sns_topic_arn: str  # SNS topic ARN
    source_type: str  # Source type (e.g., db-instance)
    event_categories: list[EventCategory]  # Event categories to subscribe to
    source_ids: list[str] | None = None  # Source identifiers
    enabled: bool = True  # Subscription enabled state
    tags: dict[str, str] = field(default_factory=dict)  # Resource tags


@dataclass
class EventSubscription:
    """Event subscription details."""

    subscription_name: str  # Subscription name
    sns_topic_arn: str  # SNS topic ARN
    status: str  # Subscription status
    source_type: str  # Source type
    event_categories: list[EventCategory]  # Subscribed event categories
    source_ids: list[str]  # Source identifiers
    enabled: bool  # Subscription enabled state
    creation_time: datetime  # Subscription creation time
    tags: dict[str, str] = field(default_factory=dict)  # Resource tags


@dataclass
class RDSAPIConfig(APIConfig):
    """Configuration for RDS API."""

    default_region: str = "ap-northeast-2"  # Default AWS region for RDS operations
    max_retries: int = 3  # Maximum number of API retry attempts
    timeout: int = 30  # Timeout for API calls in seconds
    retry_modes: dict[str, Any] = field(
        default_factory=lambda: {
            "max_attempts": 3,
            "mode": "adaptive",
        }
    )  # Retry configuration


@dataclass
class DatabaseInstanceConfig:
    """Configuration for database instance creation."""

    instance_identifier: str  # Unique instance identifier
    engine: DatabaseEngine  # Database engine
    instance_class: InstanceClass  # Instance class
    master_username: str  # Master user name
    master_password: str  # Master user password
    vpc_security_group_ids: list[str]  # VPC security group IDs
    engine_version: str | None = None  # Engine version
    allocated_storage: int = 20  # Allocated storage in GB
    availability_zone: str | None = None  # Preferred availability zone
    db_subnet_group_name: str | None = None  # DB subnet group name
    port: int | None = None  # Database port
    db_name: str | None = None  # Initial database name
    backup_retention_period: int = 7  # Backup retention period in days
    tags: dict[str, str] = field(default_factory=dict)  # Resource tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.instance_identifier:
            raise ValueError("instance_identifier is required")
        if not self.master_username:
            raise ValueError("master_username is required")
        if not self.master_password:
            raise ValueError("master_password is required")
        if not self.vpc_security_group_ids:
            raise ValueError("vpc_security_group_ids is required")
        if self.allocated_storage < 20:
            raise ValueError("allocated_storage must be at least 20 GB")
        if self.port is not None and not 1150 <= self.port <= 65535:
            raise ValueError("port must be between 1150 and 65535")


class BackupType(str, Enum):
    """Types of RDS backups."""

    AUTOMATED = "automated"
    MANUAL = "manual"
    SNAPSHOT = "snapshot"


@dataclass
class BackupConfig:
    """Configuration for database backup."""

    instance_identifier: str  # Instance identifier
    backup_identifier: str  # Backup identifier
    backup_type: BackupType = BackupType.MANUAL  # Type of backup
    copy_tags: bool = True  # Copy instance tags to backup
    tags: dict[str, str] = field(default_factory=dict)  # Backup tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.instance_identifier:
            raise ValueError("instance_identifier is required")
        if not self.backup_identifier:
            raise ValueError("backup_identifier is required")


@dataclass
class RestoreConfig:
    """Configuration for database restore."""

    source_identifier: str  # Source backup identifier
    target_identifier: str  # Target instance identifier
    # Instance class for restored instance
    instance_class: InstanceClass | None = None
    availability_zone: str | None = None  # Target availability zone
    port: int | None = None  # Database port
    multi_az: bool = False  # Enable Multi-AZ deployment
    vpc_security_group_ids: list[str] | None = None  # VPC security group IDs
    tags: dict[str, str] = field(default_factory=dict)  # Instance tags
    point_in_time: datetime | None = None  # Point-in-time to restore to

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.source_identifier:
            raise ValueError("source_identifier is required")
        if not self.target_identifier:
            raise ValueError("target_identifier is required")
        if self.port is not None and not 1150 <= self.port <= 65535:
            raise ValueError("port must be between 1150 and 65535")
