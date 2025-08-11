"""ElastiCache API for managing Redis and Memcached clusters."""

from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime
from botocore.exceptions import ClientError

from chainsaws.aws.elasticache._elasticache_internal import ElastiCache
from chainsaws.aws.elasticache.builder import (
    ClusterBuilder,
    EventSubscriptionBuilder,
    MetricRequestBuilder,
    ParameterGroupBuilder,
    ReplicationGroupBuilder,
)
from chainsaws.aws.elasticache.elasticache_models import (
    ClusterStatus,
    ElastiCacheAPIConfig,
    EventSubscriptionStatus,
    MetricResponse,
    ModifyClusterRequest,
    ModifyParameterGroupRequest,
    ParameterGroupStatus,
    ReplicationGroupStatus,
    RestoreClusterRequest,
    ServerlessScalingConfiguration,
    SnapshotConfig,
    ValKeyConfig,
    CreateServerlessRequest,
    ModifyServerlessRequest,
    ServerlessStatus,
)

from chainsaws.aws.shared import session
from .redis_client import RedisClient
from .memcached_client import MemcachedClient
from .valkey_client import ValKeyClient
from .dataplane_models import CacheConfig


class ElastiCacheAPI:
    """High-level API for managing ElastiCache clusters."""

    def __init__(
        self,
        config: Optional[ElastiCacheAPIConfig] = None,
    ) -> None:
        """Initialize ElastiCache API."""
        self.config = config or ElastiCacheAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.elasticache = ElastiCache(
            boto3_session=self.boto3_session,
            config=config,
        )

        # NOTE: Check ElastiCache dependencies once during initialization
        try:
            import redis  # noqa
            import pymemcache  # noqa
            self._has_elasticache_deps = True
        except ImportError:
            self._has_elasticache_deps = False

    def _check_elasticache_deps(self):
        """Check if ElastiCache dependencies are installed."""
        if not self._has_elasticache_deps:
            raise ImportError(
                "ElastiCache client dependencies not found. "
                "Please install them with: pip install chainsaws[elasticache]"
            )

    def create_cluster(
        self,
        cluster_id: str,
        engine: Literal["redis", "memcached", "valkey"],
        instance_type: str = "cache.t3.micro",
        num_nodes: int = 1,
        version: Optional[str] = None,
        port: Optional[int] = None,
        auth_token: Optional[str] = None,
        parameter_group: Optional[str] = None,
        subnet_group: Optional[str] = None,
        security_groups: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
        serverless_config: Optional[ServerlessScalingConfiguration] = None,
        valkey_config: Optional[ValKeyConfig] = None,
        **kwargs: Any,
    ) -> ClusterStatus:
        """Create a new ElastiCache cluster."""
        builder = ClusterBuilder(cluster_id, engine)

        # Handle serverless configuration
        if instance_type == "serverless":
            builder.with_node_type(
                instance_type, serverless_config=serverless_config)
        else:
            builder.with_node_type(instance_type, num_nodes)

        if version:
            builder.with_version(version)
        if port:
            builder.with_port(port)
        if auth_token:
            builder.with_auth(auth_token)
        if parameter_group:
            builder.with_parameter_group(parameter_group)
        if subnet_group and security_groups:
            builder.with_network(subnet_group, security_groups)
        if tags:
            builder.with_tags(tags)

        # Handle ValKey specific configuration
        if engine == "valkey" and valkey_config:
            builder.with_valkey_config(valkey_config)

        # Apply any additional configurations from kwargs
        for key, value in kwargs.items():
            if hasattr(builder, f"with_{key}"):
                getattr(builder, f"with_{key}")(value)

        request = builder.build()
        return self.elasticache.create_cluster(request)

    def create_cluster_from_builder(self, builder: ClusterBuilder) -> ClusterStatus:
        """Create a new ElastiCache cluster using a builder.

        Args:
            builder: Configured ClusterBuilder instance

        Returns:
            ClusterStatus containing the new cluster information
        """
        request = builder.build()
        return self.elasticache.create_cluster(request)

    def cluster_builder(self, cluster_id: str, engine: Literal["redis", "memcached"]) -> ClusterBuilder:
        """Create a new cluster builder.

        Args:
            cluster_id: Unique identifier for the cluster
            engine: Cache engine type ("redis" or "memcached")

        Returns:
            ClusterBuilder instance
        """
        return ClusterBuilder(cluster_id, engine)

    def modify_cluster(self, request: ModifyClusterRequest) -> ClusterStatus:
        """Modify an existing ElastiCache cluster.

        Args:
            request: Cluster modification parameters

        Returns:
            ClusterStatus containing the updated cluster information

        Examples:
            >>> status = api.modify_cluster(
            ...     ModifyClusterRequest(
            ...         cluster_id="my-redis",
            ...         node_type=NodeType(
            ...             instance_type="cache.t3.small",
            ...             num_nodes=3,
            ...         ),
            ...         apply_immediately=True,
            ...     )
            ... )
        """
        return self.elasticache.modify_cluster(request)

    def delete_cluster(self, cluster_id: str) -> None:
        """Delete an ElastiCache cluster.

        Args:
            cluster_id: ID of the cluster to delete

        Examples:
            >>> api.delete_cluster("my-redis")
        """
        self.elasticache.delete_cluster(cluster_id)

    def get_cluster_status(self, cluster_id: str) -> ClusterStatus:
        """Get the current status of an ElastiCache cluster.

        Args:
            cluster_id: ID of the cluster to check

        Returns:
            ClusterStatus containing the cluster information

        Examples:
            >>> status = api.get_cluster_status("my-redis")
            >>> print(f"Cluster status: {status.status}")
            >>> print(f"Endpoint: {status.endpoint}")
        """
        return self.elasticache.get_cluster_status(cluster_id)

    def create_snapshot(self, cluster_id: str, config: SnapshotConfig) -> Dict[str, Any]:
        """Create a snapshot of an ElastiCache cluster.

        Args:
            cluster_id: ID of the cluster to snapshot
            config: Snapshot configuration

        Returns:
            Dict containing the snapshot information

        Examples:
            >>> snapshot = api.create_snapshot(
            ...     cluster_id="my-redis",
            ...     config=SnapshotConfig(
            ...         snapshot_name="my-backup",
            ...         retention_period=7,
            ...     )
            ... )
        """
        return self.elasticache.create_snapshot(cluster_id, config)

    def restore_cluster(self, request: RestoreClusterRequest) -> ClusterStatus:
        """Restore an ElastiCache cluster from a snapshot.

        Args:
            request: Restore configuration

        Returns:
            ClusterStatus containing the restored cluster information

        Examples:
            >>> status = api.restore_cluster(
            ...     RestoreClusterRequest(
            ...         snapshot_name="my-backup",
            ...         target_cluster_id="my-redis-restored",
            ...         node_type=NodeType(
            ...             instance_type="cache.t3.micro",
            ...             num_nodes=2,
            ...         ),
            ...     )
            ... )
        """
        return self.elasticache.restore_cluster(request)

    def create_parameter_group(
        self,
        group_name: str,
        group_family: str,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Union[str, int, bool]]] = None,
    ) -> ParameterGroupStatus:
        """Create a new parameter group.

        Args:
            group_name: The name of the parameter group
            group_family: The family of the parameter group (e.g., redis6.x)
            description: Description for the parameter group
            parameters: Initial parameter values

        Returns:
            ParameterGroupStatus containing the new parameter group information

        Examples:
            Simple parameter group:
            >>> status = api.create_parameter_group(
            ...     group_name="my-redis-params",
            ...     group_family="redis6.x",
            ...     description="Custom Redis parameters",
            ... )

            Using the builder pattern:
            >>> builder = api.parameter_group_builder("my-redis-params", "redis6.x")
            >>> status = api.create_parameter_group_from_builder(
            ...     builder.with_description("Custom Redis parameters")
            ...            .with_parameter("maxmemory-policy", "volatile-lru")
            ...            .with_parameter("timeout", 0)
            ... )
        """
        builder = ParameterGroupBuilder(group_name, group_family)
        if description:
            builder.with_description(description)
        if parameters:
            builder.with_parameters(parameters)
        request = builder.build()
        return self.elasticache.create_parameter_group(request)

    def parameter_group_builder(self, group_name: str, group_family: str) -> ParameterGroupBuilder:
        """Create a new parameter group builder.

        Args:
            group_name: The name of the parameter group
            group_family: The family of the parameter group

        Returns:
            ParameterGroupBuilder instance
        """
        return ParameterGroupBuilder(group_name, group_family)

    def create_parameter_group_from_builder(self, builder: ParameterGroupBuilder) -> ParameterGroupStatus:
        """Create a new parameter group using a builder.

        Args:
            builder: Configured ParameterGroupBuilder instance

        Returns:
            ParameterGroupStatus containing the new parameter group information
        """
        request = builder.build()
        return self.elasticache.create_parameter_group(request)

    def modify_parameter_group(
        self,
        group_name: str,
        parameters: Dict[str, Union[str, int, bool]],
    ) -> ParameterGroupStatus:
        """Modify parameters in a parameter group.

        Args:
            group_name: The name of the parameter group
            parameters: Parameters to modify

        Returns:
            ParameterGroupStatus containing the updated parameter group information

        Examples:
            >>> status = api.modify_parameter_group(
            ...     group_name="my-redis-params",
            ...     parameters={
            ...         "maxmemory-policy": "allkeys-lru",
            ...         "timeout": 300,
            ...     },
            ... )
        """
        request = ModifyParameterGroupRequest(
            group_name=group_name,
            parameters=parameters,
        )
        return self.elasticache.modify_parameter_group(request)

    def delete_parameter_group(self, group_name: str) -> None:
        """Delete a parameter group.

        Args:
            group_name: Name of the parameter group to delete

        Examples:
            >>> api.delete_parameter_group("my-redis-params")
        """
        self.elasticache.delete_parameter_group(group_name)

    def get_parameter_group_status(self, group_name: str) -> ParameterGroupStatus:
        """Get the current status of a parameter group.

        Args:
            group_name: Name of the parameter group to check

        Returns:
            ParameterGroupStatus containing the parameter group information

        Examples:
            >>> status = api.get_parameter_group_status("my-redis-params")
            >>> print(f"Parameter group family: {status.group_family}")
            >>> for name, param in status.parameters.items():
            ...     print(f"{name}: {param.value} ({param.description})")
        """
        return self.elasticache.get_parameter_group_status(group_name)

    def reset_parameter_group(
        self,
        group_name: str,
        parameter_names: Optional[List[str]] = None,
    ) -> ParameterGroupStatus:
        """Reset parameters in a parameter group to their default values.

        Args:
            group_name: Name of the parameter group
            parameter_names: Optional list of parameter names to reset. If None, all parameters are reset.

        Returns:
            ParameterGroupStatus containing the updated parameter group information

        Examples:
            Reset specific parameters:
            >>> status = api.reset_parameter_group(
            ...     "my-redis-params",
            ...     parameter_names=["maxmemory-policy", "timeout"],
            ... )

            Reset all parameters:
            >>> status = api.reset_parameter_group("my-redis-params")
        """
        return self.elasticache.reset_parameter_group(group_name, parameter_names)

    def create_event_subscription(
        self,
        subscription_name: str,
        sns_topic_arn: str,
        source_type: Optional[Literal["cache-cluster", "cache-parameter-group",
                                      "cache-security-group", "cache-subnet-group"]] = None,
        source_ids: Optional[List[str]] = None,
        event_categories: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> EventSubscriptionStatus:
        """Create an event subscription.

        Args:
            subscription_name: The name of the event subscription
            sns_topic_arn: The ARN of the SNS topic to notify
            source_type: The type of source to monitor
            source_ids: List of source IDs to monitor
            event_categories: Event categories to subscribe to
            tags: Resource tags

        Returns:
            EventSubscriptionStatus containing the subscription information

        Examples:
            Simple subscription:
            >>> status = api.create_event_subscription(
            ...     subscription_name="my-cluster-events",
            ...     sns_topic_arn="arn:aws:sns:region:account:topic",
            ... )

            Using the builder pattern:
            >>> builder = api.event_subscription_builder(
            ...     "my-cluster-events",
            ...     "arn:aws:sns:region:account:topic",
            ... )
            >>> status = api.create_event_subscription_from_builder(
            ...     builder.with_source_type("cache-cluster")
            ...            .with_source_ids(["my-redis"])
            ...            .with_event_categories(["failure", "maintenance"])
            ... )
        """
        builder = EventSubscriptionBuilder(subscription_name, sns_topic_arn)
        if source_type:
            builder.with_source_type(source_type)
        if source_ids:
            builder.with_source_ids(source_ids)
        if event_categories:
            builder.with_event_categories(event_categories)
        if tags:
            builder.with_tags(tags)
        request = builder.build()
        return self.elasticache.create_event_subscription(request)

    def event_subscription_builder(
        self,
        subscription_name: str,
        sns_topic_arn: str,
    ) -> EventSubscriptionBuilder:
        """Create a new event subscription builder.

        Args:
            subscription_name: The name of the event subscription
            sns_topic_arn: The ARN of the SNS topic to notify

        Returns:
            EventSubscriptionBuilder instance
        """
        return EventSubscriptionBuilder(subscription_name, sns_topic_arn)

    def create_event_subscription_from_builder(
        self,
        builder: EventSubscriptionBuilder,
    ) -> EventSubscriptionStatus:
        """Create a new event subscription using a builder.

        Args:
            builder: Configured EventSubscriptionBuilder instance

        Returns:
            EventSubscriptionStatus containing the subscription information
        """
        request = builder.build()
        return self.elasticache.create_event_subscription(request)

    def get_metric_data(
        self,
        metric_name: str,
        cluster_id: str,
        start_time: datetime,
        end_time: datetime,
        period: int = 60,
        statistics: Optional[List[Literal["Average",
                                          "Maximum", "Minimum", "Sum", "SampleCount"]]] = None,
    ) -> MetricResponse:
        """Get performance metric data.

        Args:
            metric_name: The name of the metric to retrieve
            cluster_id: The ID of the cluster
            start_time: The start time of the metric data
            end_time: The end time of the metric data
            period: The granularity in seconds (default: 60)
            statistics: The metric statistics to return (default: ["Average"])

        Returns:
            MetricResponse containing the metric data

        Examples:
            Simple metric request:
            >>> from datetime import datetime, timedelta
            >>> end_time = datetime.utcnow()
            >>> start_time = end_time - timedelta(hours=1)
            >>> response = api.get_metric_data(
            ...     metric_name="CPUUtilization",
            ...     cluster_id="my-redis",
            ...     start_time=start_time,
            ...     end_time=end_time,
            ... )

            Using the builder pattern:
            >>> builder = api.metric_request_builder("CPUUtilization", "my-redis")
            >>> response = api.get_metric_data_from_builder(
            ...     builder.with_time_range(start_time, end_time)
            ...            .with_period(300)
            ...            .with_statistics(["Average", "Maximum"])
            ... )
        """
        builder = MetricRequestBuilder(metric_name, cluster_id)
        builder.with_time_range(start_time, end_time)
        if period != 60:
            builder.with_period(period)
        if statistics:
            builder.with_statistics(statistics)
        request = builder.build()
        return self.elasticache.get_metric_data(request)

    def metric_request_builder(
        self,
        metric_name: str,
        cluster_id: str,
    ) -> MetricRequestBuilder:
        """Create a new metric request builder.

        Args:
            metric_name: The name of the metric to retrieve
            cluster_id: The ID of the cluster

        Returns:
            MetricRequestBuilder instance
        """
        return MetricRequestBuilder(metric_name, cluster_id)

    def get_metric_data_from_builder(
        self,
        builder: MetricRequestBuilder,
    ) -> MetricResponse:
        """Get performance metric data using a builder.

        Args:
            builder: Configured MetricRequestBuilder instance

        Returns:
            MetricResponse containing the metric data
        """
        request = builder.build()
        return self.elasticache.get_metric_data(request)

    def create_replication_group(
        self,
        group_id: str,
        description: str,
        instance_type: str = "cache.t3.micro",
        num_nodes: int = 1,
        engine_version: str = "6.x",
        num_node_groups: int = 1,
        replicas_per_node_group: int = 1,
        automatic_failover: bool = True,
        multi_az: bool = True,
        subnet_group: Optional[str] = None,
        security_groups: Optional[List[str]] = None,
        parameter_group: Optional[str] = None,
        port: int = 6379,
        maintenance_window: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> ReplicationGroupStatus:
        """Create a replication group.

        Args:
            group_id: The ID of the replication group
            description: Description of the replication group
            instance_type: The compute and memory capacity
            num_nodes: Number of cache nodes
            engine_version: Redis engine version
            num_node_groups: Number of node groups (shards)
            replicas_per_node_group: Number of replica nodes per shard
            automatic_failover: Enable automatic failover
            multi_az: Enable Multi-AZ
            subnet_group: Cache subnet group name
            security_groups: List of security group IDs
            parameter_group: Cache parameter group name
            port: Port number
            maintenance_window: Preferred maintenance window
            tags: Resource tags

        Returns:
            ReplicationGroupStatus containing the group information

        Examples:
            Simple replication group:
            >>> status = api.create_replication_group(
            ...     group_id="my-redis-group",
            ...     description="My Redis replication group",
            ...     instance_type="cache.t3.small",
            ... )

            Using the builder pattern:
            >>> builder = api.replication_group_builder(
            ...     "my-redis-group",
            ...     "My Redis replication group",
            ... )
            >>> status = api.create_replication_group_from_builder(
            ...     builder.with_node_type("cache.t3.small", 2)
            ...            .with_sharding(2, 1)
            ...            .with_network("my-subnet", ["sg-123"])
            ...            .with_tags({"Environment": "Production"})
            ... )
        """
        builder = ReplicationGroupBuilder(group_id, description)
        builder.with_node_type(instance_type, num_nodes)
        builder.with_engine_version(engine_version)
        builder.with_sharding(num_node_groups, replicas_per_node_group)
        builder.with_availability(automatic_failover, multi_az)
        if subnet_group or security_groups:
            builder.with_network(subnet_group, security_groups)
        if parameter_group:
            builder.with_parameter_group(parameter_group)
        if port != 6379:
            builder.with_port(port)
        if maintenance_window:
            builder.with_maintenance_window(maintenance_window)
        if tags:
            builder.with_tags(tags)
        request = builder.build()
        return self.elasticache.create_replication_group(request)

    def replication_group_builder(
        self,
        group_id: str,
        description: str,
    ) -> ReplicationGroupBuilder:
        """Create a new replication group builder.

        Args:
            group_id: The ID of the replication group
            description: Description of the replication group

        Returns:
            ReplicationGroupBuilder instance
        """
        return ReplicationGroupBuilder(group_id, description)

    def create_replication_group_from_builder(
        self,
        builder: ReplicationGroupBuilder,
    ) -> ReplicationGroupStatus:
        """Create a replication group using a builder.

        Args:
            builder: Configured ReplicationGroupBuilder instance

        Returns:
            ReplicationGroupStatus containing the group information
        """
        request = builder.build()
        return self.elasticache.create_replication_group(request)

    def create_serverless(
        self,
        cache_name: str,
        description: Optional[str] = None,
        major_engine_version: str = "7.0",
        daily_backup_window: Optional[str] = None,
        backup_retention_period: Optional[int] = None,
        security_group_ids: Optional[List[str]] = None,
        subnet_ids: Optional[List[str]] = None,
        kms_key_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        minimum_capacity: float = 0.5,
        maximum_capacity: float = 4.0,
    ) -> ServerlessStatus:
        """Create a new serverless cache.

        Args:
            cache_name: The name of the serverless cache
            description: Optional description
            major_engine_version: Redis version (default: "7.0")
            daily_backup_window: Optional backup window (format: "04:00-05:00")
            backup_retention_period: Optional backup retention period (0-35 days)
            security_group_ids: Optional list of security group IDs
            subnet_ids: Optional list of subnet IDs
            kms_key_id: Optional KMS key ID for encryption
            tags: Optional resource tags
            minimum_capacity: Minimum ECU units (0.5-100.0, default: 0.5)
            maximum_capacity: Maximum ECU units (0.5-100.0, default: 4.0)

        Returns:
            ServerlessStatus containing the new cache information

        Examples:
            Simple serverless cache:
            >>> status = api.create_serverless(
            ...     cache_name="my-serverless-cache",
            ...     description="My serverless Redis cache",
            ... )

            Advanced configuration:
            >>> status = api.create_serverless(
            ...     cache_name="my-serverless-cache",
            ...     description="Production serverless Redis cache",
            ...     major_engine_version="7.0",
            ...     daily_backup_window="04:00-05:00",
            ...     backup_retention_period=7,
            ...     security_group_ids=["sg-123456"],
            ...     subnet_ids=["subnet-123456"],
            ...     minimum_capacity=1.0,
            ...     maximum_capacity=8.0,
            ...     tags={"Environment": "Production"},
            ... )
        """
        request = CreateServerlessRequest(
            cache_name=cache_name,
            description=description,
            major_engine_version=major_engine_version,
            daily_backup_window=daily_backup_window,
            backup_retention_period=backup_retention_period,
            security_group_ids=security_group_ids,
            subnet_ids=subnet_ids,
            kms_key_id=kms_key_id,
            tags=tags,
            scaling=ServerlessScalingConfiguration(
                minimum_capacity=minimum_capacity,
                maximum_capacity=maximum_capacity,
            ),
        )
        return self.elasticache.create_serverless(request)

    def modify_serverless(
        self,
        cache_name: str,
        description: Optional[str] = None,
        daily_backup_window: Optional[str] = None,
        backup_retention_period: Optional[int] = None,
        security_group_ids: Optional[List[str]] = None,
        minimum_capacity: Optional[float] = None,
        maximum_capacity: Optional[float] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> ServerlessStatus:
        """Modify an existing serverless cache.

        Args:
            cache_name: The name of the serverless cache
            description: Optional new description
            daily_backup_window: Optional new backup window (format: "04:00-05:00")
            backup_retention_period: Optional new backup retention period (0-35 days)
            security_group_ids: Optional new list of security group IDs
            minimum_capacity: Optional new minimum ECU units (0.5-100.0)
            maximum_capacity: Optional new maximum ECU units (0.5-100.0)
            tags: Optional new resource tags

        Returns:
            ServerlessStatus containing the updated cache information

        Examples:
            >>> status = api.modify_serverless(
            ...     cache_name="my-serverless-cache",
            ...     description="Updated serverless Redis cache",
            ...     minimum_capacity=2.0,
            ...     maximum_capacity=16.0,
            ... )
        """
        scaling = None
        if minimum_capacity is not None and maximum_capacity is not None:
            scaling = ServerlessScalingConfiguration(
                minimum_capacity=minimum_capacity,
                maximum_capacity=maximum_capacity,
            )

        request = ModifyServerlessRequest(
            cache_name=cache_name,
            description=description,
            daily_backup_window=daily_backup_window,
            backup_retention_period=backup_retention_period,
            security_group_ids=security_group_ids,
            scaling=scaling,
            tags=tags,
        )
        return self.elasticache.modify_serverless(request)

    def delete_serverless(self, cache_name: str) -> None:
        """Delete a serverless cache.

        Args:
            cache_name: The name of the serverless cache to delete

        Examples:
            >>> api.delete_serverless("my-serverless-cache")
        """
        self.elasticache.delete_serverless(cache_name)

    def get_serverless_status(self, cache_name: str) -> ServerlessStatus:
        """Get the current status of a serverless cache.

        Args:
            cache_name: The name of the serverless cache to check

        Returns:
            ServerlessStatus containing the cache information

        Examples:
            >>> status = api.get_serverless_status("my-serverless-cache")
            >>> print(f"Cache status: {status.status}")
            >>> print(f"Endpoint: {status.endpoint}")
            >>> if status.scaling:
            ...     print(f"Capacity: {status.scaling.minimum_capacity} - {status.scaling.maximum_capacity} ECU")
        """
        return self.elasticache.get_serverless_status(cache_name)

    def init_serverless_cache(
        self,
        cache_name: str,
        description: Optional[str] = None,
        major_engine_version: str = "7.0",
        daily_backup_window: Optional[str] = None,
        backup_retention_period: Optional[int] = None,
        security_group_ids: Optional[List[str]] = None,
        subnet_ids: Optional[List[str]] = None,
        kms_key_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        minimum_capacity: float = 0.5,
        maximum_capacity: float = 4.0,
    ) -> ServerlessStatus:
        """Initialize a serverless cache. Creates the cache if it doesn't exist, skips if it does.

        Args:
            cache_name: The name of the serverless cache
            description: Optional description
            major_engine_version: Redis version (default: "7.0")
            daily_backup_window: Optional backup window (format: "04:00-05:00")
            backup_retention_period: Optional backup retention period (0-35 days)
            security_group_ids: Optional list of security group IDs
            subnet_ids: Optional list of subnet IDs
            kms_key_id: Optional KMS key ID for encryption
            tags: Optional resource tags
            minimum_capacity: Minimum ECU units (0.5-100.0, default: 0.5)
            maximum_capacity: Maximum ECU units (0.5-100.0, default: 4.0)

        Returns:
            ServerlessStatus containing the cache information

        Examples:
            >>> status = api.init_serverless_cache(
            ...     cache_name="my-serverless-cache",
            ...     description="My serverless Redis cache",
            ...     major_engine_version="7.0",
            ...     daily_backup_window="04:00-05:00",
            ...     backup_retention_period=7,
            ...     minimum_capacity=1.0,
            ...     maximum_capacity=8.0,
            ...     tags={"Environment": "Production"},
            ... )
            >>> print(f"Cache status: {status.status}")
            >>> print(f"Endpoint: {status.endpoint}")
        """
        try:
            # Try to get the existing cache status
            status = self.get_serverless_status(cache_name)
            return status
        except ClientError as e:
            if e.response["Error"]["Code"] == "CacheClusterNotFound":
                # Cache doesn't exist, create it
                return self.create_serverless(
                    cache_name=cache_name,
                    description=description,
                    major_engine_version=major_engine_version,
                    daily_backup_window=daily_backup_window,
                    backup_retention_period=backup_retention_period,
                    security_group_ids=security_group_ids,
                    subnet_ids=subnet_ids,
                    kms_key_id=kms_key_id,
                    tags=tags,
                    minimum_capacity=minimum_capacity,
                    maximum_capacity=maximum_capacity,
                )
            else:
                # Some other error occurred
                raise

    def get_redis_client(self, endpoint: str, port: int = 6379) -> RedisClient:
        """Get a Redis client for the specified endpoint.

        Args:
            endpoint: The endpoint of the Redis cluster/node
            port: The port number (default: 6379)

        Returns:
            RedisClient instance configured for the endpoint

        Examples:
            >>> redis = api.get_redis_client("my-redis.xxxxx.clustercfg.use1.cache.amazonaws.com")
            >>> response = redis.set("key", "value", ttl=3600)
            >>> if response.success:
            ...     print(f"Value set successfully")
            ... else:
            ...     print(f"Error: {response.error}")
        """
        self._check_elasticache_deps()
        config = CacheConfig(
            host=endpoint,
            port=port,
            username=self.config.credentials.aws_access_key_id if self.config.credentials else None,
            password=self.config.credentials.aws_secret_access_key if self.config.credentials else None,
        )
        return RedisClient(config)

    def get_memcached_client(self, endpoint: str, port: int = 11211) -> MemcachedClient:
        """Get a Memcached client for the specified endpoint.

        Args:
            endpoint: The endpoint of the Memcached cluster/node
            port: The port number (default: 11211)

        Returns:
            MemcachedClient instance configured for the endpoint

        Examples:
            >>> memcached = api.get_memcached_client("my-memcached.xxxxx.cfg.use1.cache.amazonaws.com")
            >>> response = memcached.set("key", "value", ttl=3600)
            >>> if response.success:
            ...     print(f"Value set successfully")
            ... else:
            ...     print(f"Error: {response.error}")
        """
        self._check_elasticache_deps()
        config = CacheConfig(
            host=endpoint,
            port=port,
        )
        return MemcachedClient(config)

    def get_cache_client(self, cluster_id: str) -> Union[RedisClient, MemcachedClient]:
        """Get appropriate cache client based on cluster ID.

        Args:
            cluster_id: The ID of the cluster

        Returns:
            Either RedisClient or MemcachedClient based on the cluster engine

        Examples:
            >>> client = api.get_cache_client("my-redis")
            >>> if isinstance(client, RedisClient):
            ...     response = client.set("key", "value")
            ... else:
            ...     response = client.add("key", "value")
        """
        self._check_elasticache_deps()
        status = self.get_cluster_status(cluster_id)
        if status.engine == "redis":
            return self.get_redis_client(status.endpoint)
        elif status.engine == "memcached":
            return self.get_memcached_client(status.endpoint)
        else:
            raise ValueError(f"Unsupported engine type: {status.engine}")

    def get_serverless_client(
        self,
        cache_name: str,
        cache_type: Literal["redis", "memcached", "valkey"] = "redis"
    ) -> Union[RedisClient, MemcachedClient, ValKeyClient]:
        """Get appropriate client for a serverless cache.

        Args:
            cache_name: The name of the serverless cache
            cache_type: The type of cache engine ("redis", "memcached", or "valkey")

        Returns:
            Appropriate client instance for the specified cache type

        Raises:
            ValueError: If an unsupported cache type is specified

        Examples:
            Redis client:
            >>> redis = api.get_serverless_client("my-cache", "redis")
            >>> response = redis.set("key", "value", ttl=3600)

            Memcached client:
            >>> memcached = api.get_serverless_client("my-cache", "memcached")
            >>> response = memcached.set("key", "value", ttl=3600)

            ValKey client:
            >>> valkey = api.get_serverless_client("my-cache", "valkey")
            >>> response = valkey.set("key", "value", ttl=3600)
            >>> response = valkey.enhanced_io("key", "value")  # ValKey 특화 기능
        """
        self._check_elasticache_deps()
        status = self.get_serverless_status(cache_name)
        config = CacheConfig(
            host=status.endpoint,
            port=6379 if cache_type in ["redis", "valkey"] else 11211,
            username=self.config.credentials.aws_access_key_id if self.config.credentials else None,
            password=self.config.credentials.aws_secret_access_key if self.config.credentials else None,
        )

        if cache_type == "redis":
            return RedisClient(config)
        elif cache_type == "memcached":
            return MemcachedClient(config)
        elif cache_type == "valkey":
            return ValKeyClient(config)
        else:
            raise ValueError(f"Unsupported cache type: {cache_type}")
