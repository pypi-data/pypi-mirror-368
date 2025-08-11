from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict

from chainsaws.aws.shared.config import APIConfig


@dataclass
class ECSAPIConfig(APIConfig):
    """Configuration for ECS API."""
    max_retries: int = 3  # Maximum number of API call retries
    timeout: int = 30  # Timeout for API calls in seconds


@dataclass
class CapacityProviderStrategy:
    """Capacity provider strategy in cluster response."""
    capacity_provider: str
    weight: int
    base: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return {
            "capacityProvider": self.capacity_provider,
            "weight": self.weight,
            "base": self.base
        }


@dataclass
class AttachmentDetail:
    """Attachment detail in cluster response."""
    name: str
    value: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return asdict(self)


@dataclass
class ClusterAttachment:
    """Attachment in cluster response."""
    id: str
    type: str
    status: str
    details: List[AttachmentDetail]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = asdict(self)
        result["details"] = [detail.to_dict() for detail in self.details]
        return result


@dataclass
class ServiceConnectDefaults:
    """Service connect defaults in cluster response."""
    namespace: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return asdict(self)


@dataclass
class Cluster:
    """Cluster details in response."""
    cluster_arn: str
    cluster_name: str
    configuration: Dict[str, Any]
    status: str
    registered_container_instances_count: int = 0
    running_tasks_count: int = 0
    pending_tasks_count: int = 0
    active_services_count: int = 0
    statistics: List[Dict[str, str]] = field(default_factory=list)
    tags: List[Dict[str, str]] = field(default_factory=list)
    settings: List[Dict[str, str]] = field(default_factory=list)
    capacity_providers: List[str] = field(default_factory=list)
    default_capacity_provider_strategy: List[CapacityProviderStrategy] = field(
        default_factory=list)
    attachments: List[ClusterAttachment] = field(default_factory=list)
    attachments_status: str = ""
    service_connect_defaults: Optional[ServiceConnectDefaults] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = {
            "clusterArn": self.cluster_arn,
            "clusterName": self.cluster_name,
            "configuration": self.configuration,
            "status": self.status,
            "registeredContainerInstancesCount": self.registered_container_instances_count,
            "runningTasksCount": self.running_tasks_count,
            "pendingTasksCount": self.pending_tasks_count,
            "activeServicesCount": self.active_services_count,
            "statistics": self.statistics,
            "tags": self.tags,
            "settings": self.settings,
            "capacityProviders": self.capacity_providers,
            "defaultCapacityProviderStrategy": [s.to_dict() for s in self.default_capacity_provider_strategy],
            "attachments": [a.to_dict() for a in self.attachments],
            "attachmentsStatus": self.attachments_status,
        }
        if self.service_connect_defaults:
            result["serviceConnectDefaults"] = self.service_connect_defaults.to_dict()
        return result


@dataclass
class CreateClusterResponse:
    """Response from create_cluster API call."""
    cluster: Cluster

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return {"cluster": self.cluster.to_dict()}


@dataclass
class ContainerDefinition:
    """Container definition for ECS task."""
    name: str  # Container name
    image: str  # Container image
    cpu: int = 256  # CPU units
    memory: int = 512  # Memory in MB
    essential: bool = True  # Whether container is essential
    port_mappings: List[Dict[str, Any]] = field(
        default_factory=list)  # Port mappings
    environment: List[Dict[str, str]] = field(
        default_factory=list)  # Environment variables
    secrets: List[Dict[str, str]] = field(
        default_factory=list)  # Secret variables
    mount_points: List[Dict[str, Any]] = field(
        default_factory=list)  # Mount points
    volumes_from: List[Dict[str, Any]] = field(
        default_factory=list)  # Volumes from other containers
    log_configuration: Optional[Dict[str, Any]] = None  # Log configuration
    health_check: Optional[Dict[str, Any]] = None  # Health check configuration
    linux_parameters: Optional[Dict[str, Any]] = None  # Linux parameters
    entry_point: Optional[List[str]] = None  # Container entry point
    command: Optional[List[str]] = None  # Container command


@dataclass
class TaskDefinition:
    """Task definition for ECS service."""
    family: str  # Task definition family
    containers: List[ContainerDefinition]  # Container definitions
    cpu: str = "256"  # Total CPU units
    memory: str = "512"  # Total memory in MB
    network_mode: str = "awsvpc"  # Network mode
    execution_role_arn: Optional[str] = None  # Task execution role ARN
    task_role_arn: Optional[str] = None  # Task role ARN
    volumes: List[Dict[str, Any]] = field(
        default_factory=list)  # Volume definitions
    placement_constraints: List[Dict[str, str]] = field(
        default_factory=list)  # Placement constraints
    requires_compatibilities: List[str] = field(
        default_factory=lambda: ["FARGATE"])  # Required compatibilities


@dataclass
class ServiceDefinition:
    """Service definition for ECS cluster."""
    name: str  # Service name
    cluster: str  # Cluster name
    task_definition: str  # Task definition ARN
    desired_count: int = 1  # Desired task count
    launch_type: str = "FARGATE"  # Launch type
    # Network configuration
    network_configuration: Optional[Dict[str, Any]] = None
    load_balancers: List[Dict[str, Any]] = field(
        default_factory=list)  # Load balancer configuration
    service_registries: List[Dict[str, Any]] = field(
        default_factory=list)  # Service discovery configuration
    scheduling_strategy: str = "REPLICA"  # Scheduling strategy
    deployment_configuration: Dict[str, Any] = field(
        default_factory=lambda: {
            "maximumPercent": 200,
            "minimumHealthyPercent": 100,
        })  # Deployment configuration
    placement_constraints: List[Dict[str, str]] = field(
        default_factory=list)  # Placement constraints
    placement_strategy: List[Dict[str, str]] = field(
        default_factory=list)  # Placement strategy
    # Health check grace period
    health_check_grace_period_seconds: Optional[int] = None
    platform_version: Optional[str] = None  # Platform version
    tags: Dict[str, str] = field(default_factory=dict)  # Service tags


@dataclass
class ClusterConfiguration:
    """Configuration for ECS cluster."""
    cluster_name: str  # Cluster name
    capacity_providers: list[str] = field(
        # Capacity providers
        default_factory=lambda: ["FARGATE", "FARGATE_SPOT"])
    default_capacity_provider_strategy: list[dict[str, Any]] = field(
        default_factory=lambda: [{
            "capacityProvider": "FARGATE",
            "weight": 1,
            "base": 1
        }])  # Default capacity provider strategy
    settings: list[dict[str, str]] = field(
        default_factory=list)  # Cluster settings
    configuration: dict[str, Any] = field(
        default_factory=dict)  # Additional configuration
    tags: list[dict[str, str]] = field(
        default_factory=list)  # Cluster tags
    # Service connect defaults
    service_connect_defaults: Optional[dict[str, str]] = None


@dataclass
class AutoScalingConfiguration:
    """Configuration for ECS service auto scaling."""
    service_namespace: str  # Service namespace
    resource_id: str  # Resource ID
    scalable_dimension: str  # Scalable dimension
    min_capacity: int  # Minimum capacity
    max_capacity: int  # Maximum capacity
    target_tracking_scaling_policies: List[Dict[str, Any]] = field(
        default_factory=list)  # Target tracking scaling policies
    step_scaling_policies: List[Dict[str, Any]] = field(
        default_factory=list)  # Step scaling policies
    scheduled_actions: List[Dict[str, Any]] = field(
        default_factory=list)  # Scheduled actions


@dataclass
class TaskSet:
    """Task set configuration for ECS service."""
    service: str  # Service name
    cluster: str  # Cluster name
    task_definition: str  # Task definition ARN
    external_id: Optional[str] = None  # External ID
    # Network configuration
    network_configuration: Optional[Dict[str, Any]] = None
    load_balancers: List[Dict[str, Any]] = field(
        default_factory=list)  # Load balancer configuration
    service_registries: List[Dict[str, Any]] = field(
        default_factory=list)  # Service discovery configuration
    launch_type: str = "FARGATE"  # Launch type
    capacity_provider_strategy: List[Dict[str, Any]] = field(
        default_factory=list)  # Capacity provider strategy
    platform_version: Optional[str] = None  # Platform version
    scale: Dict[str, Any] = field(
        # Scale configuration
        default_factory=lambda: {"unit": "PERCENT", "value": 100})
    client_token: Optional[str] = None  # Client token for idempotency
    tags: Dict[str, str] = field(default_factory=dict)  # Task set tags
