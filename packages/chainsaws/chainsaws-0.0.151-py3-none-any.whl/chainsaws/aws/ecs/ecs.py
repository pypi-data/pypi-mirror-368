import logging
from typing import Optional, List, Dict, Any, Literal

from chainsaws.aws.shared import session

from chainsaws.aws.ecs._ecs_internal import ECS
from chainsaws.aws.ecs.ecs_models import (
    ECSAPIConfig,
    ClusterConfiguration,
    ServiceConfiguration,
    TaskConfiguration,
    TaskDefinitionConfiguration,
    Cluster
)
from chainsaws.aws.ecs.ecs_exceptions import (
    ECSClusterException,
    ECSServiceException,
    ECSTaskException,
    ECSTaskDefinitionException,
    ECSContainerInstanceException,
)

logger = logging.getLogger(__name__)

# TODO: Test this


class ECSAPI:
    def __init__(
        self,
        config: Optional[ECSAPIConfig] = None,
    ) -> None:
        """Initialize ECS API.

        Args:
            boto3_session: Boto3 session
            config: Optional ECS configuration
        """
        self.config = config or ECSAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.ecs = ECS(
            boto3_session=self.boto3_session,
            config=self.config,
        )

    def create_cluster(self, config: ClusterConfiguration) -> Cluster:
        """Create a new ECS cluster.

        Args:
            config: Cluster configuration containing:
                - cluster_name: Name of your cluster (up to 255 letters, numbers, hyphens, and underscores)
                - tags: Optional metadata tags for the cluster (max 50 tags)
                - settings: Optional Container Insights settings (name must be 'containerInsights', value one of 'enhanced', 'enabled', 'disabled')
                - configuration: Optional execute command and managed storage configuration
                - capacity_providers: Optional names of capacity providers to associate
                - default_capacity_provider_strategy: Optional default capacity provider strategy
                - service_connect_defaults: Optional default Service Connect namespace configuration

        Returns:
            CreateClusterResponse: Response containing the created cluster details

        Raises:
            ECSClusterException: If cluster creation fails
        """
        try:
            return self.ecs.create_cluster(
                cluster_name=config.cluster_name,
                tags=[tag.to_dict()
                      for tag in config.tags] if config.tags else None,
                settings=[setting.to_dict()
                          for setting in config.settings] if config.settings else None,
                configuration=config.configuration,
                capacity_providers=config.capacity_providers,
                default_capacity_provider_strategy=[
                    strategy.to_dict() for strategy in config.default_capacity_provider_strategy
                ] if config.default_capacity_provider_strategy else None,
                service_connect_defaults=config.service_connect_defaults,
            )
        except Exception as e:
            logger.error(f"Failed to create cluster {
                         config.cluster_name}: {e}")
            raise ECSClusterException(f"Failed to create cluster: {e}") from e

    def delete_cluster(self, cluster_name: str) -> Cluster:
        """Delete an ECS cluster.

        Args:
            cluster_name: Name of the cluster to delete

        Returns:
            Deleted cluster details

        Raises:
            ECSClusterException: If cluster deletion fails
        """
        try:
            return self.ecs.delete_cluster(cluster_name=cluster_name)
        except Exception as e:
            logger.error(f"Failed to delete cluster {cluster_name}: {e}")
            raise ECSClusterException(f"Failed to delete cluster: {e}") from e

    def list_clusters(
        self,
        max_results: Optional[int] = None,
        include: Optional[List[Literal["ATTACHMENTS",
                                       "CONFIGURATIONS", "SETTINGS", "STATISTICS", "TAGS"]]] = None,
    ) -> List[Cluster]:
        """List all ECS clusters with their details.

        Args:
            max_results: Maximum number of results to return per page
            include: Additional information to include in the response:
                    - ATTACHMENTS: Include attachment details
                    - CONFIGURATIONS: Include execute command and managed storage configurations
                    - SETTINGS: Include cluster settings
                    - STATISTICS: Include resource usage statistics
                    - TAGS: Include cluster tags

        Returns:
            List[Cluster]: List of cluster details with specified information included

        Raises:
            ECSClusterException: If listing clusters fails
        """
        try:
            return self.ecs.list_clusters(
                max_results=max_results,
                include=include,
            )
        except Exception as e:
            logger.error(f"Failed to list clusters: {e}")
            raise ECSClusterException(f"Failed to list clusters: {e}") from e

    def create_service(self, config: ServiceConfiguration) -> Dict[str, Any]:
        """Create a new ECS service.

        Args:
            config: Service configuration

        Returns:
            Created service details

        Raises:
            ServiceException: If service creation fails
        """
        try:
            return self.ecs.create_service(
                cluster_name=config.cluster_name,
                service_name=config.service_name,
                task_definition=config.task_definition,
                desired_count=config.desired_count,
                capacity_provider_strategy=[
                    strategy.__dict__ for strategy in config.capacity_provider_strategy
                ] if config.capacity_provider_strategy else None,
                deployment_configuration=config.deployment_configuration.__dict__ if config.deployment_configuration else None,
                deployment_controller=config.deployment_controller.__dict__ if config.deployment_controller else None,
                enable_ecs_managed_tags=config.enable_ecs_managed_tags,
                enable_execute_command=config.enable_execute_command,
                health_check_grace_period_seconds=config.health_check_grace_period_seconds,
                launch_type=config.launch_type,
                load_balancers=[
                    lb.__dict__ for lb in config.load_balancers] if config.load_balancers else None,
                network_configuration=config.network_configuration.__dict__ if config.network_configuration else None,
                placement_constraints=[
                    constraint.__dict__ for constraint in config.placement_constraints
                ] if config.placement_constraints else None,
                placement_strategy=[
                    strategy.__dict__ for strategy in config.placement_strategy
                ] if config.placement_strategy else None,
                platform_version=config.platform_version,
                propagate_tags=config.propagate_tags,
                scheduling_strategy=config.scheduling_strategy,
                service_registries=[
                    registry.__dict__ for registry in config.service_registries
                ] if config.service_registries else None,
                tags=[tag.__dict__ for tag in config.tags] if config.tags else None,
            )
        except Exception as e:
            logger.error(f"Failed to create service {
                         config.service_name} in cluster {config.cluster_name}: {e}")
            raise ECSServiceException(f"Failed to create service: {e}") from e

    def update_service(
        self,
        cluster_name: str,
        service_name: str,
        desired_count: Optional[int] = None,
        task_definition: Optional[str] = None,
        force_new_deployment: Optional[bool] = None,
        health_check_grace_period_seconds: Optional[int] = None,
        platform_version: Optional[str] = None,
        deployment_configuration: Optional[Dict[str, Any]] = None,
        network_configuration: Optional[Dict[str, Any]] = None,
        capacity_provider_strategy: Optional[List[Dict[str, Any]]] = None,
        enable_execute_command: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update an existing ECS service.

        Args:
            cluster_name: Name of the cluster
            service_name: Name of the service to update
            desired_count: Desired number of tasks
            task_definition: Task definition to use
            force_new_deployment: Whether to force a new deployment
            health_check_grace_period_seconds: Health check grace period
            platform_version: Platform version
            deployment_configuration: Deployment configuration
            network_configuration: Network configuration
            capacity_provider_strategy: Capacity provider strategy
            enable_execute_command: Whether to enable execute command

        Returns:
            Updated service details

        Raises:
            ServiceException: If service update fails
        """
        try:
            return self.ecs.update_service(
                cluster_name=cluster_name,
                service_name=service_name,
                desired_count=desired_count,
                task_definition=task_definition,
                force_new_deployment=force_new_deployment,
                health_check_grace_period_seconds=health_check_grace_period_seconds,
                platform_version=platform_version,
                deployment_configuration=deployment_configuration,
                network_configuration=network_configuration,
                capacity_provider_strategy=capacity_provider_strategy,
                enable_execute_command=enable_execute_command,
            )
        except Exception as e:
            logger.error(f"Failed to update service {
                         service_name} in cluster {cluster_name}: {e}")
            raise ECSServiceException(f"Failed to update service: {e}") from e

    def delete_service(
        self,
        cluster_name: str,
        service_name: str,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Delete an ECS service.

        Args:
            cluster_name: Name of the cluster
            service_name: Name of the service to delete
            force: Whether to force deletion

        Returns:
            Deleted service details

        Raises:
            ServiceException: If service deletion fails
        """
        try:
            return self.ecs.delete_service(
                cluster_name=cluster_name,
                service_name=service_name,
                force=force,
            )
        except Exception as e:
            logger.error(f"Failed to delete service {
                         service_name} in cluster {cluster_name}: {e}")
            raise ECSServiceException(f"Failed to delete service: {e}") from e

    def list_services(
        self,
        cluster_name: str,
        launch_type: Optional[str] = None,
        scheduling_strategy: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> List[str]:
        """List all services in a cluster.

        Args:
            cluster_name: Name of the cluster
            launch_type: Filter by launch type
            scheduling_strategy: Filter by scheduling strategy
            max_results: Maximum number of results to return

        Returns:
            List of service ARNs

        Raises:
            ServiceException: If listing services fails
        """
        try:
            return self.ecs.list_services(
                cluster_name=cluster_name,
                launch_type=launch_type,
                scheduling_strategy=scheduling_strategy,
                max_results=max_results,
            )
        except Exception as e:
            logger.error(f"Failed to list services in cluster {
                         cluster_name}: {e}")
            raise ECSServiceException(f"Failed to list services: {e}") from e

    def run_task(self, config: TaskConfiguration) -> Dict[str, Any]:
        """Run a new task.

        Args:
            config: Task configuration

        Returns:
            Task details

        Raises:
            TaskException: If task execution fails
        """
        try:
            return self.ecs.run_task(
                cluster_name=config.cluster_name,
                task_definition=config.task_definition,
                capacity_provider_strategy=[
                    strategy.__dict__ for strategy in config.capacity_provider_strategy
                ] if config.capacity_provider_strategy else None,
                count=config.count,
                enable_ecs_managed_tags=config.enable_ecs_managed_tags,
                enable_execute_command=config.enable_execute_command,
                group=config.group,
                launch_type=config.launch_type,
                network_configuration=config.network_configuration.__dict__ if config.network_configuration else None,
                overrides=config.overrides,
                placement_constraints=[
                    constraint.__dict__ for constraint in config.placement_constraints
                ] if config.placement_constraints else None,
                placement_strategy=[
                    strategy.__dict__ for strategy in config.placement_strategy
                ] if config.placement_strategy else None,
                platform_version=config.platform_version,
                propagate_tags=config.propagate_tags,
                reference_id=config.reference_id,
                started_by=config.started_by,
                tags=[tag.__dict__ for tag in config.tags] if config.tags else None,
            )
        except Exception as e:
            logger.error(f"Failed to run task in cluster {
                         config.cluster_name}: {e}")
            raise ECSTaskException(f"Failed to run task: {e}") from e

    def stop_task(
        self,
        cluster_name: str,
        task_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Stop a running task.

        Args:
            cluster_name: Name of the cluster
            task_id: ID of the task to stop
            reason: Reason for stopping the task

        Returns:
            Stopped task details

        Raises:
            TaskException: If task stop fails
        """
        try:
            return self.ecs.stop_task(
                cluster_name=cluster_name,
                task_id=task_id,
                reason=reason,
            )
        except Exception as e:
            logger.error(f"Failed to stop task {
                         task_id} in cluster {cluster_name}: {e}")
            raise ECSTaskException(f"Failed to stop task: {e}") from e

    def list_tasks(
        self,
        cluster_name: str,
        service_name: Optional[str] = None,
        container_instance: Optional[str] = None,
        desired_status: Optional[str] = None,
        family: Optional[str] = None,
        launch_type: Optional[str] = None,
        started_by: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> List[str]:
        """List tasks in a cluster.

        Args:
            cluster_name: Name of the cluster
            service_name: Filter by service name
            container_instance: Filter by container instance
            desired_status: Filter by desired status
            family: Filter by family
            launch_type: Filter by launch type
            started_by: Filter by who started the task
            max_results: Maximum number of results to return

        Returns:
            List of task ARNs

        Raises:
            TaskException: If listing tasks fails
        """
        try:
            return self.ecs.list_tasks(
                cluster_name=cluster_name,
                service_name=service_name,
                container_instance=container_instance,
                desired_status=desired_status,
                family=family,
                launch_type=launch_type,
                started_by=started_by,
                max_results=max_results,
            )
        except Exception as e:
            logger.error(f"Failed to list tasks in cluster {
                         cluster_name}: {e}")
            raise ECSTaskException(f"Failed to list tasks: {e}") from e

    def register_task_definition(self, config: TaskDefinitionConfiguration) -> Dict[str, Any]:
        """Register a new task definition.

        Args:
            config: Task definition configuration

        Returns:
            Registered task definition details

        Raises:
            TaskDefinitionException: If task definition registration fails
        """
        try:
            return self.ecs.register_task_definition(
                family=config.family,
                container_definitions=[
                    container.__dict__ for container in config.container_definitions
                ],
                cpu=config.cpu,
                ephemeral_storage=config.ephemeral_storage.__dict__ if config.ephemeral_storage else None,
                execution_role_arn=config.execution_role_arn,
                inference_accelerators=[
                    accelerator.__dict__ for accelerator in config.inference_accelerators
                ] if config.inference_accelerators else None,
                ipc_mode=config.ipc_mode,
                memory=config.memory,
                network_mode=config.network_mode,
                pid_mode=config.pid_mode,
                placement_constraints=[
                    constraint.__dict__ for constraint in config.placement_constraints
                ] if config.placement_constraints else None,
                proxy_configuration=config.proxy_configuration.__dict__ if config.proxy_configuration else None,
                requires_compatibilities=config.requires_compatibilities,
                runtime_platform=config.runtime_platform.__dict__ if config.runtime_platform else None,
                tags=[tag.__dict__ for tag in config.tags] if config.tags else None,
                task_role_arn=config.task_role_arn,
                volumes=[
                    volume.__dict__ for volume in config.volumes] if config.volumes else None,
            )
        except Exception as e:
            logger.error(f"Failed to register task definition {
                         config.family}: {e}")
            raise ECSTaskDefinitionException(
                f"Failed to register task definition: {e}") from e

    def deregister_task_definition(self, task_definition: str) -> Dict[str, Any]:
        """Deregister a task definition.

        Args:
            task_definition: Task definition to deregister

        Returns:
            Deregistered task definition details

        Raises:
            TaskDefinitionException: If task definition deregistration fails
        """
        try:
            return self.ecs.deregister_task_definition(task_definition=task_definition)
        except Exception as e:
            logger.error(f"Failed to deregister task definition {
                         task_definition}: {e}")
            raise ECSTaskDefinitionException(
                f"Failed to deregister task definition: {e}") from e

    def list_task_definitions(
        self,
        family_prefix: Optional[str] = None,
        status: str = "ACTIVE",
        sort: str = "ASC",
        max_results: Optional[int] = None,
    ) -> List[str]:
        """List task definitions.

        Args:
            family_prefix: Filter by family prefix
            status: Filter by status
            sort: Sort order
            max_results: Maximum number of results to return

        Returns:
            List of task definition ARNs

        Raises:
            TaskDefinitionException: If listing task definitions fails
        """
        try:
            return self.ecs.list_task_definitions(
                family_prefix=family_prefix,
                status=status,
                sort=sort,
                max_results=max_results,
            )
        except Exception as e:
            logger.error(f"Failed to list task definitions: {e}")
            raise ECSTaskDefinitionException(
                f"Failed to list task definitions: {e}") from e

    def list_container_instances(
        self,
        cluster_name: str,
        filter: Optional[str] = None,
        status: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> List[str]:
        """List container instances in a cluster.

        Args:
            cluster_name: Name of the cluster
            filter: Filter expression
            status: Filter by status
            max_results: Maximum number of results to return

        Returns:
            List of container instance ARNs

        Raises:
            ContainerInstanceException: If listing container instances fails
        """
        try:
            return self.ecs.list_container_instances(
                cluster_name=cluster_name,
                filter=filter,
                status=status,
                max_results=max_results,
            )
        except Exception as e:
            logger.error(f"Failed to list container instances in cluster {
                         cluster_name}: {e}")
            raise ECSContainerInstanceException(
                f"Failed to list container instances: {e}") from e

    def describe_container_instances(
        self,
        cluster_name: str,
        container_instance_ids: List[str],
        include: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Describe container instances.

        Args:
            cluster_name: Name of the cluster
            container_instance_ids: List of container instance IDs
            include: Additional information to include

        Returns:
            List of container instance details

        Raises:
            ContainerInstanceException: If describing container instances fails
        """
        try:
            return self.ecs.describe_container_instances(
                cluster_name=cluster_name,
                container_instance_ids=container_instance_ids,
                include=include,
            )
        except Exception as e:
            logger.error(f"Failed to describe container instances in cluster {
                         cluster_name}: {e}")
            raise ECSContainerInstanceException(
                f"Failed to describe container instances: {e}") from e
