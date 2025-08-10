"""Type definitions for AWS EC2 operations."""

from typing import Literal, TypedDict, List, Optional, Dict, Any
from typing_extensions import NotRequired

# Instance types
InstanceType = Literal[
    "t2.nano", "t2.micro", "t2.small", "t2.medium", "t2.large",
    "t3.nano", "t3.micro", "t3.small", "t3.medium", "t3.large",
    "m5.large", "m5.xlarge", "m5.2xlarge",
    "c5.large", "c5.xlarge", "c5.2xlarge",
    "r5.large", "r5.xlarge", "r5.2xlarge"
]

# Instance states
InstanceState = Literal[
    "pending", "running", "stopping", "stopped", "shutting-down", "terminated"
]

# Volume types
VolumeType = Literal["gp2", "gp3", "io1", "io2", "st1", "sc1", "standard"]

# Volume states
VolumeState = Literal["creating", "available", "in-use", "deleting", "deleted", "error"]

# Image states
ImageState = Literal["pending", "available", "invalid", "deregistered", "transient", "failed", "error"]

# Snapshot states
SnapshotState = Literal["pending", "completed", "error"]

# Security group rule types
SecurityGroupRuleType = TypedDict('SecurityGroupRuleType', {
    'IpProtocol': str,
    'FromPort': NotRequired[int],
    'ToPort': NotRequired[int],
    'IpRanges': NotRequired[List[Dict[str, str]]],
    'UserIdGroupPairs': NotRequired[List[Dict[str, str]]],
    'PrefixListIds': NotRequired[List[Dict[str, str]]],
})

# Metric alarm configuration
MetricAlarmConfig = TypedDict('MetricAlarmConfig', {
    'MetricName': str,
    'Threshold': float,
    'ComparisonOperator': str,
    'Period': int,
    'EvaluationPeriods': int,
    'Statistic': str,
    'ActionsEnabled': NotRequired[bool],
    'AlarmActions': NotRequired[List[str]],
})

# Resource types for tagging
ResourceType = Literal[
    "instance", "volume", "snapshot", "security-group", "network-interface", "image"
]

# Architecture types
ArchitectureType = Literal["x86_64", "arm64"]

# Common filter type
FilterType = TypedDict('FilterType', {
    'Name': str,
    'Values': List[str],
})

# Health status type
HealthStatusType = TypedDict('HealthStatusType', {
    'Status': str,
    'Details': List[Dict[str, str]],
    'SystemStatus': Dict[str, str],
    'InstanceStatus': Dict[str, str],
})

# Cost estimate type
CostEstimateType = TypedDict('CostEstimateType', {
    'InstanceType': str,
    'Region': str,
    'HourlyCost': float,
    'MonthlyCost': float,
    'Currency': str,
})

# Backup configuration
BackupConfigType = TypedDict('BackupConfigType', {
    'Schedule': str,
    'RetentionDays': int,
    'Tags': NotRequired[Dict[str, str]],
})

# Operation schedule
OperationScheduleType = TypedDict('OperationScheduleType', {
    'StartSchedule': str,
    'StopSchedule': str,
    'TimeZone': NotRequired[str],
})

class AutomationScheduleType(TypedDict):
    """Instance automation schedule configuration."""
    start_time: str  # Cron expression
    stop_time: str   # Cron expression
    timezone: str
    notification_arn: Optional[str]
    enabled: bool

class BackupPolicyType(TypedDict):
    """Backup policy configuration."""
    frequency: Literal["daily", "weekly", "monthly"]
    retention_days: int
    backup_window: str
    tags: Optional[List[Dict[str, str]]]
    cross_region_copy: Optional[Dict[str, Any]]

class SecurityPolicyType(TypedDict):
    """Security policy configuration."""
    name: str
    rules: List[Dict[str, Any]]
    compliance: Optional[List[str]]
    auto_remediation: bool 