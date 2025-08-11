"""AWS Kinesis Firehose client module."""

from chainsaws.aws.firehose.firehose import FirehoseAPI
from chainsaws.aws.firehose.firehose_models import (
    DeliveryStreamRequest,
    FirehoseAPIConfig,
    S3DestinationConfig,
)

__all__ = [
    "DeliveryStreamRequest",
    "FirehoseAPI",
    "FirehoseAPIConfig",
    "S3DestinationConfig",
]
