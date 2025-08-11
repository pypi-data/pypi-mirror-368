"""Internal implementation of ElastiCache API."""

from typing import Any, Dict, List, Optional
import boto3
from botocore.exceptions import ClientError
import logging

from chainsaws.aws.elasticache.elasticache_models import (
    ClusterStatus,
    CreateClusterRequest,
    CreateParameterGroupRequest,
    ElastiCacheAPIConfig,
    EventSubscriptionRequest,
    EventSubscriptionStatus,
    MetricDatapoint,
    MetricRequest,
    MetricResponse,
    ModifyClusterRequest,
    ModifyParameterGroupRequest,
    ModifyMaintenanceWindowRequest,
    ParameterType,
    ParameterGroupStatus,
    ReplicationGroupRequest,
    ReplicationGroupStatus,
    RestoreClusterRequest,
    SnapshotConfig,
    CreateServerlessRequest,
    ModifyServerlessRequest,
    ServerlessStatus,
    ServerlessScalingConfiguration
)

logger = logging.getLogger(__name__)


class ElastiCache:
    """Internal ElastiCache implementation."""

    def __init__(
        self,
        boto3_session: boto3.Session,
        config: Optional[ElastiCacheAPIConfig] = None,
    ) -> None:
        """Initialize ElastiCache client."""
        self.config = config or ElastiCacheAPIConfig()
        self.client = boto3_session.client(
            "elasticache",
            config=boto3.Config(
                retries={"max_attempts": self.config.max_retries}),
        )
        self.cloudwatch = boto3_session.client("cloudwatch")

    def create_cluster(self, request: CreateClusterRequest) -> ClusterStatus:
        """Create an ElastiCache cluster."""
        try:
            params: Dict[str, Any] = {
                "CacheClusterId": request.cluster_id,
                "Engine": request.engine,
                "CacheNodeType": request.node_type.instance_type,
                "NumCacheNodes": request.node_type.num_nodes,
                "Tags": [{"Key": k, "Value": v} for k, v in request.tags.items()],
            }

            # Handle serverless configuration
            if request.node_type.instance_type == "serverless":
                if not request.node_type.serverless_config:
                    raise ValueError(
                        "Serverless configuration is required for serverless clusters")
                params.update({
                    "ServerlessConfiguration": {
                        "MinimumCapacity": request.node_type.serverless_config.minimum_capacity,
                        "MaximumCapacity": request.node_type.serverless_config.maximum_capacity,
                    }
                })

            # Handle engine specific configurations
            if request.engine == "redis":
                if not request.redis_config:
                    raise ValueError(
                        "Redis configuration is required for Redis clusters")
                params.update({
                    "EngineVersion": request.redis_config.version,
                    "Port": request.redis_config.port,
                    "AuthToken": request.redis_config.auth_token,
                    "TransitEncryptionEnabled": request.redis_config.transit_encryption,
                    "AtRestEncryptionEnabled": request.redis_config.at_rest_encryption,
                    "AutomaticFailoverEnabled": request.redis_config.auto_failover,
                    "MultiAZEnabled": request.redis_config.multi_az,
                    "SnapshotRetentionLimit": request.redis_config.backup_retention,
                    "PreferredMaintenanceWindow": request.redis_config.maintenance_window,
                    "CacheParameterGroupName": request.redis_config.parameter_group,
                })
            elif request.engine == "memcached":
                if not request.memcached_config:
                    raise ValueError(
                        "Memcached configuration is required for Memcached clusters")
                params.update({
                    "EngineVersion": request.memcached_config.version,
                    "Port": request.memcached_config.port,
                    "CacheParameterGroupName": request.memcached_config.parameter_group,
                })
            elif request.engine == "valkey":
                if not request.valkey_config:
                    raise ValueError(
                        "ValKey configuration is required for ValKey clusters")
                params.update({
                    "EngineVersion": request.valkey_config.version,
                    "Port": request.valkey_config.port,
                    "AuthToken": request.valkey_config.auth_token,
                    "TransitEncryptionEnabled": request.valkey_config.transit_encryption,
                    "AtRestEncryptionEnabled": request.valkey_config.at_rest_encryption,
                    "AutomaticFailoverEnabled": request.valkey_config.auto_failover,
                    "MultiAZEnabled": request.valkey_config.multi_az,
                    "SnapshotRetentionLimit": request.valkey_config.backup_retention,
                    "PreferredMaintenanceWindow": request.valkey_config.maintenance_window,
                    "CacheParameterGroupName": request.valkey_config.parameter_group,
                    "EnhancedIOEnabled": request.valkey_config.enhanced_io,
                    "TLSOffloadingEnabled": request.valkey_config.tls_offloading,
                    "EnhancedIOMultiplexingEnabled": request.valkey_config.enhanced_io_multiplexing,
                })

            # Handle network configuration
            if request.subnet_group:
                params["CacheSubnetGroupName"] = request.subnet_group.name
            if request.security_groups:
                params["SecurityGroupIds"] = [
                    sg.id for sg in request.security_groups]

            response = self.client.create_cache_cluster(**params)
            return self._convert_to_cluster_status(response["CacheCluster"])

        except ClientError as e:
            logger.error(f"Failed to create cluster: {e}")
            raise

    def _convert_to_cluster_status(self, cluster: Dict[str, Any]) -> ClusterStatus:
        """Convert AWS response to ClusterStatus."""
        endpoint = cluster.get("ConfigurationEndpoint") or cluster.get(
            "CacheNodes", [{}])[0].get("Endpoint", {})
        return ClusterStatus(
            cluster_id=cluster["CacheClusterId"],
            status=cluster["CacheClusterStatus"],
            endpoint=f"{endpoint.get('Address', '')}:{
                endpoint.get('Port', '')}",
            port=endpoint.get("Port", 0),
            node_type=cluster["CacheNodeType"],
            num_nodes=cluster["NumCacheNodes"],
            engine=cluster["Engine"],
            engine_version=cluster["EngineVersion"],
            subnet_group=cluster.get("CacheSubnetGroupName"),
            security_groups=[sg["SecurityGroupId"]
                             for sg in cluster.get("SecurityGroups", [])],
            tags={tag["Key"]: tag["Value"] for tag in cluster.get("Tags", [])},
        )

    def modify_cluster(self, request: ModifyClusterRequest) -> ClusterStatus:
        """Modify an existing ElastiCache cluster.

        Args:
            request: Cluster modification parameters

        Returns:
            ClusterStatus containing the updated cluster information

        Raises:
            ClientError: If cluster modification fails
        """
        try:
            params = {
                "CacheClusterId": request.cluster_id,
                "ApplyImmediately": request.apply_immediately,
            }

            if request.node_type:
                params["CacheNodeType"] = request.node_type.instance_type
                params["NumCacheNodes"] = request.node_type.num_nodes

            if request.security_groups:
                params["SecurityGroupIds"] = [
                    sg.id for sg in request.security_groups]

            if request.maintenance_window:
                params["PreferredMaintenanceWindow"] = request.maintenance_window

            if request.engine_version:
                params["EngineVersion"] = request.engine_version

            if request.auth_token:
                params["AuthToken"] = request.auth_token

            response = self.client.modify_cache_cluster(**params)
            cluster = response["CacheCluster"]

            if request.tags:
                self.client.add_tags_to_resource(
                    ResourceName=cluster["ARN"],
                    Tags=[{"Key": k, "Value": v}
                          for k, v in request.tags.items()],
                )

            return ClusterStatus(
                cluster_id=cluster["CacheClusterId"],
                status=cluster["CacheClusterStatus"],
                endpoint=cluster.get(
                    "ConfigurationEndpoint", {}).get("Address"),
                port=cluster.get("ConfigurationEndpoint", {}).get("Port", 0),
                node_type=cluster["CacheNodeType"],
                num_nodes=cluster["NumCacheNodes"],
                engine=cluster["Engine"],
                engine_version=cluster["EngineVersion"],
                subnet_group=cluster.get("CacheSubnetGroupName"),
                security_groups=[sg["SecurityGroupId"]
                                 for sg in cluster.get("SecurityGroups", [])],
                tags=request.tags if request.tags else {},
            )

        except ClientError as e:
            logger.error(f"Failed to modify cluster {request.cluster_id}: {e}")
            raise

    def delete_cluster(self, cluster_id: str) -> None:
        """Delete an ElastiCache cluster.

        Args:
            cluster_id: ID of the cluster to delete

        Raises:
            ClientError: If cluster deletion fails
        """
        try:
            self.client.delete_cache_cluster(CacheClusterId=cluster_id)
        except ClientError as e:
            logger.error(f"Failed to delete cluster {cluster_id}: {e}")
            raise

    def get_cluster_status(self, cluster_id: str) -> ClusterStatus:
        """Get the current status of an ElastiCache cluster.

        Args:
            cluster_id: ID of the cluster to check

        Returns:
            ClusterStatus containing the cluster information

        Raises:
            ClientError: If status retrieval fails
        """
        try:
            response = self.client.describe_cache_clusters(
                CacheClusterId=cluster_id,
                ShowCacheNodeInfo=True,
            )
            cluster = response["CacheClusters"][0]

            # Get tags
            tags_response = self.client.list_tags_for_resource(
                ResourceName=cluster["ARN"])
            tags = {tag["Key"]: tag["Value"]
                    for tag in tags_response.get("TagList", [])}

            return ClusterStatus(
                cluster_id=cluster["CacheClusterId"],
                status=cluster["CacheClusterStatus"],
                endpoint=cluster.get(
                    "ConfigurationEndpoint", {}).get("Address"),
                port=cluster.get("ConfigurationEndpoint", {}).get("Port", 0),
                node_type=cluster["CacheNodeType"],
                num_nodes=cluster["NumCacheNodes"],
                engine=cluster["Engine"],
                engine_version=cluster["EngineVersion"],
                subnet_group=cluster.get("CacheSubnetGroupName"),
                security_groups=[sg["SecurityGroupId"]
                                 for sg in cluster.get("SecurityGroups", [])],
                tags=tags,
            )

        except ClientError as e:
            logger.error(f"Failed to get status for cluster {cluster_id}: {e}")
            raise

    def create_snapshot(self, cluster_id: str, config: SnapshotConfig) -> Dict[str, Any]:
        """Create a snapshot of an ElastiCache cluster.

        Args:
            cluster_id: ID of the cluster to snapshot
            config: Snapshot configuration

        Returns:
            Dict containing the snapshot information

        Raises:
            ClientError: If snapshot creation fails
        """
        try:
            params = {
                "CacheClusterId": cluster_id,
                "SnapshotName": config.snapshot_name,
            }

            if config.target_bucket:
                params["TargetBucket"] = config.target_bucket

            response = self.client.create_snapshot(**params)
            return response["Snapshot"]

        except ClientError as e:
            logger.error(
                f"Failed to create snapshot {config.snapshot_name} for cluster {cluster_id}: {e}")
            raise

    def restore_cluster(self, request: RestoreClusterRequest) -> ClusterStatus:
        """Restore an ElastiCache cluster from a snapshot.

        Args:
            request: Restore configuration

        Returns:
            ClusterStatus containing the restored cluster information

        Raises:
            ClientError: If cluster restoration fails
        """
        try:
            params = {
                "SnapshotName": request.snapshot_name,
                "CacheClusterId": request.target_cluster_id,
            }

            if request.node_type:
                params["CacheNodeType"] = request.node_type.instance_type
                params["NumCacheNodes"] = request.node_type.num_nodes

            if request.subnet_group:
                params["CacheSubnetGroupName"] = request.subnet_group.name

            if request.port:
                params["Port"] = request.port

            if request.security_groups:
                params["SecurityGroupIds"] = [
                    sg.id for sg in request.security_groups]

            response = self.client.restore_cache_cluster_from_snapshot(
                **params)
            cluster = response["CacheCluster"]

            if request.tags:
                self.client.add_tags_to_resource(
                    ResourceName=cluster["ARN"],
                    Tags=[{"Key": k, "Value": v}
                          for k, v in request.tags.items()],
                )

            return ClusterStatus(
                cluster_id=cluster["CacheClusterId"],
                status=cluster["CacheClusterStatus"],
                endpoint=cluster.get(
                    "ConfigurationEndpoint", {}).get("Address"),
                port=cluster.get("ConfigurationEndpoint", {}).get("Port", 0),
                node_type=cluster["CacheNodeType"],
                num_nodes=cluster["NumCacheNodes"],
                engine=cluster["Engine"],
                engine_version=cluster["EngineVersion"],
                subnet_group=cluster.get("CacheSubnetGroupName"),
                security_groups=[sg["SecurityGroupId"]
                                 for sg in cluster.get("SecurityGroups", [])],
                tags=request.tags,
            )

        except ClientError as e:
            logger.error(
                f"Failed to restore cluster from snapshot {request.snapshot_name}: {e}")
            raise

    def create_parameter_group(self, request: CreateParameterGroupRequest) -> ParameterGroupStatus:
        """Create a new parameter group.

        Args:
            request: Parameter group creation parameters

        Returns:
            ParameterGroupStatus containing the new parameter group information

        Raises:
            ClientError: If parameter group creation fails
        """
        try:
            # Create parameter group
            self.client.create_cache_parameter_group(
                CacheParameterGroupFamily=request.group_family,
                CacheParameterGroupName=request.group_name,
                Description=request.description,
            )

            # If initial parameters are provided, modify them
            if request.parameters:
                parameter_list = [
                    {"ParameterName": name, "ParameterValue": str(value)}
                    for name, value in request.parameters.items()
                ]
                self.client.modify_cache_parameter_group(
                    CacheParameterGroupName=request.group_name,
                    ParameterNameValues=parameter_list,
                )

            # Get the complete parameter group status
            return self.get_parameter_group_status(request.group_name)

        except ClientError as e:
            logger.error(
                f"Failed to create parameter group {request.group_name}: {e}")
            raise

    def modify_parameter_group(self, request: ModifyParameterGroupRequest) -> ParameterGroupStatus:
        """Modify parameters in a parameter group.

        Args:
            request: Parameter modification request

        Returns:
            ParameterGroupStatus containing the updated parameter group information

        Raises:
            ClientError: If parameter modification fails
        """
        try:
            parameter_list = [
                {"ParameterName": name, "ParameterValue": str(value)}
                for name, value in request.parameters.items()
            ]
            self.client.modify_cache_parameter_group(
                CacheParameterGroupName=request.group_name,
                ParameterNameValues=parameter_list,
            )

            return self.get_parameter_group_status(request.group_name)

        except ClientError as e:
            logger.error(
                f"Failed to modify parameter group {request.group_name}: {e}")
            raise

    def delete_parameter_group(self, group_name: str) -> None:
        """Delete a parameter group.

        Args:
            group_name: Name of the parameter group to delete

        Raises:
            ClientError: If parameter group deletion fails
        """
        try:
            self.client.delete_cache_parameter_group(
                CacheParameterGroupName=group_name)
        except ClientError as e:
            logger.error(f"Failed to delete parameter group {group_name}: {e}")
            raise

    def get_parameter_group_status(self, group_name: str) -> ParameterGroupStatus:
        """Get the current status of a parameter group.

        Args:
            group_name: Name of the parameter group to check

        Returns:
            ParameterGroupStatus containing the parameter group information

        Raises:
            ClientError: If status retrieval fails
        """
        try:
            # Get parameter group metadata
            response = self.client.describe_cache_parameter_groups(
                CacheParameterGroupName=group_name)
            group = response["CacheParameterGroups"][0]

            # Get parameter values
            params_response = self.client.describe_cache_parameters(
                CacheParameterGroupName=group_name)
            parameters = {}

            for param in params_response["Parameters"]:
                param_type = ParameterType(
                    name=param["ParameterName"],
                    value=param.get("ParameterValue", ""),
                    data_type=param["DataType"].lower(),
                    modifiable=param.get("IsModifiable", True),
                    description=param.get("Description"),
                    minimum_engine_version=param.get("MinimumEngineVersion"),
                    allowed_values=param.get("AllowedValues"),
                )
                parameters[param["ParameterName"]] = param_type

            return ParameterGroupStatus(
                group_name=group["CacheParameterGroupName"],
                group_family=group["CacheParameterGroupFamily"],
                description=group["Description"],
                parameters=parameters,
            )

        except ClientError as e:
            logger.error(
                f"Failed to get parameter group status for {group_name}: {e}")
            raise

    def reset_parameter_group(self, group_name: str, parameter_names: Optional[List[str]] = None) -> ParameterGroupStatus:
        """Reset parameters in a parameter group to their default values.

        Args:
            group_name: Name of the parameter group
            parameter_names: Optional list of parameter names to reset. If None, all parameters are reset.

        Returns:
            ParameterGroupStatus containing the updated parameter group information

        Raises:
            ClientError: If parameter reset fails
        """
        try:
            if parameter_names:
                self.client.reset_cache_parameter_group(
                    CacheParameterGroupName=group_name,
                    ParameterNameValues=[
                        {"ParameterName": name, "ParameterValue": ""}
                        for name in parameter_names
                    ],
                )
            else:
                self.client.reset_cache_parameter_group(
                    CacheParameterGroupName=group_name,
                    ResetAllParameters=True,
                )

            return self.get_parameter_group_status(group_name)

        except ClientError as e:
            logger.error(
                f"Failed to reset parameters for group {group_name}: {e}")
            raise

    def create_event_subscription(self, request: EventSubscriptionRequest) -> EventSubscriptionStatus:
        """Create an event subscription.

        Args:
            request: Event subscription configuration

        Returns:
            EventSubscriptionStatus containing the subscription information

        Raises:
            ClientError: If subscription creation fails
        """
        try:
            params = {
                "SubscriptionName": request.subscription_name,
                "SnsTopicArn": request.sns_topic_arn,
                "SourceType": request.source_type,
                "Enabled": request.enabled,
            }

            if request.source_ids:
                params["SourceIds"] = request.source_ids
            if request.event_categories:
                params["EventCategories"] = request.event_categories

            response = self.client.create_cache_security_group(**params)
            subscription = response["EventSubscription"]

            if request.tags:
                self.client.add_tags_to_resource(
                    ResourceName=subscription["EventSubscriptionArn"],
                    Tags=[{"Key": k, "Value": v}
                          for k, v in request.tags.items()],
                )

            return EventSubscriptionStatus(
                subscription_name=subscription["CacheSubscriptionName"],
                sns_topic_arn=subscription["TopicArn"],
                source_type=subscription["SourceType"],
                source_ids=subscription.get("SourceIds", []),
                event_categories=subscription.get("EventCategories", []),
                enabled=subscription["Enabled"],
                status=subscription["Status"],
            )

        except ClientError as e:
            logger.error(f"Failed to create event subscription {
                         request.subscription_name}: {e}")
            raise

    def delete_event_subscription(self, subscription_name: str) -> None:
        """Delete an event subscription.

        Args:
            subscription_name: Name of the subscription to delete

        Raises:
            ClientError: If subscription deletion fails
        """
        try:
            self.client.delete_event_subscription(
                SubscriptionName=subscription_name)
        except ClientError as e:
            logger.error(f"Failed to delete event subscription {
                         subscription_name}: {e}")
            raise

    def get_metric_data(self, request: MetricRequest) -> MetricResponse:
        """Get performance metric data.

        Args:
            request: Metric request configuration

        Returns:
            MetricResponse containing the metric data

        Raises:
            ClientError: If metric retrieval fails
        """
        try:
            cloudwatch = boto3.client("cloudwatch")
            response = cloudwatch.get_metric_data(
                MetricDataQueries=[
                    {
                        "Id": "m1",
                        "MetricStat": {
                            "Metric": {
                                "Namespace": "AWS/ElastiCache",
                                "MetricName": request.metric_name,
                                "Dimensions": [
                                    {
                                        "Name": "CacheClusterId",
                                        "Value": request.cluster_id,
                                    }
                                ],
                            },
                            "Period": request.period,
                            "Stat": request.statistics[0],
                        },
                    }
                ],
                StartTime=request.start_time,
                EndTime=request.end_time,
            )

            datapoints = []
            for timestamp, value in zip(response["Timestamps"], response["Values"]):
                datapoints.append(
                    MetricDatapoint(
                        timestamp=timestamp,
                        value=value,
                        unit=response["MetricDataResults"][0]["Unit"],
                    )
                )

            return MetricResponse(
                metric_name=request.metric_name,
                datapoints=datapoints,
            )

        except ClientError as e:
            logger.error(f"Failed to get metric data for {
                         request.cluster_id}: {e}")
            raise

    def create_replication_group(self, request: ReplicationGroupRequest) -> ReplicationGroupStatus:
        """Create a replication group.

        Args:
            request: Replication group configuration

        Returns:
            ReplicationGroupStatus containing the group information

        Raises:
            ClientError: If group creation fails
        """
        try:
            params = {
                "ReplicationGroupId": request.group_id,
                "ReplicationGroupDescription": request.description,
                "CacheNodeType": request.node_type.instance_type,
                "Engine": "redis",
                "EngineVersion": request.engine_version,
                "NumNodeGroups": request.num_node_groups,
                "ReplicasPerNodeGroup": request.replicas_per_node_group,
                "AutomaticFailoverEnabled": request.automatic_failover,
                "MultiAZEnabled": request.multi_az,
                "Port": request.port,
            }

            if request.subnet_group:
                params["CacheSubnetGroupName"] = request.subnet_group.name
            if request.security_groups:
                params["SecurityGroupIds"] = [
                    sg.id for sg in request.security_groups]
            if request.parameter_group:
                params["CacheParameterGroupName"] = request.parameter_group
            if request.maintenance_window:
                params["PreferredMaintenanceWindow"] = request.maintenance_window

            response = self.client.create_replication_group(**params)
            group = response["ReplicationGroup"]

            if request.tags:
                self.client.add_tags_to_resource(
                    ResourceName=group["ARN"],
                    Tags=[{"Key": k, "Value": v}
                          for k, v in request.tags.items()],
                )

            return self._get_replication_group_status(group)

        except ClientError as e:
            logger.error(f"Failed to create replication group {
                         request.group_id}: {e}")
            raise

    def _get_replication_group_status(self, group: Dict[str, Any]) -> ReplicationGroupStatus:
        """Convert API response to ReplicationGroupStatus."""
        return ReplicationGroupStatus(
            group_id=group["ReplicationGroupId"],
            status=group["Status"],
            description=group["Description"],
            node_groups=group.get("NodeGroups", []),
            automatic_failover=group.get("AutomaticFailover", "disabled"),
            multi_az=group.get("MultiAZ", False),
            endpoint=group.get("ConfigurationEndpoint", {}).get("Address"),
            port=group.get("ConfigurationEndpoint", {}).get("Port"),
        )

    def delete_replication_group(self, group_id: str) -> None:
        """Delete a replication group.

        Args:
            group_id: ID of the replication group to delete

        Raises:
            ClientError: If group deletion fails
        """
        try:
            self.client.delete_replication_group(ReplicationGroupId=group_id)
        except ClientError as e:
            logger.error(f"Failed to delete replication group {group_id}: {e}")
            raise

    def modify_maintenance_window(self, request: ModifyMaintenanceWindowRequest) -> ClusterStatus:
        """Modify the maintenance window for a cluster.

        Args:
            request: Maintenance window modification request

        Returns:
            ClusterStatus containing the updated cluster information

        Raises:
            ClientError: If modification fails
        """
        try:
            window = request.window
            window_str = f"{window.day_of_week}:{
                window.start_time}-{window.duration:02d}:00"

            response = self.client.modify_cache_cluster(
                CacheClusterId=request.cluster_id,
                PreferredMaintenanceWindow=window_str,
                ApplyImmediately=True,
            )
            cluster = response["CacheCluster"]

            return ClusterStatus(
                cluster_id=cluster["CacheClusterId"],
                status=cluster["CacheClusterStatus"],
                endpoint=cluster.get(
                    "ConfigurationEndpoint", {}).get("Address"),
                port=cluster.get("ConfigurationEndpoint", {}).get("Port", 0),
                node_type=cluster["CacheNodeType"],
                num_nodes=cluster["NumCacheNodes"],
                engine=cluster["Engine"],
                engine_version=cluster["EngineVersion"],
                subnet_group=cluster.get("CacheSubnetGroupName"),
                security_groups=[sg["SecurityGroupId"]
                                 for sg in cluster.get("SecurityGroups", [])],
                tags={},  # Tags are not included in the response
            )

        except ClientError as e:
            logger.error(f"Failed to modify maintenance window for cluster {
                         request.cluster_id}: {e}")
            raise

    def create_serverless(self, request: CreateServerlessRequest) -> ServerlessStatus:
        """Create a serverless cache."""
        try:
            params: Dict[str, Any] = {
                "CacheName": request.cache_name,
                "MajorEngineVersion": request.major_engine_version,
            }

            if request.description:
                params["Description"] = request.description
            if request.daily_backup_window:
                params["DailyBackupWindow"] = request.daily_backup_window
            if request.backup_retention_period is not None:
                params["BackupRetentionPeriod"] = request.backup_retention_period
            if request.security_group_ids:
                params["SecurityGroupIds"] = request.security_group_ids
            if request.subnet_ids:
                params["SubnetIds"] = request.subnet_ids
            if request.kms_key_id:
                params["KmsKeyId"] = request.kms_key_id
            if request.tags:
                params["Tags"] = [{"Key": k, "Value": v}
                                  for k, v in request.tags.items()]
            if request.scaling:
                params["ServerlessConfiguration"] = {
                    "MinimumCapacity": request.scaling.minimum_capacity,
                    "MaximumCapacity": request.scaling.maximum_capacity,
                }

            response = self.client.create_serverless_cache_cluster(**params)
            return self._convert_to_serverless_status(response["ServerlessCache"])

        except ClientError as e:
            logger.error(f"Failed to create serverless cache: {e}")
            raise

    def modify_serverless(self, request: ModifyServerlessRequest) -> ServerlessStatus:
        """Modify a serverless cache."""
        try:
            params: Dict[str, Any] = {
                "CacheName": request.cache_name,
            }

            if request.description:
                params["Description"] = request.description
            if request.daily_backup_window:
                params["DailyBackupWindow"] = request.daily_backup_window
            if request.backup_retention_period is not None:
                params["BackupRetentionPeriod"] = request.backup_retention_period
            if request.security_group_ids:
                params["SecurityGroupIds"] = request.security_group_ids
            if request.scaling:
                params["ServerlessConfiguration"] = {
                    "MinimumCapacity": request.scaling.minimum_capacity,
                    "MaximumCapacity": request.scaling.maximum_capacity,
                }

            response = self.client.modify_serverless_cache_cluster(**params)
            return self._convert_to_serverless_status(response["ServerlessCache"])

        except ClientError as e:
            logger.error(f"Failed to modify serverless cache: {e}")
            raise

    def delete_serverless(self, cache_name: str) -> None:
        """Delete a serverless cache."""
        try:
            self.client.delete_serverless_cache_cluster(CacheName=cache_name)
        except ClientError as e:
            logger.error(f"Failed to delete serverless cache: {e}")
            raise

    def get_serverless_status(self, cache_name: str) -> ServerlessStatus:
        """Get the status of a serverless cache."""
        try:
            response = self.client.describe_serverless_cache_clusters(
                CacheName=cache_name
            )
            return self._convert_to_serverless_status(response["ServerlessCaches"][0])
        except ClientError as e:
            logger.error(f"Failed to get serverless cache status: {e}")
            raise

    def _convert_to_serverless_status(self, cache: Dict[str, Any]) -> ServerlessStatus:
        """Convert AWS response to ServerlessStatus."""
        scaling = None
        if "ServerlessConfiguration" in cache:
            scaling = ServerlessScalingConfiguration(
                minimum_capacity=cache["ServerlessConfiguration"]["MinimumCapacity"],
                maximum_capacity=cache["ServerlessConfiguration"]["MaximumCapacity"],
            )

        return ServerlessStatus(
            cache_name=cache["CacheName"],
            status=cache["Status"],
            endpoint=cache.get("Endpoint"),
            reader_endpoint=cache.get("ReaderEndpoint"),
            major_engine_version=cache["MajorEngineVersion"],
            daily_backup_window=cache.get("DailyBackupWindow"),
            backup_retention_period=cache.get("BackupRetentionPeriod"),
            security_group_ids=cache.get("SecurityGroupIds", []),
            subnet_ids=cache.get("SubnetIds", []),
            kms_key_id=cache.get("KmsKeyId"),
            tags={tag["Key"]: tag["Value"] for tag in cache.get("Tags", [])},
            scaling=scaling,
        )
