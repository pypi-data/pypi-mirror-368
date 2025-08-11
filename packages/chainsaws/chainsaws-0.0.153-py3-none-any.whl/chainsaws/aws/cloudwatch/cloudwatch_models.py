from datetime import datetime
from enum import Enum
from typing import Any
from dataclasses import dataclass, field

from chainsaws.aws.shared.config import APIConfig


class LogLevel(str, Enum):
    """Log levels for CloudWatch Logs."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RetentionDays(int, Enum):
    """Available retention periods for log groups."""

    ONE_DAY = 1
    THREE_DAYS = 3
    FIVE_DAYS = 5
    ONE_WEEK = 7
    TWO_WEEKS = 14
    ONE_MONTH = 30
    TWO_MONTHS = 60
    THREE_MONTHS = 90
    FOUR_MONTHS = 120
    FIVE_MONTHS = 150
    SIX_MONTHS = 180
    ONE_YEAR = 365
    FOREVER = 0


@dataclass
class CloudWatchAPIConfig(APIConfig):
    """Configuration for CloudWatch Logs API."""

    default_region: str = "ap-northeast-2"  # Default AWS region
    max_retries: int = 3  # Maximum number of API retry attempts


@dataclass
class LogGroupConfig:
    """Configuration for log group creation."""

    log_group_name: str  # Log group name
    retention_days: RetentionDays | None = None  # Log retention period in days
    kms_key_id: str | None = None  # KMS key ID for encryption
    tags: dict[str, str] = field(
        default_factory=dict)  # Tags for the log group


@dataclass
class LogStreamConfig:
    """Configuration for log stream creation."""

    log_group_name: str  # Log group name
    log_stream_name: str  # Log stream name


@dataclass
class LogEvent:
    """Single log event."""

    message: str  # Log message
    timestamp: int  # Event timestamp (milliseconds since epoch)
    level: LogLevel = LogLevel.INFO  # Log level


@dataclass
class LogBatch:
    """Batch of log events."""

    log_group_name: str  # Log group name
    log_stream_name: str  # Log stream name
    events: list[LogEvent]  # Log events
    sequence_token: str | None = None  # Sequence token for ordered delivery


@dataclass
class LogFilter:
    """Filter for log events."""

    log_group_name: str  # Log group name
    filter_pattern: str  # Filter pattern
    start_time: datetime | None = None  # Start time for filtering
    end_time: datetime | None = None  # End time for filtering
    log_stream_names: list[str] | None = field(
        default_factory=list)  # Log stream names to filter
    limit: int | None = None  # Maximum number of events to return


@dataclass
class MetricFilter:
    """Metric filter configuration."""

    filter_name: str  # Filter name
    filter_pattern: str  # Filter pattern
    metric_transformations: list[dict[str, Any]]  # Metric transformations
    log_group_name: str  # Log group name


@dataclass
class SubscriptionFilter:
    """Subscription filter configuration."""

    filter_name: str  # Filter name
    filter_pattern: str  # Filter pattern
    destination_arn: str  # Destination ARN (Lambda, Kinesis, etc.)
    log_group_name: str  # Log group name
    role_arn: str | None = None  # IAM role ARN for delivery


@dataclass
class MetricDataQuery:
    """Query configuration for metric data."""

    metric_name: str  # Metric name
    namespace: str  # Metric namespace
    dimensions: dict[str, str]  # Metric dimensions
    period: int  # Period in seconds
    stat: str  # Statistic (e.g., Average, Sum)
    unit: str | None = None  # Unit of measure
    return_data: bool = True  # Whether to return data


@dataclass
class MetricAlarm:
    """Alarm configuration for metrics."""

    alarm_name: str  # Alarm name
    metric_name: str  # Metric name
    namespace: str  # Metric namespace
    comparison_operator: str  # Comparison operator
    evaluation_periods: int  # Number of periods to evaluate
    period: int  # Period in seconds
    threshold: float  # Threshold value
    statistic: str  # Statistic to apply
    dimensions: dict[str, str] = field(
        default_factory=dict)  # Metric dimensions
    actions_enabled: bool = True  # Whether actions are enabled
    alarm_actions: list[str] = field(
        default_factory=list)  # Actions to take when alarm triggers
    ok_actions: list[str] = field(
        default_factory=list)  # Actions to take when alarm returns to OK
    insufficient_data_actions: list[str] = field(
        default_factory=list)  # Actions to take when data is insufficient
