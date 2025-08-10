from datetime import datetime
from typing import Any, Literal, Optional, TypedDict
from dataclasses import dataclass, field

from chainsaws.aws.shared.config import APIConfig


@dataclass
class SSMAPIConfig(APIConfig):
    """Configuration for SSM client."""

    max_retries: int = 3  # Maximum number of API call retries
    timeout: int = 30  # Timeout for API calls in seconds


@dataclass
class ParameterConfig:
    """Configuration for SSM Parameter."""

    name: str  # Parameter name
    value: str  # Parameter value
    type: Literal["String", "StringList",
                  "SecureString"] = "String"  # Parameter type
    description: str | None = None  # Parameter description
    tier: Literal["Standard", "Advanced",
                  "Intelligent-Tiering"] = "Standard"  # Parameter tier
    tags: dict[str, str] | None = None  # Resource tags
    overwrite: bool = False  # Whether to overwrite existing parameter


@dataclass
class Parameter:
    """SSM Parameter details."""

    name: str  # Parameter name
    type: str  # Parameter type
    value: str  # Parameter value
    version: int  # Parameter version
    last_modified_date: datetime  # Last modification date
    arn: str  # Parameter ARN
    data_type: str  # Parameter data type


@dataclass
class ParameterHistory:
    """SSM Parameter history entry."""

    name: str  # Parameter name
    type: str  # Parameter type
    value: str  # Parameter value
    version: int  # Parameter version
    last_modified_date: datetime  # Last modification date
    last_modified_user: str  # User who modified the parameter
    description: str | None = None  # Parameter description
    labels: list[str] | None = field(default_factory=list)  # Parameter labels


@dataclass
class ParameterLabel:
    """SSM Parameter label configuration."""

    name: str  # Parameter name
    labels: list[str]  # Labels to apply


@dataclass
class ParameterTier:
    """SSM Parameter tier configuration."""

    name: str  # Parameter name
    tier: Literal["Standard", "Advanced",
                  "Intelligent-Tiering"]  # Parameter tier


@dataclass
class ParameterPolicy:
    """SSM Parameter policy configuration."""

    name: str  # Parameter name
    policies: list[dict[str, str]]  # Parameter policies


@dataclass
class ParameterSearch:
    """SSM Parameter search configuration."""

    path: str  # Parameter path to search
    recursive: bool = True  # Whether to search recursively
    max_results: int = 50  # Maximum number of results to return
    with_decryption: bool = False  # Whether to decrypt SecureString values


class ParameterDetails(TypedDict):
    name: str
    value: str
    type: str
    description: Optional[str]
    tier: str
    tags: Optional[dict[str, str]]
    overwrite: bool


@dataclass
class CommandConfig:
    """Configuration for SSM Run Command."""

    # Target instances (by tags or instance IDs)
    targets: list[dict[str, list[str]]]
    document_name: str  # SSM document name to execute
    parameters: dict[str, list[str]] | None = None  # Command parameters
    comment: str | None = None  # Command comment
    timeout_seconds: int = 3600  # Command timeout in seconds

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.timeout_seconds < 60 or self.timeout_seconds > 172800:
            raise ValueError("timeout_seconds must be between 60 and 172800")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "targets": self.targets,
            "document_name": self.document_name,
            "parameters": self.parameters,
            "comment": self.comment,
            "timeout_seconds": self.timeout_seconds
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommandConfig":
        """Create instance from dictionary."""
        return cls(
            targets=data["targets"],
            document_name=data["document_name"],
            parameters=data.get("parameters"),
            comment=data.get("comment"),
            timeout_seconds=data.get("timeout_seconds", 3600)
        )


@dataclass
class CommandInvocation:
    """SSM Command invocation details."""

    command_id: str  # Command ID
    instance_id: str  # Target instance ID
    status: str  # Command status
    status_details: str  # Detailed status
    standard_output_content: str | None = None  # Command output
    standard_error_content: str | None = None  # Command error output

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "command_id": self.command_id,
            "instance_id": self.instance_id,
            "status": self.status,
            "status_details": self.status_details,
            "standard_output_content": self.standard_output_content,
            "standard_error_content": self.standard_error_content
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommandInvocation":
        """Create instance from dictionary."""
        return cls(
            command_id=data["command_id"],
            instance_id=data["instance_id"],
            status=data["status"],
            status_details=data["status_details"],
            standard_output_content=data.get("standard_output_content"),
            standard_error_content=data.get("standard_error_content")
        )


@dataclass
class AutomationExecutionConfig:
    """Configuration for SSM Automation execution."""

    document_name: str  # Automation document name
    parameters: dict[str, list[str]] | None = None  # Automation parameters
    target_parameter_name: str | None = None  # Parameter name for rate control
    targets: list[dict[str, list[str]]] | None = None  # Automation targets
    max_concurrency: str = "1"  # Max concurrent executions
    max_errors: str = "1"  # Max allowed errors

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "document_name": self.document_name,
            "parameters": self.parameters,
            "target_parameter_name": self.target_parameter_name,
            "targets": self.targets,
            "max_concurrency": self.max_concurrency,
            "max_errors": self.max_errors
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AutomationExecutionConfig":
        """Create instance from dictionary."""
        return cls(
            document_name=data["document_name"],
            parameters=data.get("parameters"),
            target_parameter_name=data.get("target_parameter_name"),
            targets=data.get("targets"),
            max_concurrency=data.get("max_concurrency", "1"),
            max_errors=data.get("max_errors", "1")
        )


@dataclass
class AutomationExecution:
    """SSM Automation execution details."""

    automation_execution_id: str  # Execution ID
    document_name: str  # Document name
    status: str  # Execution status
    start_time: datetime  # Start time
    end_time: datetime | None = None  # End time
    outputs: dict | None = None  # Execution outputs
    failure_message: str | None = None  # Failure message

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "automation_execution_id": self.automation_execution_id,
            "document_name": self.document_name,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "outputs": self.outputs,
            "failure_message": self.failure_message
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AutomationExecution":
        """Create instance from dictionary."""
        return cls(
            automation_execution_id=data["automation_execution_id"],
            document_name=data["document_name"],
            status=data["status"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(
                data["end_time"]) if data.get("end_time") else None,
            outputs=data.get("outputs"),
            failure_message=data.get("failure_message")
        )


@dataclass
class SessionConfig:
    """Configuration for Session Manager."""

    target: str  # Target instance ID
    document_name: str = "AWS-StartInteractiveCommand"  # Session document name
    parameters: dict[str, list[str]] | None = None  # Session parameters
    reason: str | None = None  # Session start reason


@dataclass
class SessionDetails:
    """Session Manager session details."""

    session_id: str  # Session ID
    target: str  # Target instance ID
    status: str  # Session status
    reason: str | None = None  # Session reason
    start_date: datetime  # Session start time
    end_date: datetime | None = None  # Session end time


@dataclass
class PatchBaselineConfig:
    """Configuration for Patch baseline."""

    name: str  # Baseline name
    operating_system: str  # OS type
    approval_rules: dict  # Patch approval rules
    description: str | None = None  # Baseline description
    tags: dict[str, str] | None = None  # Resource tags


@dataclass
class PatchSummary:
    """Patch operation summary."""

    instance_id: str  # Instance ID
    patch_group: str  # Patch group
    baseline_id: str  # Patch baseline ID
    status: str  # Patching status
    operation_type: str  # Patch operation type
    critical_missing: int = 0  # Critical patches missing
    security_missing: int = 0  # Security patches missing
    installed_count: int = 0  # Installed patches count
    installed_rejected: int = 0  # Rejected patches count


@dataclass
class StateConfig:
    """Configuration for State Manager association."""

    name: str  # Association name
    document_name: str  # SSM document name
    targets: list[dict[str, list[str]]]  # Association targets
    schedule_expression: str  # Schedule expression
    parameters: dict[str, list[str]] | None = None  # Association parameters
    # Target parameter for automation
    automation_target_parameter_name: str | None = None


@dataclass
class StateAssociation:
    """State Manager association details."""

    association_id: str  # Association ID
    name: str  # Association name
    document_name: str  # SSM document name
    targets: list[dict[str, list[str]]]  # Association targets
    schedule_expression: str  # Schedule expression
    parameters: dict[str, list[str]] | None = None  # Association parameters
    # Target parameter for automation
    automation_target_parameter_name: str | None = None
    status: str | None = None  # Association status
    last_execution_date: datetime | None = None  # Last execution date
    next_execution_date: datetime | None = None  # Next execution date

    def __post_init__(self) -> None:
        """Validate association details after initialization."""
        if not self.association_id:
            raise ValueError("association_id is required")
        if not self.name:
            raise ValueError("name is required")
        if not self.document_name:
            raise ValueError("document_name is required")
        if not self.targets:
            raise ValueError("targets is required")
        if not self.schedule_expression:
            raise ValueError("schedule_expression is required")


@dataclass
class InventoryConfig:
    """Configuration for Inventory collection."""

    instance_id: str  # Instance ID
    type_name: str  # Inventory type
    schema_version: str  # Schema version
    capture_time: str  # Data capture time
    content: dict  # Inventory content

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "instance_id": self.instance_id,
            "type_name": self.type_name,
            "schema_version": self.schema_version,
            "capture_time": self.capture_time,
            "content": self.content
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InventoryConfig":
        """Create instance from dictionary."""
        return cls(
            instance_id=data["instance_id"],
            type_name=data["type_name"],
            schema_version=data["schema_version"],
            capture_time=data["capture_time"],
            content=data["content"]
        )


@dataclass
class MaintenanceWindowConfig:
    """Configuration for Maintenance Window."""

    name: str  # Window name
    schedule: str  # CRON/Rate expression
    duration: int  # Window duration in hours
    cutoff: int  # Cutoff time in hours
    allow_unregistered_targets: bool = False  # Allow unregistered targets
    tags: dict[str, str] | None = None  # Resource tags

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "name": self.name,
            "schedule": self.schedule,
            "duration": self.duration,
            "cutoff": self.cutoff,
            "allow_unregistered_targets": self.allow_unregistered_targets
        }
        if self.tags is not None:
            result["tags"] = self.tags
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MaintenanceWindowConfig":
        """Create instance from dictionary."""
        return cls(
            name=data["name"],
            schedule=data["schedule"],
            duration=data["duration"],
            cutoff=data["cutoff"],
            allow_unregistered_targets=data.get(
                "allow_unregistered_targets", False),
            tags=data.get("tags")
        )


@dataclass
class MaintenanceWindow:
    """Maintenance Window details."""

    window_id: str  # Window ID
    name: str  # Window name
    status: str  # Window status
    enabled: bool  # Window enabled state
    schedule: str  # Schedule expression
    duration: int  # Duration in hours
    cutoff: int  # Cutoff in hours
    next_execution_time: str | None = None  # Next scheduled execution

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "window_id": self.window_id,
            "name": self.name,
            "status": self.status,
            "enabled": self.enabled,
            "schedule": self.schedule,
            "duration": self.duration,
            "cutoff": self.cutoff
        }
        if self.next_execution_time is not None:
            result["next_execution_time"] = self.next_execution_time
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MaintenanceWindow":
        """Create instance from dictionary."""
        return cls(
            window_id=data["window_id"],
            name=data["name"],
            status=data["status"],
            enabled=data["enabled"],
            schedule=data["schedule"],
            duration=data["duration"],
            cutoff=data["cutoff"],
            next_execution_time=data.get("next_execution_time")
        )


@dataclass
class MaintenanceTask:
    """Maintenance Window task."""

    window_id: str  # Window ID
    task_id: str  # Task ID
    task_type: str  # Task type
    targets: list[dict]  # Task targets
    task_arn: str  # Task ARN
    service_role_arn: str  # Service role ARN
    status: str  # Task status
    priority: int  # Task priority
    max_concurrency: str  # Max concurrent executions
    max_errors: str  # Max allowed errors

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "window_id": self.window_id,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "targets": self.targets,
            "task_arn": self.task_arn,
            "service_role_arn": self.service_role_arn,
            "status": self.status,
            "priority": self.priority,
            "max_concurrency": self.max_concurrency,
            "max_errors": self.max_errors
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MaintenanceTask":
        """Create instance from dictionary."""
        return cls(
            window_id=data["window_id"],
            task_id=data["task_id"],
            task_type=data["task_type"],
            targets=data["targets"],
            task_arn=data["task_arn"],
            service_role_arn=data["service_role_arn"],
            status=data["status"],
            priority=data["priority"],
            max_concurrency=data["max_concurrency"],
            max_errors=data["max_errors"]
        )
