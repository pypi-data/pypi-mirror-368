"""ElastiCache API models."""

from typing import Any, Dict, List, Literal, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field

from chainsaws.aws.shared.config import APIConfig


@dataclass
class ElastiCacheAPIConfig(APIConfig):
    """ElastiCache API configuration."""

    max_retries: int = 3  # Maximum number of retry attempts (0-10)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 0 <= self.max_retries <= 10:
            raise ValueError("max_retries must be between 0 and 10")


# General Purpose
GeneralPurposeNodeType = Literal[
    # M7g
    "cache.m7g.large", "cache.m7g.xlarge", "cache.m7g.2xlarge", "cache.m7g.4xlarge",
    "cache.m7g.8xlarge", "cache.m7g.12xlarge", "cache.m7g.16xlarge",
    # M6g
    "cache.m6g.large", "cache.m6g.xlarge", "cache.m6g.2xlarge", "cache.m6g.4xlarge",
    "cache.m6g.8xlarge", "cache.m6g.12xlarge", "cache.m6g.16xlarge",
    # M5
    "cache.m5.large", "cache.m5.xlarge", "cache.m5.2xlarge", "cache.m5.4xlarge",
    "cache.m5.12xlarge", "cache.m5.24xlarge",
    # M4
    "cache.m4.large", "cache.m4.xlarge", "cache.m4.2xlarge", "cache.m4.4xlarge",
    "cache.m4.10xlarge",
    # T4g
    "cache.t4g.micro", "cache.t4g.small", "cache.t4g.medium",
    # T3
    "cache.t3.micro", "cache.t3.small", "cache.t3.medium",
    # T2
    "cache.t2.micro", "cache.t2.small", "cache.t2.medium"
]

# Memory Optimized
MemoryOptimizedNodeType = Literal[
    # R7g
    "cache.r7g.large", "cache.r7g.xlarge", "cache.r7g.2xlarge", "cache.r7g.4xlarge",
    "cache.r7g.8xlarge", "cache.r7g.12xlarge", "cache.r7g.16xlarge",
    # R6g
    "cache.r6g.large", "cache.r6g.xlarge", "cache.r6g.2xlarge", "cache.r6g.4xlarge",
    "cache.r6g.8xlarge", "cache.r6g.12xlarge", "cache.r6g.16xlarge",
    # R5
    "cache.r5.large", "cache.r5.xlarge", "cache.r5.2xlarge", "cache.r5.4xlarge",
    "cache.r5.12xlarge", "cache.r5.24xlarge",
    # R4
    "cache.r4.large", "cache.r4.xlarge", "cache.r4.2xlarge", "cache.r4.4xlarge",
    "cache.r4.8xlarge", "cache.r4.16xlarge"
]

# Memory Optimized with Data Tiering
MemoryOptimizedWithDataTieringNodeType = Literal[
    "cache.r6gd.xlarge", "cache.r6gd.2xlarge", "cache.r6gd.4xlarge",
    "cache.r6gd.8xlarge", "cache.r6gd.12xlarge", "cache.r6gd.16xlarge"
]

# Network Optimized
NetworkOptimizedNodeType = Literal[
    "cache.c7gn.large", "cache.c7gn.xlarge", "cache.c7gn.2xlarge", "cache.c7gn.4xlarge",
    "cache.c7gn.8xlarge", "cache.c7gn.12xlarge", "cache.c7gn.16xlarge"
]

# Serverless Configuration


@dataclass
class ServerlessScalingConfiguration:
    """Serverless scaling configuration."""

    # Minimum capacity in ElastiCache Capacity Units (ECU)
    minimum_capacity: float = 0.5
    # Maximum capacity in ElastiCache Capacity Units (ECU)
    maximum_capacity: float = 100.0

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not 0.5 <= self.minimum_capacity <= 100.0:
            raise ValueError("minimum_capacity must be between 0.5 and 100.0")
        if not 0.5 <= self.maximum_capacity <= 100.0:
            raise ValueError("maximum_capacity must be between 0.5 and 100.0")
        if self.minimum_capacity > self.maximum_capacity:
            raise ValueError(
                "minimum_capacity cannot be greater than maximum_capacity")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "minimum_capacity": self.minimum_capacity,
            "maximum_capacity": self.maximum_capacity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerlessScalingConfiguration":
        """Create instance from dictionary."""
        return cls(
            minimum_capacity=data.get("minimum_capacity", 0.5),
            maximum_capacity=data.get("maximum_capacity", 100.0)
        )


# Serverless Cache Type
ServerlessType = Literal["serverless"]

# Combined node types including serverless
NodeInstanceType = Union[
    GeneralPurposeNodeType,
    MemoryOptimizedNodeType,
    MemoryOptimizedWithDataTieringNodeType,
    NetworkOptimizedNodeType,
    ServerlessType
]


@dataclass
class NodeType:
    """Node type configuration for ElastiCache clusters."""

    instance_type: NodeInstanceType
    num_nodes: int = 1
    serverless_config: Optional[ServerlessScalingConfiguration] = None

    def __post_init__(self):
        """Validate serverless configuration."""
        if self.instance_type == "serverless":
            if not self.serverless_config:
                self.serverless_config = ServerlessScalingConfiguration()
            self.num_nodes = 1  # Serverless always uses 1 node


@dataclass
class RedisConfig:
    """Redis specific configuration."""

    version: str  # Redis engine version
    port: int = 6379  # Port number
    auth_token: Optional[str] = None  # Auth token for Redis AUTH
    transit_encryption: bool = True  # Enable in-transit encryption
    at_rest_encryption: bool = True  # Enable at-rest encryption
    auto_failover: bool = True  # Enable auto-failover
    multi_az: bool = True  # Enable Multi-AZ
    backup_retention: int = 7  # Backup retention period in days
    backup_window: Optional[str] = None  # Preferred backup window
    maintenance_window: Optional[str] = None  # Preferred maintenance window
    parameter_group: Optional[str] = None  # Cache parameter group
    is_serverless: bool = False  # Whether this is a serverless configuration

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not 0 <= self.backup_retention <= 35:
            raise ValueError("backup_retention must be between 0 and 35 days")
        if self.port < 1 or self.port > 65535:
            raise ValueError("port must be between 1 and 65535")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "version": self.version,
            "port": self.port,
            "auth_token": self.auth_token,
            "transit_encryption": self.transit_encryption,
            "at_rest_encryption": self.at_rest_encryption,
            "auto_failover": self.auto_failover,
            "multi_az": self.multi_az,
            "backup_retention": self.backup_retention,
            "backup_window": self.backup_window,
            "maintenance_window": self.maintenance_window,
            "parameter_group": self.parameter_group,
            "is_serverless": self.is_serverless
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedisConfig":
        """Create instance from dictionary."""
        return cls(
            version=data["version"],
            port=data.get("port", 6379),
            auth_token=data.get("auth_token"),
            transit_encryption=data.get("transit_encryption", True),
            at_rest_encryption=data.get("at_rest_encryption", True),
            auto_failover=data.get("auto_failover", True),
            multi_az=data.get("multi_az", True),
            backup_retention=data.get("backup_retention", 7),
            backup_window=data.get("backup_window"),
            maintenance_window=data.get("maintenance_window"),
            parameter_group=data.get("parameter_group"),
            is_serverless=data.get("is_serverless", False)
        )


@dataclass
class MemcachedConfig:
    """Memcached specific configuration."""

    version: str  # Memcached engine version
    port: int = 11211  # Port number
    parameter_group: Optional[str] = None  # Cache parameter group

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.port < 1 or self.port > 65535:
            raise ValueError("port must be between 1 and 65535")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "version": self.version,
            "port": self.port,
            "parameter_group": self.parameter_group
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemcachedConfig":
        """Create instance from dictionary."""
        return cls(
            version=data["version"],
            port=data.get("port", 11211),
            parameter_group=data.get("parameter_group")
        )


@dataclass
class SubnetGroup:
    """Subnet group configuration."""

    name: str  # The name of the subnet group
    description: str  # Description for the subnet group
    subnet_ids: List[str]  # List of VPC subnet IDs

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "subnet_ids": self.subnet_ids
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubnetGroup":
        """Create instance from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            subnet_ids=data["subnet_ids"]
        )


@dataclass
class SecurityGroup:
    """Security group configuration."""

    id: str  # The ID of the security group
    name: Optional[str] = None  # The name of the security group

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityGroup":
        """Create instance from dictionary."""
        return cls(
            id=data["id"],
            name=data.get("name")
        )


# Engine Types
EngineType = Literal["redis", "memcached", "valkey"]


@dataclass
class ValKeyConfig:
    """ValKey specific configuration."""

    version: str  # ValKey engine version
    port: int = 6379  # Port number
    auth_token: Optional[str] = None  # Auth token for ValKey AUTH
    transit_encryption: bool = True  # Enable in-transit encryption
    at_rest_encryption: bool = True  # Enable at-rest encryption
    auto_failover: bool = True  # Enable auto-failover
    multi_az: bool = True  # Enable Multi-AZ
    backup_retention: int = 7  # Backup retention period in days
    backup_window: Optional[str] = None  # Preferred backup window
    maintenance_window: Optional[str] = None  # Preferred maintenance window
    parameter_group: Optional[str] = None  # Cache parameter group
    enhanced_io: bool = True  # Enable Enhanced I/O
    tls_offloading: bool = True  # Enable TLS Offloading
    enhanced_io_multiplexing: bool = True  # Enable Enhanced I/O Multiplexing

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not 0 <= self.backup_retention <= 35:
            raise ValueError("backup_retention must be between 0 and 35 days")
        if self.port < 1 or self.port > 65535:
            raise ValueError("port must be between 1 and 65535")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "version": self.version,
            "port": self.port,
            "auth_token": self.auth_token,
            "transit_encryption": self.transit_encryption,
            "at_rest_encryption": self.at_rest_encryption,
            "auto_failover": self.auto_failover,
            "multi_az": self.multi_az,
            "backup_retention": self.backup_retention,
            "backup_window": self.backup_window,
            "maintenance_window": self.maintenance_window,
            "parameter_group": self.parameter_group,
            "enhanced_io": self.enhanced_io,
            "tls_offloading": self.tls_offloading,
            "enhanced_io_multiplexing": self.enhanced_io_multiplexing
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValKeyConfig":
        """Create instance from dictionary."""
        return cls(
            version=data["version"],
            port=data.get("port", 6379),
            auth_token=data.get("auth_token"),
            transit_encryption=data.get("transit_encryption", True),
            at_rest_encryption=data.get("at_rest_encryption", True),
            auto_failover=data.get("auto_failover", True),
            multi_az=data.get("multi_az", True),
            backup_retention=data.get("backup_retention", 7),
            backup_window=data.get("backup_window"),
            maintenance_window=data.get("maintenance_window"),
            parameter_group=data.get("parameter_group"),
            enhanced_io=data.get("enhanced_io", True),
            tls_offloading=data.get("tls_offloading", True),
            enhanced_io_multiplexing=data.get("enhanced_io_multiplexing", True)
        )


@dataclass
class CreateClusterRequest:
    """Request model for creating an ElastiCache cluster."""

    cluster_id: str  # Unique identifier for the cluster
    engine: EngineType  # Cache engine type
    node_type: NodeType  # Node type configuration
    redis_config: Optional[RedisConfig] = None  # Redis specific configuration
    # Memcached specific configuration
    memcached_config: Optional[MemcachedConfig] = None
    # ValKey specific configuration
    valkey_config: Optional[ValKeyConfig] = None
    subnet_group: Optional[SubnetGroup] = None  # Subnet group configuration
    security_groups: Optional[List[SecurityGroup]] = None  # Security groups
    tags: Dict[str, str] = field(default_factory=dict)  # Resource tags

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.cluster_id:
            raise ValueError("cluster_id is required")

        # Validate engine-specific configuration
        if self.engine == "redis" and not self.redis_config:
            raise ValueError("redis_config is required for Redis engine")
        elif self.engine == "memcached" and not self.memcached_config:
            raise ValueError(
                "memcached_config is required for Memcached engine")
        elif self.engine == "valkey" and not self.valkey_config:
            raise ValueError("valkey_config is required for ValKey engine")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "cluster_id": self.cluster_id,
            "engine": self.engine,
            "node_type": self.node_type.to_dict() if hasattr(self.node_type, "to_dict") else self.node_type,
            "tags": self.tags
        }

        if self.redis_config:
            result["redis_config"] = self.redis_config.to_dict()
        if self.memcached_config:
            result["memcached_config"] = self.memcached_config.to_dict()
        if self.valkey_config:
            result["valkey_config"] = self.valkey_config.to_dict()
        if self.subnet_group:
            result["subnet_group"] = self.subnet_group.to_dict()
        if self.security_groups:
            result["security_groups"] = [sg.to_dict()
                                         for sg in self.security_groups]

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateClusterRequest":
        """Create instance from dictionary."""
        node_type_data = data.get("node_type")
        if isinstance(node_type_data, dict):
            node_type = NodeType(**node_type_data)
        else:
            node_type = node_type_data

        redis_config = data.get("redis_config")
        if redis_config:
            redis_config = RedisConfig.from_dict(redis_config)

        memcached_config = data.get("memcached_config")
        if memcached_config:
            memcached_config = MemcachedConfig.from_dict(memcached_config)

        valkey_config = data.get("valkey_config")
        if valkey_config:
            valkey_config = ValKeyConfig.from_dict(valkey_config)

        subnet_group = data.get("subnet_group")
        if subnet_group:
            subnet_group = SubnetGroup.from_dict(subnet_group)

        security_groups = data.get("security_groups")
        if security_groups:
            security_groups = [SecurityGroup.from_dict(
                sg) for sg in security_groups]

        return cls(
            cluster_id=data["cluster_id"],
            engine=data["engine"],
            node_type=node_type,
            redis_config=redis_config,
            memcached_config=memcached_config,
            valkey_config=valkey_config,
            subnet_group=subnet_group,
            security_groups=security_groups,
            tags=data.get("tags", {})
        )


@dataclass
class ClusterStatus:
    """Status information for an ElastiCache cluster."""

    cluster_id: str  # The ID of the cache cluster
    status: str  # The status of the cluster
    node_type: NodeType  # Node type configuration
    engine: str  # Cache engine (redis/memcached)
    engine_version: str  # Engine version
    num_cache_nodes: int  # Number of cache nodes
    port: int  # Port number
    endpoint: Optional[str] = None  # Cluster endpoint
    subnet_group: Optional[str] = None  # Subnet group name
    security_groups: List[str] = field(
        default_factory=list)  # Security group IDs
    tags: Dict[str, str] = field(default_factory=dict)  # Resource tags


@dataclass
class ModifyClusterRequest:
    """Request model for modifying an ElastiCache cluster."""

    cluster_id: str  # The ID of the cache cluster
    node_type: Optional[NodeType] = None  # New node type configuration
    security_groups: Optional[List[SecurityGroup]
                              ] = None  # New security groups
    maintenance_window: Optional[str] = None  # New maintenance window
    engine_version: Optional[str] = None  # New engine version
    auth_token: Optional[str] = None  # New auth token (Redis only)
    tags: Optional[Dict[str, str]] = None  # New resource tags
    apply_immediately: bool = False  # Whether to apply changes immediately


@dataclass
class SnapshotConfig:
    """Snapshot configuration."""

    snapshot_name: str  # The name of the snapshot
    retention_period: int = 7  # Number of days to retain the snapshot
    target_bucket: Optional[str] = None  # S3 bucket for exporting snapshot

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 1 <= self.retention_period <= 35:
            raise ValueError("retention_period must be between 1 and 35 days")


@dataclass
class RestoreConfig:
    """Configuration for restoring from a snapshot."""

    snapshot_name: str  # The name of the snapshot to restore from
    target_cluster_id: str  # The ID for the new cluster
    node_type: Optional[NodeType] = None  # New node type configuration
    subnet_group: Optional[SubnetGroup] = None  # New subnet group
    port: Optional[int] = None  # New port number
    security_groups: Optional[List[SecurityGroup]] = None  # Security groups
    tags: Dict[str, str] = field(default_factory=dict)  # Resource tags


@dataclass
class ParameterType:
    """Parameter type definition."""

    name: str  # Parameter name
    value: Union[str, int, bool]  # Parameter value
    data_type: Literal["string", "integer", "boolean"]  # Parameter data type
    description: Optional[str] = None  # Parameter description
    modifiable: bool = True  # Whether the parameter can be modified
    # Minimum engine version required
    minimum_engine_version: Optional[str] = None
    allowed_values: Optional[str] = None  # Allowed values for the parameter


@dataclass
class CreateParameterGroupRequest:
    """Request model for creating a parameter group."""

    group_name: str  # The name of the parameter group
    group_family: str  # The family of the parameter group (e.g., redis6.x)
    description: str  # Description for the parameter group
    parameters: Optional[Dict[str, Union[str, int, bool]]
                         ] = None  # Initial parameter values


@dataclass
class ModifyParameterGroupRequest:
    """Request model for modifying a parameter group."""

    group_name: str  # Parameter group name
    parameters: Dict[str, str] = field(
        default_factory=dict)  # Parameter values to modify

    def __post_init__(self) -> None:
        """Validate request after initialization."""
        if not self.group_name:
            raise ValueError("group_name is required")
        if not self.parameters:
            raise ValueError("parameters is required")


@dataclass
class ParameterGroupStatus:
    """Parameter group status information."""

    group_name: str  # The name of the parameter group
    group_family: str  # The family of the parameter group
    description: str  # Description of the parameter group
    parameters: Dict[str, ParameterType] = field(
        default_factory=dict)  # Current parameter values


class EventSubscriptionConfig:
    """Configuration for event subscription."""

    subscription_name: str  # The name of the event subscription
    sns_topic_arn: str  # The ARN of the SNS topic
    source_type: str  # The type of source to monitor
    source_ids: Optional[List[str]] = None  # Source IDs to monitor
    # Event categories to subscribe to
    event_categories: Optional[List[str]] = None
    enabled: bool = True  # Whether the subscription is enabled
    tags: Dict[str, str] = field(default_factory=dict)  # Resource tags


@dataclass
class EventSubscriptionStatus:
    """Status information for an event subscription."""

    subscription_name: str  # The name of the event subscription
    sns_topic_arn: str  # The ARN of the SNS topic
    source_type: str  # The type of source being monitored
    # List of source IDs being monitored
    source_ids: List[str] = field(default_factory=list)
    # Event categories being monitored
    event_categories: List[str] = field(default_factory=list)
    enabled: bool  # Whether the subscription is enabled
    status: str  # The status of the subscription


@dataclass
class MetricRequest:
    """Request model for retrieving performance metrics."""

    metric_name: str  # The name of the metric
    cluster_id: str  # The ID of the cache cluster
    start_time: datetime  # Start time for metrics
    end_time: datetime  # End time for metrics
    period: int = 60  # Period in seconds
    statistics: List[str] = field(default_factory=lambda: [
                                  "Average"])  # Statistics to retrieve


@dataclass
class MetricDatapoint:
    """A single metric datapoint."""

    timestamp: datetime  # The timestamp of the datapoint
    value: float  # The value of the metric
    unit: str  # The unit of the metric


@dataclass
class MetricResponse:
    """Response model for performance metrics."""

    metric_name: str  # The name of the metric
    datapoints: List[MetricDatapoint] = field(
        default_factory=list)  # The metric datapoints
    namespace: str = "AWS/ElastiCache"  # The metric namespace


@dataclass
class ReplicationGroupConfig:
    """Configuration for creating/modifying a replication group."""

    group_id: str  # Replication group identifier
    description: str  # Replication group description
    node_type: NodeType  # Node type configuration
    engine: EngineType  # Cache engine type
    engine_version: str  # Cache engine version
    num_node_groups: int = 1  # Number of node groups
    replicas_per_node_group: int = 1  # Number of replicas per node group
    port: Optional[int] = None  # Port number
    subnet_group: Optional[str] = None  # Subnet group name
    security_groups: Optional[List[str]] = None  # Security group IDs
    auth_token: Optional[str] = None  # Auth token for Redis
    tags: Dict[str, str] = field(default_factory=dict)  # Resource tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.group_id:
            raise ValueError("group_id is required")
        if not self.description:
            raise ValueError("description is required")
        if not 1 <= self.num_node_groups <= 90:
            raise ValueError("num_node_groups must be between 1 and 90")
        if not 0 <= self.replicas_per_node_group <= 5:
            raise ValueError("replicas_per_node_group must be between 0 and 5")
        if self.port is not None and not 1024 <= self.port <= 65535:
            raise ValueError("port must be between 1024 and 65535")


@dataclass
class ReplicationGroupStatus:
    """Status information for a replication group."""

    group_id: str  # The ID of the replication group
    status: str  # The status of the replication group
    description: str  # Description of the replication group
    node_groups: List[Dict[str, Any]] = field(
        default_factory=list)  # Node group information
    automatic_failover: str  # Automatic failover status
    multi_az: bool  # Multi-AZ status
    endpoint: Optional[str] = None  # Primary endpoint address
    port: Optional[int] = None  # Port number


@dataclass
class MaintenanceWindow:
    """Maintenance window configuration."""

    day_of_week: int  # Day of week (0-6, Sunday=0)
    start_time: str  # Start time in UTC (HH:mm)
    duration_hours: int  # Duration in hours

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 0 <= self.day_of_week <= 6:
            raise ValueError("day_of_week must be between 0 and 6")
        if not 1 <= self.duration_hours <= 24:
            raise ValueError("duration_hours must be between 1 and 24")
        try:
            hour, minute = map(int, self.start_time.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError("start_time must be in format HH:mm")


@dataclass
class ModifyMaintenanceWindowRequest:
    """Request model for modifying maintenance window."""

    cluster_id: str  # Cluster identifier
    maintenance_window: MaintenanceWindow  # New maintenance window

    def __post_init__(self) -> None:
        """Validate request after initialization."""
        if not self.cluster_id:
            raise ValueError("cluster_id is required")


@dataclass
class CreateServerlessRequest:
    """Request to create a serverless cache."""
    cache_name: str
    description: Optional[str] = None
    major_engine_version: str = "7.0"  # Redis version
    daily_backup_window: Optional[str] = None  # Format: "04:00-05:00"
    backup_retention_period: Optional[int] = None  # 0-35 days
    security_group_ids: Optional[List[str]] = None
    subnet_ids: Optional[List[str]] = None
    kms_key_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    scaling: Optional[ServerlessScalingConfiguration] = None


@dataclass
class ServerlessStatus:
    """Status of a serverless cache."""
    cache_name: str
    status: str  # available, creating, modifying, deleting
    endpoint: Optional[str] = None
    reader_endpoint: Optional[str] = None
    major_engine_version: str = "7.0"
    daily_backup_window: Optional[str] = None
    backup_retention_period: Optional[int] = None
    security_group_ids: Optional[List[str]] = None
    subnet_ids: Optional[List[str]] = None
    kms_key_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    scaling: Optional[ServerlessScalingConfiguration] = None


@dataclass
class ModifyServerlessRequest:
    """Request to modify a serverless cache."""
    cache_name: str
    description: Optional[str] = None
    daily_backup_window: Optional[str] = None
    backup_retention_period: Optional[int] = None
    security_group_ids: Optional[List[str]] = None
    scaling: Optional[ServerlessScalingConfiguration] = None
    tags: Optional[Dict[str, str]] = None


@dataclass
class BulkUploadResult:
    """Result of a bulk upload operation."""

    # Dictionary of successful uploads mapping object_key to S3 URL
    successful: Dict[str, str] = field(default_factory=dict)
    # Dictionary of failed uploads mapping object_key to error message
    failed: Dict[str, str] = field(default_factory=dict)
