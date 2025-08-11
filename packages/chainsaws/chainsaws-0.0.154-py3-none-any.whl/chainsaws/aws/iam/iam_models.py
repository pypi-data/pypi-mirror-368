from typing import Any, Literal
from dataclasses import dataclass, field

from chainsaws.aws.shared.config import APIConfig


@dataclass
class IAMAPIConfig(APIConfig):
    """IAM API configuration."""

    max_retries: int = 3  # Maximum number of API call retries
    timeout: int = 30  # Timeout for API calls in seconds


@dataclass
class RoleConfig:
    """Configuration for creating/modifying an IAM role."""

    name: str  # Role name
    trust_policy: dict[str, Any]  # Trust policy document
    description: str | None = None  # Role description
    path: str = "/"  # Role path
    max_session_duration: int = 3600  # Maximum session duration in seconds
    permissions_boundary: str | None = None  # Permissions boundary policy ARN
    tags: dict[str, str] = field(default_factory=dict)  # Role tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.name:
            raise ValueError("name is required")
        if not self.trust_policy:
            raise ValueError("trust_policy is required")
        if not 3600 <= self.max_session_duration <= 43200:
            raise ValueError(
                "max_session_duration must be between 3600 and 43200 seconds")


@dataclass
class RolePolicyConfig:
    """Configuration for attaching policies to an IAM role."""

    role_name: str  # Role name
    policy_arn: str  # Policy ARN to attach
    policy_name: str | None = None  # Name for inline policy
    policy_document: dict[str, Any] | None = None  # Inline policy document

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.role_name:
            raise ValueError("role_name is required")
        if not self.policy_arn and not (self.policy_name and self.policy_document):
            raise ValueError(
                "Either policy_arn or both policy_name and policy_document are required")


@dataclass
class PolicyConfig:
    """Configuration for creating/modifying an IAM policy."""

    name: str  # Policy name
    document: dict[str, Any]  # Policy document
    description: str | None = None  # Policy description
    path: str = "/"  # Policy path
    tags: dict[str, str] = field(default_factory=dict)  # Policy tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.name:
            raise ValueError("name is required")
        if not self.document:
            raise ValueError("document is required")


@dataclass
class UserConfig:
    """Configuration for creating/modifying an IAM user."""

    name: str  # User name
    path: str = "/"  # User path
    permissions_boundary: str | None = None  # Permissions boundary policy ARN
    tags: dict[str, str] = field(default_factory=dict)  # User tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.name:
            raise ValueError("name is required")


@dataclass
class GroupConfig:
    """Configuration for creating/modifying an IAM group."""

    name: str  # Group name
    path: str = "/"  # Group path
    tags: dict[str, str] = field(default_factory=dict)  # Group tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.name:
            raise ValueError("name is required")


@dataclass
class AccessKeyConfig:
    """Configuration for creating/modifying an IAM access key."""

    user_name: str  # User name
    status: Literal["Active", "Inactive"] = "Active"  # Access key status

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.user_name:
            raise ValueError("user_name is required")


@dataclass
class InstanceProfileConfig:
    """Configuration for creating/modifying an IAM instance profile."""

    name: str  # Instance profile name
    path: str = "/"  # Instance profile path
    role_name: str | None = None  # Role to attach to the instance profile
    tags: dict[str, str] = field(default_factory=dict)  # Instance profile tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.name:
            raise ValueError("name is required")
