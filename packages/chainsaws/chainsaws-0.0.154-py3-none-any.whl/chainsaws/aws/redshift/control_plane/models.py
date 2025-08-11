"""Unified models for Redshift Control Plane operations."""

from datetime import datetime
from typing import List, Optional, Final
from dataclasses import dataclass, field


# Constants
UNLIMITED_CONNECTIONS: Final[int] = -1


@dataclass
class NodeType:
    """Redshift node type configuration."""

    name: str  # Node type identifier (e.g., dc2.large)
    vcpu: int  # Number of virtual CPUs
    memory_gb: int  # Memory in GB
    storage_gb: int  # Storage capacity in GB


@dataclass
class NetworkConfig:
    """Network configuration for Redshift cluster."""

    vpc_id: str  # VPC ID
    subnet_ids: List[str]  # List of subnet IDs
    security_group_ids: List[str]  # List of security group IDs
    publicly_accessible: bool = False  # Whether cluster is publicly accessible


@dataclass
class MaintenanceWindow:
    """Maintenance window configuration."""

    day_of_week: int  # Day of week (0-6)
    start_time: str  # Start time in UTC (HH:mm)
    duration_hours: int  # Duration in hours

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 0 <= self.day_of_week <= 6:
            raise ValueError("day_of_week must be between 0 and 6")
        if not 1 <= self.duration_hours <= 24:
            raise ValueError("duration_hours must be between 1 and 24")


@dataclass
class BackupConfig:
    """Backup configuration for Redshift cluster."""

    # Daily time when automated snapshots are taken (UTC HH:mm)
    automated_snapshot_start_time: str
    retention_period_days: int = 7  # Backup retention period in days

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.retention_period_days >= 1:
            raise ValueError("retention_period_days must be at least 1")


@dataclass
class ClusterConfig:
    """Configuration for creating/modifying a Redshift cluster."""

    cluster_identifier: str  # Unique cluster identifier
    node_type: str  # Node type (e.g., dc2.large)
    master_username: str  # Master user name
    master_user_password: str  # Master user password
    database_name: str  # Initial database name
    network: NetworkConfig  # Network configuration
    number_of_nodes: int = 1  # Number of compute nodes
    port: int = 5439  # Database port
    # Maintenance window configuration
    maintenance_window: Optional[MaintenanceWindow] = None
    backup: Optional[BackupConfig] = None  # Backup configuration
    encrypted: bool = True  # Whether to encrypt the cluster
    kms_key_id: Optional[str] = None  # KMS key ID for encryption
    tags: dict = field(default_factory=dict)  # Resource tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.number_of_nodes >= 1:
            raise ValueError("number_of_nodes must be at least 1")


@dataclass
class ClusterStatus:
    """Current status of a Redshift cluster."""

    cluster_identifier: str  # Cluster identifier
    status: str  # Current cluster status
    node_type: str  # Node type
    number_of_nodes: int  # Number of nodes
    availability_zone: str  # Availability zone
    vpc_id: str  # VPC ID
    publicly_accessible: bool  # Publicly accessible
    encrypted: bool  # Encrypted status
    database_name: str  # Database name
    master_username: str  # Master username
    automated_snapshot_retention_period: int  # Backup retention period
    cluster_security_groups: List[str]  # Security group IDs
    vpc_security_groups: List[str]  # VPC security group IDs
    preferred_maintenance_window: str  # Maintenance window
    cluster_version: str  # Redshift engine version
    allow_version_upgrade: bool  # Allow version upgrade
    total_storage_capacity_in_mega_bytes: int  # Total storage capacity
    aqua_configuration_status: str  # AQUA configuration status
    maintenance_track_name: str  # Maintenance track
    endpoint_address: Optional[str] = None  # Endpoint address
    endpoint_port: Optional[int] = None  # Endpoint port
    cluster_create_time: Optional[datetime] = None  # Cluster creation time
    number_of_nodes_ready: Optional[int] = None  # Number of nodes ready
    pending_modified_values: dict = field(
        default_factory=dict)  # Pending changes
    node_type_parameters: dict = field(
        default_factory=dict)  # Node type specific parameters
    default_iam_role_arn: Optional[str] = None  # Default IAM role ARN
    # Available node count options for elastic resize
    elastic_resize_number_of_node_options: Optional[str] = None
    deferred_maintenance_windows: List[dict] = field(
        default_factory=list)  # Deferred maintenance windows


@dataclass
class InboundRule:
    """Inbound security group rule."""

    protocol: str  # Protocol (tcp, udp, icmp)
    from_port: int  # Start port
    to_port: int  # End port
    cidr_ip: Optional[str] = None  # CIDR IP range
    security_group_id: Optional[str] = None  # Security group ID

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.cidr_ip and not self.security_group_id:
            raise ValueError(
                "Either cidr_ip or security_group_id must be specified")


@dataclass
class SecurityGroupConfig:
    """Configuration for creating/modifying a security group."""

    group_name: str  # Security group name
    description: str  # Security group description
    vpc_id: str  # VPC ID
    inbound_rules: List[InboundRule] = field(
        default_factory=list)  # Inbound rules
    tags: dict = field(default_factory=dict)  # Resource tags


@dataclass
class User:
    """Redshift database user."""

    username: str  # User name
    connection_limit: int = UNLIMITED_CONNECTIONS  # Maximum number of connections
    password: Optional[str] = None  # User password
    valid_until: Optional[str] = None  # Password validity period
    create_database: bool = False  # Permission to create databases
    superuser: bool = False  # Superuser status


@dataclass
class Group:
    """Redshift user group."""

    group_name: str  # Group name
    users: List[str] = field(default_factory=list)  # Group members


@dataclass
class Permission:
    """Database object permission."""

    database: str  # Database name
    permissions: List[str]  # Granted permissions
    schema: Optional[str] = None  # Schema name
    table: Optional[str] = None  # Table name


@dataclass
class GrantConfig:
    """Configuration for granting permissions."""

    grantee: str  # User or group name
    grantee_type: str  # USER or GROUP
    permissions: List[Permission]  # Permissions to grant


@dataclass
class ParameterValue:
    """Parameter value with metadata."""

    name: str  # Parameter name
    value: str  # Parameter value
    description: str  # Parameter description
    source: str  # Value source
    data_type: str  # Parameter data type
    allowed_values: str  # Allowed values
    apply_type: str  # static or dynamic
    is_modifiable: bool  # Whether parameter can be modified
    minimum_engine_version: str  # Minimum engine version required


@dataclass
class ParameterGroupFamily:
    """Redshift parameter group family."""

    name: str  # Family name
    description: str  # Family description
    engine: str  # Database engine
    engine_version: str  # Engine version


@dataclass
class ParameterGroupConfig:
    """Configuration for creating/modifying a parameter group."""

    name: str  # Parameter group name
    family: str  # Parameter group family
    description: Optional[str] = None  # Parameter group description
    parameters: Optional[dict[str, str]] = None  # Parameter values
    tags: dict[str, str] = field(default_factory=dict)  # Resource tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.name or len(self.name) > 255:
            raise ValueError("name must be between 1 and 255 characters")
        if not self.family:
            raise ValueError("family is required")


@dataclass
class ParameterGroupStatus:
    """Status information about a parameter group."""

    name: str  # Parameter group name
    family: str  # Parameter group family
    description: Optional[str] = None  # Parameter group description
    parameters: dict[str, str] = field(
        default_factory=dict)  # Current parameter values
    tags: dict[str, str] = field(default_factory=dict)  # Resource tags


@dataclass
class ParameterModification:
    """Parameter modification details."""

    parameter_name: str  # Name of the parameter
    current_value: str  # Current parameter value
    applied_value: str  # Value being applied
    modification_state: str  # State of the modification
    error_message: Optional[str] = None  # Error message if modification failed


@dataclass
class ApplyStatus:
    """Status of parameter modifications."""

    parameters_to_apply: list[str] = field(
        default_factory=list)  # Parameters pending application
    parameters_applied: list[str] = field(
        default_factory=list)  # Successfully applied parameters
    parameters_pending_reboot: list[str] = field(
        default_factory=list)  # Parameters requiring reboot
    error_parameters: dict[str, str] = field(
        default_factory=dict)  # Parameters with errors
