from typing import TypedDict, Optional, List, Dict, Any


class Filter(TypedDict, total=False):
    """Notification filter configuration."""
    Key: Optional[Dict[str, Any]]


class LambdaFunctionConfiguration(TypedDict, total=False):
    """Lambda function notification configuration."""
    Id: Optional[str]
    LambdaFunctionArn: str
    Events: List[str]
    Filter: Optional[Filter]


class TopicConfiguration(TypedDict, total=False):
    """SNS topic notification configuration."""
    Id: Optional[str]
    TopicArn: str
    Events: List[str]
    Filter: Optional[Filter]


class QueueConfiguration(TypedDict, total=False):
    """SQS queue notification configuration."""
    Id: Optional[str]
    QueueArn: str
    Events: List[str]
    Filter: Optional[Filter]


class EventBridgeConfiguration(TypedDict, total=False):
    """EventBridge notification configuration."""
    pass


class GetBucketNotificationResponse(TypedDict, total=False):
    """Response from S3 GetBucketNotificationConfiguration operation."""
    TopicConfigurations: Optional[List[TopicConfiguration]]
    QueueConfigurations: Optional[List[QueueConfiguration]]
    LambdaFunctionConfigurations: Optional[List[LambdaFunctionConfiguration]]
    EventBridgeConfiguration: Optional[EventBridgeConfiguration] 