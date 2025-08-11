"""Functions for common AWS services usage, such as boto3 Session management."""
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

import boto3


@dataclass
class AWSCredentials:
    """AWS credentials configuration."""

    aws_access_key_id: Optional[str] = None  # AWS access key ID
    aws_secret_access_key: Optional[str] = None  # AWS secret access key
    region_name: Optional[str] = field(
        default="ap-northeast-2")  # AWS region name
    profile_name: Optional[str] = None  # AWS profile name

    def to_dict(self, exclude_none: bool = False) -> dict[str, Any]:
        """Convert the model to a dictionary.

        Args:
            exclude_none (bool): Whether to exclude None values from the output

        Returns:
            dict[str, Any]: The model as a dictionary
        """
        result = asdict(self)
        if exclude_none:
            return {k: v for k, v in result.items() if v is not None}
        return result


def get_boto_session(credentials: Optional[AWSCredentials] = None) -> boto3.Session:
    """Returns a boto3 session. This function is wrapped to allow for future customization.

    Args:
        credentials (Optional[AWSCredentials]): Validated AWS credentials

    Returns:
        boto3.Session: Configured AWS session

    Warning:
        Using hardcoded credentials is not recommended for security reasons.
        Please use AWS IAM environment profiles instead.

    """
    if credentials:
        return boto3.Session(**credentials.to_dict(exclude_none=True))

    return boto3.Session()
