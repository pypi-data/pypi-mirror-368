"""ElastiCache API for managing Redis and Memcached clusters.

This module provides a high-level interface for managing ElastiCache clusters,
including provisioned instances (Redis, Memcached) and serverless caches.

Features:
- Cluster management (create, modify, delete, backup/restore)
- Parameter group management
- Event subscription and monitoring
- Performance metrics collection
- Replication group management
- Auto failover configuration
- Maintenance window scheduling
- Serverless cache management

Examples:
    Initialize a serverless cache (creates if not exists):
    >>> from chainsaws.aws.elasticache import ElastiCacheAPI
    >>> api = ElastiCacheAPI()
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

    Create a new serverless cache:
    >>> status = api.create_serverless(
    ...     cache_name="my-serverless-cache",
    ...     description="My serverless Redis cache",
    ...     major_engine_version="7.0",
    ...     daily_backup_window="04:00-05:00",
    ...     backup_retention_period=7,
    ...     minimum_capacity=1.0,
    ...     maximum_capacity=8.0,
    ...     tags={"Environment": "Production"},
    ... )
"""

from chainsaws.aws.elasticache.elasticache import ElastiCacheAPI
from chainsaws.aws.elasticache.elasticache_models import (
    ClusterStatus,
    CreateServerlessRequest,
    ModifyServerlessRequest,
    ServerlessStatus,
    ServerlessScalingConfiguration,
    ElastiCacheAPIConfig,
    EventSubscriptionStatus,
    MetricResponse,
    ParameterGroupStatus,
    ReplicationGroupStatus,
)
from chainsaws.aws.elasticache.builder import (
    ClusterBuilder,
    EventSubscriptionBuilder,
    MetricRequestBuilder,
    ParameterGroupBuilder,
    ReplicationGroupBuilder,
)

__all__ = [
    "ElastiCacheAPI",
    "ElastiCacheAPIConfig",
    "ClusterStatus",
    "EventSubscriptionStatus",
    "MetricResponse",
    "ParameterGroupStatus",
    "ReplicationGroupStatus",
    "ClusterBuilder",
    "EventSubscriptionBuilder",
    "MetricRequestBuilder",
    "ParameterGroupBuilder",
    "ReplicationGroupBuilder",
    "CreateServerlessRequest",
    "ModifyServerlessRequest",
    "ServerlessStatus",
    "ServerlessScalingConfiguration",
]
