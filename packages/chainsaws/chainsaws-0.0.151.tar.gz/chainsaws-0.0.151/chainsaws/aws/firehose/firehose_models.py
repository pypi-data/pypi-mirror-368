from dataclasses import dataclass
from typing_extensions import TypedDict, NotRequired

from chainsaws.aws.shared.config import APIConfig


@dataclass
class FirehoseAPIConfig(APIConfig):
    """Kinesis Firehose configuration."""
    pass


class S3DestinationConfig(TypedDict):
    """S3 destination configuration (for Firehose S3 destination)."""

    role_arn: str  # IAM role ARN for Firehose
    bucket_name: str  # S3 bucket name
    prefix: str  # Object key prefix within bucket
    error_prefix: NotRequired[str]  # Error output prefix (default "error")


class DeliveryStreamRequest(TypedDict):
    """Delivery stream creation request."""

    name: str  # Stream name
    s3_config: S3DestinationConfig  # S3 destination configuration
    tags: NotRequired[dict[str, str]]  # Optional resource tags
