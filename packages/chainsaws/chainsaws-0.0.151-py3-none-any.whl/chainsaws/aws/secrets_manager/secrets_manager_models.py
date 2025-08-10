from datetime import datetime
from typing import Any, Optional, TypedDict
from dataclasses import dataclass, field

from chainsaws.aws.shared.config import APIConfig


@dataclass
class SecretsManagerAPIConfig(APIConfig):
    """Secrets Manager configuration."""

    max_retries: int = 3  # Maximum number of API call retries
    timeout: int = 30  # Timeout for API calls in seconds
    retry_modes: dict[str, Any] = field(
        default_factory=lambda: {
            "max_attempts": 3,
            "mode": "adaptive",
        }
    )  # Retry configuration


@dataclass
class SecretConfig:
    """Secret configuration."""

    name: str  # Secret name
    description: Optional[str] = None  # Secret description
    secret_string: Optional[str] = None  # Secret string value
    secret_binary: Optional[bytes] = None  # Secret binary value
    tags: Optional[dict[str, str]] = None  # Secret tags

    def __post_init__(self) -> None:
        """Validate secret name."""
        secret_name_length_limit = 512
        if not self.name or len(self.name) > secret_name_length_limit:
            msg = f"Secret name must be between 1 and {
                secret_name_length_limit} characters"
            raise ValueError(msg)


@dataclass
class RotationConfig:
    """Secret rotation configuration."""

    rotation_lambda_arn: str  # Lambda ARN for rotation
    rotation_rules: dict[str, Any]  # Rotation rules including schedule
    # Days after which to rotate automatically
    automatically_after_days: Optional[int] = None


@dataclass
class BatchSecretOperation:
    """Batch operation configuration."""

    secret_ids: list[str]  # List of secret IDs
    operation: str  # Operation to perform
    params: dict[str, Any] = field(
        default_factory=dict)  # Operation parameters


@dataclass
class SecretBackupConfig:
    """Secret backup configuration."""

    secret_ids: list[str]  # Secrets to backup
    backup_path: str  # Backup file path


@dataclass
class SecretFilterConfig:
    """Secret filtering configuration."""

    name_prefix: Optional[str] = None  # Filter by name prefix
    tags: Optional[dict[str, str]] = None  # Filter by tags
    created_after: Optional[datetime] = None  # Filter by creation date
    last_updated_after: Optional[datetime] = None  # Filter by update date


class GetSecretResponse(TypedDict):
    """Response from creating a secret."""

    ARN: str
    Name: str
    VersionId: str
    SecretBinary: Optional[bytes]  # Exclusive OR
    SecretString: Optional[str]  # Exclusive OR
    VersionStages: list[str]
    CreatedDate: float  # unix timestamp
