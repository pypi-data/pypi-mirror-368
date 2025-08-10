"""Builder classes for ElastiCache API requests."""

from typing import Dict, List, Optional, Union, Literal
from datetime import datetime

from chainsaws.aws.elasticache.elasticache_models import (
    CreateClusterRequest,
    CreateParameterGroupRequest,
    EventSubscriptionRequest,
    MetricRequest,
    NodeType,
    RedisConfig,
    MemcachedConfig,
    ReplicationGroupRequest,
    SecurityGroup,
    SubnetGroup,
)


class ParameterGroupBuilder:
    """Builder for parameter group configuration."""

    def __init__(self, group_name: str, group_family: str) -> None:
        self.group_name = group_name
        self.group_family = group_family
        self.description = ""
        self.parameters: Dict[str, Union[str, int, bool]] = {}

    def with_description(self, description: str) -> "ParameterGroupBuilder":
        """Set the description."""
        self.description = description
        return self

    def with_parameter(self, name: str, value: Union[str, int, bool]) -> "ParameterGroupBuilder":
        """Add a parameter."""
        self.parameters[name] = value
        return self

    def with_parameters(self, parameters: Dict[str, Union[str, int, bool]]) -> "ParameterGroupBuilder":
        """Add multiple parameters."""
        self.parameters.update(parameters)
        return self

    def build(self) -> CreateParameterGroupRequest:
        """Build the parameter group request."""
        return CreateParameterGroupRequest(
            group_name=self.group_name,
            group_family=self.group_family,
            description=self.description,
            parameters=self.parameters,
        )


class EventSubscriptionBuilder:
    """Builder for event subscription configuration."""

    def __init__(self, subscription_name: str, sns_topic_arn: str) -> None:
        self.subscription_name = subscription_name
        self.sns_topic_arn = sns_topic_arn
        self.source_type: Literal["cache-cluster", "cache-parameter-group",
                                  "cache-security-group", "cache-subnet-group"] = "cache-cluster"
        self.source_ids: Optional[List[str]] = None
        self.event_categories: Optional[List[str]] = None
        self.enabled = True
        self.tags: Dict[str, str] = {}

    def with_source_type(self, source_type: Literal["cache-cluster", "cache-parameter-group",
                                                    "cache-security-group", "cache-subnet-group"]) -> "EventSubscriptionBuilder":
        """Set the source type."""
        self.source_type = source_type
        return self

    def with_source_ids(self, source_ids: List[str]) -> "EventSubscriptionBuilder":
        """Set the source IDs to monitor."""
        self.source_ids = source_ids
        return self

    def with_event_categories(self, categories: List[str]) -> "EventSubscriptionBuilder":
        """Set the event categories to monitor."""
        self.event_categories = categories
        return self

    def with_enabled(self, enabled: bool) -> "EventSubscriptionBuilder":
        """Set whether the subscription is enabled."""
        self.enabled = enabled
        return self

    def with_tags(self, tags: Dict[str, str]) -> "EventSubscriptionBuilder":
        """Add resource tags."""
        self.tags = tags
        return self

    def build(self) -> EventSubscriptionRequest:
        """Build the event subscription request."""
        return EventSubscriptionRequest(
            subscription_name=self.subscription_name,
            sns_topic_arn=self.sns_topic_arn,
            source_type=self.source_type,
            source_ids=self.source_ids,
            event_categories=self.event_categories,
            enabled=self.enabled,
            tags=self.tags,
        )


class MetricRequestBuilder:
    """Builder for metric request configuration."""

    def __init__(self, metric_name: str, cluster_id: str) -> None:
        self.metric_name = metric_name
        self.cluster_id = cluster_id
        self.period = 60
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.statistics = ["Average"]

    def with_period(self, period: int) -> "MetricRequestBuilder":
        """Set the granularity in seconds."""
        self.period = period
        return self

    def with_time_range(self, start_time: datetime, end_time: datetime) -> "MetricRequestBuilder":
        """Set the time range."""
        self.start_time = start_time
        self.end_time = end_time
        return self

    def with_statistics(self, statistics: List[Literal["Average", "Maximum", "Minimum", "Sum", "SampleCount"]]) -> "MetricRequestBuilder":
        """Set the statistics to retrieve."""
        self.statistics = statistics
        return self

    def build(self) -> MetricRequest:
        """Build the metric request."""
        if not self.start_time or not self.end_time:
            raise ValueError("Time range must be specified")

        return MetricRequest(
            metric_name=self.metric_name,
            cluster_id=self.cluster_id,
            period=self.period,
            start_time=self.start_time,
            end_time=self.end_time,
            statistics=self.statistics,
        )


class ReplicationGroupBuilder:
    """Builder for replication group configuration."""

    def __init__(self, group_id: str, description: str) -> None:
        self.group_id = group_id
        self.description = description
        self.instance_type = "cache.t3.micro"
        self.num_nodes = 1
        self.engine_version = "6.x"
        self.num_node_groups = 1
        self.replicas_per_node_group = 1
        self.automatic_failover = True
        self.multi_az = True
        self.subnet_group = None
        self.security_groups = None
        self.parameter_group = None
        self.port = 6379
        self.maintenance_window = None
        self.tags: Dict[str, str] = {}

    def with_node_type(self, instance_type: str, num_nodes: int = 1) -> "ReplicationGroupBuilder":
        """Set the node type configuration."""
        self.instance_type = instance_type
        self.num_nodes = num_nodes
        return self

    def with_engine_version(self, version: str) -> "ReplicationGroupBuilder":
        """Set the Redis engine version."""
        self.engine_version = version
        return self

    def with_sharding(self, num_node_groups: int, replicas_per_node_group: int) -> "ReplicationGroupBuilder":
        """Configure sharding settings."""
        self.num_node_groups = num_node_groups
        self.replicas_per_node_group = replicas_per_node_group
        return self

    def with_availability(self, automatic_failover: bool = True, multi_az: bool = True) -> "ReplicationGroupBuilder":
        """Configure availability settings."""
        self.automatic_failover = automatic_failover
        self.multi_az = multi_az
        return self

    def with_network(self, subnet_group: Optional[str] = None, security_groups: Optional[List[str]] = None) -> "ReplicationGroupBuilder":
        """Configure network settings."""
        self.subnet_group = subnet_group
        self.security_groups = security_groups
        return self

    def with_parameter_group(self, group_name: str) -> "ReplicationGroupBuilder":
        """Set the parameter group."""
        self.parameter_group = group_name
        return self

    def with_port(self, port: int) -> "ReplicationGroupBuilder":
        """Set the port number."""
        self.port = port
        return self

    def with_maintenance_window(self, window: str) -> "ReplicationGroupBuilder":
        """Set the maintenance window."""
        self.maintenance_window = window
        return self

    def with_tags(self, tags: Dict[str, str]) -> "ReplicationGroupBuilder":
        """Add resource tags."""
        self.tags = tags
        return self

    def build(self) -> ReplicationGroupRequest:
        """Build the replication group request."""
        return ReplicationGroupRequest(
            group_id=self.group_id,
            description=self.description,
            node_type=NodeType(
                instance_type=self.instance_type,
                num_nodes=self.num_nodes,
            ),
            engine_version=self.engine_version,
            num_node_groups=self.num_node_groups,
            replicas_per_node_group=self.replicas_per_node_group,
            automatic_failover=self.automatic_failover,
            multi_az=self.multi_az,
            subnet_group=SubnetGroup(
                name=self.subnet_group) if self.subnet_group else None,
            security_groups=[SecurityGroup(
                id=sg) for sg in self.security_groups] if self.security_groups else None,
            parameter_group=self.parameter_group,
            port=self.port,
            maintenance_window=self.maintenance_window,
            tags=self.tags,
        )


class ClusterBuilder:
    """Builder for ElastiCache cluster configuration."""

    def __init__(self, cluster_id: str, engine: Literal["redis", "memcached"]) -> None:
        self.cluster_id = cluster_id
        self.engine = engine
        self.instance_type = "cache.t3.micro"
        self.num_nodes = 1
        self.version = None
        self.port = None
        self.auth_token = None
        self.transit_encryption = True
        self.at_rest_encryption = True
        self.auto_failover = True
        self.multi_az = True
        self.backup_retention = 7
        self.backup_window = None
        self.maintenance_window = None
        self.parameter_group = None
        self.subnet_group = None
        self.security_groups = []
        self.tags = {}

    def with_node_type(self, instance_type: str, num_nodes: int = 1) -> "ClusterBuilder":
        """Set the node type configuration."""
        self.instance_type = instance_type
        self.num_nodes = num_nodes
        return self

    def with_version(self, version: str) -> "ClusterBuilder":
        """Set the engine version."""
        self.version = version
        return self

    def with_port(self, port: int) -> "ClusterBuilder":
        """Set the port number."""
        self.port = port
        return self

    def with_auth(self, auth_token: str) -> "ClusterBuilder":
        """Set the auth token (Redis only)."""
        self.auth_token = auth_token
        return self

    def with_encryption(self, transit: bool = True, at_rest: bool = True) -> "ClusterBuilder":
        """Configure encryption settings."""
        self.transit_encryption = transit
        self.at_rest_encryption = at_rest
        return self

    def with_availability(self, auto_failover: bool = True, multi_az: bool = True) -> "ClusterBuilder":
        """Configure availability settings."""
        self.auto_failover = auto_failover
        self.multi_az = multi_az
        return self

    def with_backup(self, retention_days: int = 7, backup_window: Optional[str] = None) -> "ClusterBuilder":
        """Configure backup settings."""
        self.backup_retention = retention_days
        self.backup_window = backup_window
        return self

    def with_maintenance_window(self, window: str) -> "ClusterBuilder":
        """Set the maintenance window."""
        self.maintenance_window = window
        return self

    def with_parameter_group(self, group_name: str) -> "ClusterBuilder":
        """Set the parameter group."""
        self.parameter_group = group_name
        return self

    def with_network(self, subnet_group: str, security_groups: List[str]) -> "ClusterBuilder":
        """Configure network settings."""
        self.subnet_group = subnet_group
        self.security_groups = security_groups
        return self

    def with_tags(self, tags: Dict[str, str]) -> "ClusterBuilder":
        """Add resource tags."""
        self.tags = tags
        return self

    def build(self) -> CreateClusterRequest:
        """Build the cluster request."""
        if self.engine == "redis":
            engine_config = RedisConfig(
                version=self.version or "6.x",
                port=self.port or 6379,
                auth_token=self.auth_token,
                transit_encryption=self.transit_encryption,
                at_rest_encryption=self.at_rest_encryption,
                auto_failover=self.auto_failover,
                multi_az=self.multi_az,
                backup_retention=self.backup_retention,
                backup_window=self.backup_window,
                maintenance_window=self.maintenance_window,
                parameter_group=self.parameter_group,
            )
            memcached_config = None
        else:
            engine_config = None
            memcached_config = MemcachedConfig(
                version=self.version or "1.6.6",
                port=self.port or 11211,
                parameter_group=self.parameter_group,
            )

        return CreateClusterRequest(
            cluster_id=self.cluster_id,
            engine=self.engine,
            node_type=NodeType(
                instance_type=self.instance_type,
                num_nodes=self.num_nodes,
            ),
            redis_config=engine_config,
            memcached_config=memcached_config,
            subnet_group=SubnetGroup(
                name=self.subnet_group) if self.subnet_group else None,
            security_groups=[SecurityGroup(
                id=sg) for sg in self.security_groups] if self.security_groups else None,
            tags=self.tags,
        )
