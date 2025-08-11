import logging
from typing import Optional, Literal, List, Dict, Any
from boto3.session import Session
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor, as_completed

from chainsaws.aws.ecs.ecs_models import (
    ECSAPIConfig,
    CreateClusterResponse,
    Cluster
)

logger = logging.getLogger(__name__)


class ECS:
    """Internal ECS operations using boto3."""

    def __init__(
        self,
        boto3_session: Session,
        config: Optional[ECSAPIConfig] = None,
    ) -> None:
        """Initialize ECS client."""
        self.config = config or ECSAPIConfig()
        self.client = boto3_session.client(
            service_name="ecs",
            region_name=self.config.region if self.config else None,
        )

    def create_cluster(
        self,
        cluster_name: str,
        tags: Optional[List[Dict[str, str]]] = None,
        settings: Optional[List[Dict[Literal["name", "value"], str]]] = None,
        configuration: Optional[Dict[str, Any]] = None,
        capacity_providers: Optional[List[str]] = None,
        default_capacity_provider_strategy: Optional[List[Dict[str, Any]]] = None,
        service_connect_defaults: Optional[Dict[str, str]] = None,
    ) -> Cluster:
        """Create a new ECS cluster.

        Args:
            cluster_name: Name of your cluster (up to 255 letters, numbers, hyphens, and underscores)
            tags: Metadata tags for the cluster (max 50 tags)
            settings: Cluster settings for Container Insights. Must be list of dicts with 'name' as 'containerInsights'
                     and 'value' as one of 'enhanced', 'enabled', or 'disabled'
            configuration: Execute command and managed storage configuration
            capacity_providers: Names of capacity providers to associate
            default_capacity_provider_strategy: Default capacity provider strategy
            service_connect_defaults: Default Service Connect namespace configuration

        Returns:
            CreateClusterResponse: Response containing the created cluster details

        Raises:
            ClientError: If the request fails
        """
        try:
            params = {
                "clusterName": cluster_name
            }
            if tags:
                params["tags"] = tags
            if settings:
                params["settings"] = settings
            if configuration:
                params["configuration"] = configuration
            if capacity_providers:
                params["capacityProviders"] = capacity_providers
            if default_capacity_provider_strategy:
                params["defaultCapacityProviderStrategy"] = default_capacity_provider_strategy
            if service_connect_defaults:
                params["serviceConnectDefaults"] = service_connect_defaults

            response: CreateClusterResponse = self.client.create_cluster(
                **params)
            return response['cluster']
        except ClientError as e:
            logger.error(f"Failed to create cluster {cluster_name}: {e}")
            raise

    def delete_cluster(
        self,
        cluster_name: str,
    ) -> Cluster:
        """Delete an existing ECS cluster."""
        try:
            response = self.client.delete_cluster(cluster=cluster_name)
            return response["cluster"]
        except ClientError as e:
            logger.error(f"Failed to delete cluster {cluster_name}: {e}")
            raise

    def list_clusters(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        include: Optional[List[Literal["ATTACHMENTS",
                                       "CONFIGURATIONS", "SETTINGS", "STATISTICS", "TAGS"]]] = None,
    ) -> List[Cluster]:
        """List all ECS clusters with their details.

        Args:
            max_results: Maximum number of results to return per page
            next_token: Token for the next page of results
            include: Additional information to include in the response:
                    - ATTACHMENTS: Include attachment details
                    - CONFIGURATIONS: Include execute command and managed storage configurations
                    - SETTINGS: Include cluster settings
                    - STATISTICS: Include resource usage statistics
                    - TAGS: Include cluster tags

        Returns:
            List[Cluster]: List of cluster details

        Raises:
            ClientError: If the request fails
        """
        try:
            # First, get list of cluster ARNs
            paginator = self.client.get_paginator("list_clusters")
            params = {}
            if max_results:
                params["maxResults"] = max_results
            if next_token:
                params["nextToken"] = next_token

            clusters: List[Cluster] = []
            cluster_arns: List[str] = []
            for page in paginator.paginate(**params):
                cluster_arns.extend(page.get("clusterArns", []))

            if not cluster_arns:
                return clusters

            def describe_cluster_batch(batch: List[str]) -> List[Cluster]:
                describe_params = {"clusters": batch}
                if include:
                    describe_params["include"] = include
                response = self.client.describe_clusters(**describe_params)
                return response.get("clusters", [])

            with ThreadPoolExecutor() as executor:
                futures = []
                for i in range(0, len(cluster_arns), 100):
                    batch = cluster_arns[i:i + 100]
                    futures.append(executor.submit(
                        describe_cluster_batch, batch))

                # Collect results as they complete
                for future in as_completed(futures):
                    clusters.extend(future.result())

            return clusters
        except ClientError as e:
            logger.error(f"Failed to list clusters: {e}")
            raise

    def create_service(
        self,
        cluster_name: str,
        service_name: str,
        task_definition: str,
        desired_count: int,
        capacity_provider_strategy: Optional[List[dict]] = None,
        deployment_configuration: Optional[dict] = None,
        deployment_controller: Optional[dict] = None,
        enable_ecs_managed_tags: Optional[bool] = None,
        enable_execute_command: Optional[bool] = None,
        health_check_grace_period_seconds: Optional[int] = None,
        launch_type: Optional[Literal["EC2", "FARGATE", "EXTERNAL"]] = None,
        load_balancers: Optional[List[dict]] = None,
        network_configuration: Optional[dict] = None,
        placement_constraints: Optional[List[dict]] = None,
        placement_strategy: Optional[List[dict]] = None,
        platform_version: Optional[str] = None,
        propagate_tags: Optional[Literal["SERVICE", "TASK_DEFINITION"]] = None,
        scheduling_strategy: Optional[Literal["REPLICA", "DAEMON"]] = None,
        service_registries: Optional[List[dict]] = None,
        tags: Optional[List[dict]] = None,
    ) -> dict:
        """Create a new ECS service."""
        try:
            params = {
                "cluster": cluster_name,
                "serviceName": service_name,
                "taskDefinition": task_definition,
                "desiredCount": desired_count,
            }
            if capacity_provider_strategy:
                params["capacityProviderStrategy"] = capacity_provider_strategy
            if deployment_configuration:
                params["deploymentConfiguration"] = deployment_configuration
            if deployment_controller:
                params["deploymentController"] = deployment_controller
            if enable_ecs_managed_tags is not None:
                params["enableECSManagedTags"] = enable_ecs_managed_tags
            if enable_execute_command is not None:
                params["enableExecuteCommand"] = enable_execute_command
            if health_check_grace_period_seconds:
                params["healthCheckGracePeriodSeconds"] = health_check_grace_period_seconds
            if launch_type:
                params["launchType"] = launch_type
            if load_balancers:
                params["loadBalancers"] = load_balancers
            if network_configuration:
                params["networkConfiguration"] = network_configuration
            if placement_constraints:
                params["placementConstraints"] = placement_constraints
            if placement_strategy:
                params["placementStrategy"] = placement_strategy
            if platform_version:
                params["platformVersion"] = platform_version
            if propagate_tags:
                params["propagateTags"] = propagate_tags
            if scheduling_strategy:
                params["schedulingStrategy"] = scheduling_strategy
            if service_registries:
                params["serviceRegistries"] = service_registries
            if tags:
                params["tags"] = tags

            response = self.client.create_service(**params)
            return response["service"]
        except ClientError as e:
            logger.error(f"Failed to create service {
                         service_name} in cluster {cluster_name}: {e}")
            raise

    def update_service(
        self,
        cluster_name: str,
        service_name: str,
        desired_count: Optional[int] = None,
        task_definition: Optional[str] = None,
        capacity_provider_strategy: Optional[List[dict]] = None,
        deployment_configuration: Optional[dict] = None,
        network_configuration: Optional[dict] = None,
        placement_constraints: Optional[List[dict]] = None,
        placement_strategy: Optional[List[dict]] = None,
        platform_version: Optional[str] = None,
        force_new_deployment: Optional[bool] = None,
        health_check_grace_period_seconds: Optional[int] = None,
        enable_execute_command: Optional[bool] = None,
    ) -> dict:
        """Update an existing ECS service."""
        try:
            params = {
                "cluster": cluster_name,
                "service": service_name,
            }
            if desired_count is not None:
                params["desiredCount"] = desired_count
            if task_definition:
                params["taskDefinition"] = task_definition
            if capacity_provider_strategy:
                params["capacityProviderStrategy"] = capacity_provider_strategy
            if deployment_configuration:
                params["deploymentConfiguration"] = deployment_configuration
            if network_configuration:
                params["networkConfiguration"] = network_configuration
            if placement_constraints:
                params["placementConstraints"] = placement_constraints
            if placement_strategy:
                params["placementStrategy"] = placement_strategy
            if platform_version:
                params["platformVersion"] = platform_version
            if force_new_deployment is not None:
                params["forceNewDeployment"] = force_new_deployment
            if health_check_grace_period_seconds is not None:
                params["healthCheckGracePeriodSeconds"] = health_check_grace_period_seconds
            if enable_execute_command is not None:
                params["enableExecuteCommand"] = enable_execute_command

            response = self.client.update_service(**params)
            return response["service"]
        except ClientError as e:
            logger.error(f"Failed to update service {
                         service_name} in cluster {cluster_name}: {e}")
            raise

    def delete_service(
        self,
        cluster_name: str,
        service_name: str,
        force: bool = False,
    ) -> dict:
        """Delete an ECS service."""
        try:
            params = {
                "cluster": cluster_name,
                "service": service_name,
                "force": force,
            }
            response = self.client.delete_service(**params)
            return response["service"]
        except ClientError as e:
            logger.error(f"Failed to delete service {
                         service_name} in cluster {cluster_name}: {e}")
            raise

    def list_services(
        self,
        cluster_name: str,
        launch_type: Optional[Literal["EC2", "FARGATE", "EXTERNAL"]] = None,
        scheduling_strategy: Optional[Literal["REPLICA", "DAEMON"]] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list:
        """List all services within a cluster."""
        try:
            paginator = self.client.get_paginator("list_services")
            services = []
            params = {"cluster": cluster_name}
            if launch_type:
                params["launchType"] = launch_type
            if scheduling_strategy:
                params["schedulingStrategy"] = scheduling_strategy
            if max_results:
                params["maxResults"] = max_results
            if next_token:
                params["nextToken"] = next_token

            for page in paginator.paginate(**params):
                services.extend(page.get("serviceArns", []))
            return services
        except ClientError as e:
            logger.error(f"Failed to list services in cluster {
                         cluster_name}: {e}")
            raise

    def run_task(
        self,
        cluster_name: str,
        task_definition: str,
        capacity_provider_strategy: Optional[List[dict]] = None,
        count: int = 1,
        enable_ecs_managed_tags: Optional[bool] = None,
        enable_execute_command: Optional[bool] = None,
        group: Optional[str] = None,
        launch_type: Optional[Literal["EC2", "FARGATE", "EXTERNAL"]] = None,
        network_configuration: Optional[dict] = None,
        overrides: Optional[dict] = None,
        placement_constraints: Optional[List[dict]] = None,
        placement_strategy: Optional[List[dict]] = None,
        platform_version: Optional[str] = None,
        propagate_tags: Optional[Literal["TASK_DEFINITION"]] = None,
        reference_id: Optional[str] = None,
        started_by: Optional[str] = None,
        tags: Optional[List[dict]] = None,
    ) -> dict:
        """Run a new task on ECS."""
        try:
            params = {
                "cluster": cluster_name,
                "taskDefinition": task_definition,
                "count": count,
            }
            if capacity_provider_strategy:
                params["capacityProviderStrategy"] = capacity_provider_strategy
            if enable_ecs_managed_tags is not None:
                params["enableECSManagedTags"] = enable_ecs_managed_tags
            if enable_execute_command is not None:
                params["enableExecuteCommand"] = enable_execute_command
            if group:
                params["group"] = group
            if launch_type:
                params["launchType"] = launch_type
            if network_configuration:
                params["networkConfiguration"] = network_configuration
            if overrides:
                params["overrides"] = overrides
            if placement_constraints:
                params["placementConstraints"] = placement_constraints
            if placement_strategy:
                params["placementStrategy"] = placement_strategy
            if platform_version:
                params["platformVersion"] = platform_version
            if propagate_tags:
                params["propagateTags"] = propagate_tags
            if reference_id:
                params["referenceId"] = reference_id
            if started_by:
                params["startedBy"] = started_by
            if tags:
                params["tags"] = tags

            response = self.client.run_task(**params)
            return response["tasks"]
        except ClientError as e:
            logger.error(f"Failed to run task in cluster {cluster_name}: {e}")
            raise

    def stop_task(
        self,
        cluster_name: str,
        task_id: str,
        reason: Optional[str] = None,
    ) -> dict:
        """Stop a running task."""
        try:
            params = {
                "cluster": cluster_name,
                "task": task_id,
            }
            if reason:
                params["reason"] = reason

            response = self.client.stop_task(**params)
            return response["task"]
        except ClientError as e:
            logger.error(f"Failed to stop task {
                         task_id} in cluster {cluster_name}: {e}")
            raise

    def list_tasks(
        self,
        cluster_name: str,
        container_instance: Optional[str] = None,
        desired_status: Optional[Literal["RUNNING",
                                         "PENDING", "STOPPED"]] = None,
        family: Optional[str] = None,
        launch_type: Optional[Literal["EC2", "FARGATE", "EXTERNAL"]] = None,
        service_name: Optional[str] = None,
        started_by: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list:
        """List all tasks within a cluster or service."""
        try:
            paginator = self.client.get_paginator("list_tasks")
            tasks = []
            params = {"cluster": cluster_name}
            if container_instance:
                params["containerInstance"] = container_instance
            if desired_status:
                params["desiredStatus"] = desired_status
            if family:
                params["family"] = family
            if launch_type:
                params["launchType"] = launch_type
            if service_name:
                params["serviceName"] = service_name
            if started_by:
                params["startedBy"] = started_by
            if max_results:
                params["maxResults"] = max_results
            if next_token:
                params["nextToken"] = next_token

            for page in paginator.paginate(**params):
                tasks.extend(page.get("taskArns", []))
            return tasks
        except ClientError as e:
            logger.error(f"Failed to list tasks in cluster {
                         cluster_name}: {e}")
            raise

    def register_task_definition(
        self,
        family: str,
        container_definitions: List[dict],
        cpu: Optional[str] = None,
        ephemeral_storage: Optional[dict] = None,
        execution_role_arn: Optional[str] = None,
        inference_accelerators: Optional[List[dict]] = None,
        ipc_mode: Optional[Literal["host", "task", "none"]] = None,
        memory: Optional[str] = None,
        network_mode: Optional[Literal["bridge",
                                       "host", "awsvpc", "none"]] = None,
        pid_mode: Optional[Literal["host", "task"]] = None,
        placement_constraints: Optional[List[dict]] = None,
        proxy_configuration: Optional[dict] = None,
        requires_compatibilities: Optional[List[Literal["EC2", "FARGATE"]]] = None,
        runtime_platform: Optional[dict] = None,
        tags: Optional[List[dict]] = None,
        task_role_arn: Optional[str] = None,
        volumes: Optional[List[dict]] = None,
    ) -> dict:
        """Register a new task definition."""
        try:
            params = {
                "family": family,
                "containerDefinitions": container_definitions,
            }
            if cpu:
                params["cpu"] = cpu
            if ephemeral_storage:
                params["ephemeralStorage"] = ephemeral_storage
            if execution_role_arn:
                params["executionRoleArn"] = execution_role_arn
            if inference_accelerators:
                params["inferenceAccelerators"] = inference_accelerators
            if ipc_mode:
                params["ipcMode"] = ipc_mode
            if memory:
                params["memory"] = memory
            if network_mode:
                params["networkMode"] = network_mode
            if pid_mode:
                params["pidMode"] = pid_mode
            if placement_constraints:
                params["placementConstraints"] = placement_constraints
            if proxy_configuration:
                params["proxyConfiguration"] = proxy_configuration
            if requires_compatibilities:
                params["requiresCompatibilities"] = requires_compatibilities
            if runtime_platform:
                params["runtimePlatform"] = runtime_platform
            if tags:
                params["tags"] = tags
            if task_role_arn:
                params["taskRoleArn"] = task_role_arn
            if volumes:
                params["volumes"] = volumes

            response = self.client.register_task_definition(**params)
            return response["taskDefinition"]
        except ClientError as e:
            logger.error(f"Failed to register task definition {family}: {e}")
            raise

    def deregister_task_definition(
        self,
        task_definition: str,
    ) -> dict:
        """Deregister an existing task definition."""
        try:
            response = self.client.deregister_task_definition(
                taskDefinition=task_definition,
            )
            return response["taskDefinition"]
        except ClientError as e:
            logger.error(f"Failed to deregister task definition {
                         task_definition}: {e}")
            raise

    def list_task_definitions(
        self,
        family_prefix: Optional[str] = None,
        status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE",
        sort: Literal["ASC", "DESC"] = "ASC",
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list:
        """List all task definitions."""
        try:
            paginator = self.client.get_paginator("list_task_definitions")
            params = {"status": status, "sort": sort}
            if family_prefix:
                params["familyPrefix"] = family_prefix
            if max_results:
                params["maxResults"] = max_results
            if next_token:
                params["nextToken"] = next_token

            definitions = []
            for page in paginator.paginate(**params):
                definitions.extend(page.get("taskDefinitionArns", []))
            return definitions
        except ClientError:
            logger.error("Failed to list task definitions: {e}")
            raise

    def list_container_instances(
        self,
        cluster_name: str,
        filter: Optional[str] = None,
        status: Optional[Literal["ACTIVE", "DRAINING", "REGISTERING",
                                 "DEREGISTERING", "REGISTRATION_FAILED"]] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list:
        """List all container instances in a cluster."""
        try:
            paginator = self.client.get_paginator("list_container_instances")
            params = {"cluster": cluster_name}
            if filter:
                params["filter"] = filter
            if status:
                params["status"] = status
            if max_results:
                params["maxResults"] = max_results
            if next_token:
                params["nextToken"] = next_token

            instances = []
            for page in paginator.paginate(**params):
                instances.extend(page.get("containerInstanceArns", []))
            return instances
        except ClientError as e:
            logger.error(f"Failed to list container instances in cluster {
                         cluster_name}: {e}")
            raise

    def describe_container_instances(
        self,
        cluster_name: str,
        container_instance_ids: List[str],
        include: Optional[List[Literal["TAGS",
                                       "CONTAINER_INSTANCE_HEALTH"]]] = None,
    ) -> dict:
        """Describe specific container instances."""
        try:
            params = {
                "cluster": cluster_name,
                "containerInstances": container_instance_ids,
            }
            if include:
                params["include"] = include

            response = self.client.describe_container_instances(**params)
            return response["containerInstances"]
        except ClientError as e:
            logger.error(f"Failed to describe container instances in cluster {
                         cluster_name}: {e}")
            raise

    # Placeholder for logging and monitoring methods
    # def get_service_logs(self, ...):
    #     pass

    # def get_task_logs(self, ...):
    #     pass
