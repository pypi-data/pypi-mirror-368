"""Models for AWS SNS service.

This module contains dataclass models representing various SNS entities and configurations.
These models provide type safety and validation for SNS operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, List, Tuple

from chainsaws.aws.shared.config import APIConfig


@dataclass
class SNSAPIConfig(APIConfig):
    """Configuration for the SNS API.

    Attributes:
        credentials: AWS credentials.
        region: AWS region.
    """
    pass


@dataclass
class SNSMessageAttributes:
    """Message attributes for SNS messages.

    Attributes:
        string_value: The String value of the message attribute.
        binary_value: The Binary value of the message attribute.
        data_type: The data type of the message attribute.
    """
    string_value: Optional[str] = None
    binary_value: Optional[bytes] = None
    data_type: str = "String"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = {}
        if self.string_value is not None:
            result["StringValue"] = self.string_value
        if self.binary_value is not None:
            result["BinaryValue"] = self.binary_value
        result["DataType"] = self.data_type
        return result


@dataclass
class SNSMessage:
    """Model representing an SNS message.

    Attributes:
        message: The message you want to send.
        subject: Optional subject for the message.
        message_attributes: Optional message attributes.
        message_structure: The structure of the message (json, string).
        message_deduplication_id: Token used for deduplication of sent messages.
        message_group_id: Tag that specifies that a message belongs to a specific group.
    """
    message: str
    subject: Optional[str] = None
    message_attributes: Optional[Dict[str, SNSMessageAttributes]] = None
    message_structure: Optional[str] = None
    message_deduplication_id: Optional[str] = None
    message_group_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = {
            "Message": self.message,
        }
        if self.subject:
            result["Subject"] = self.subject
        if self.message_attributes:
            result["MessageAttributes"] = {
                k: v.to_dict() for k, v in self.message_attributes.items()
            }
        if self.message_structure:
            result["MessageStructure"] = self.message_structure
        if self.message_deduplication_id:
            result["MessageDeduplicationId"] = self.message_deduplication_id
        if self.message_group_id:
            result["MessageGroupId"] = self.message_group_id
        return result


@dataclass
class SNSTopic:
    """Model representing an SNS topic.

    Attributes:
        topic_arn: The ARN of the topic.
        topic_name: The name of the topic.
        display_name: The display name of the topic.
        policy: The topic's access policy.
        delivery_policy: The topic's delivery policy.
        tags: Tags associated with the topic.
    """
    topic_arn: str
    topic_name: str
    display_name: Optional[str] = None
    policy: Optional[Dict[str, Any]] = None
    delivery_policy: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, str]] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = {
            "TopicArn": self.topic_arn,
            "TopicName": self.topic_name,
        }
        if self.display_name:
            result["DisplayName"] = self.display_name
        if self.policy:
            result["Policy"] = self.policy
        if self.delivery_policy:
            result["DeliveryPolicy"] = self.delivery_policy
        if self.tags:
            result["Tags"] = self.tags
        if self.created_at:
            result["CreatedAt"] = self.created_at.isoformat()
        return result


@dataclass
class SNSSubscription:
    """Model representing an SNS subscription.

    Attributes:
        subscription_arn: The ARN of the subscription.
        topic_arn: The ARN of the topic.
        protocol: The subscription's protocol (http, https, email, sms, etc.).
        endpoint: The subscription's endpoint.
        raw_message_delivery: Whether to enable raw message delivery.
        filter_policy: The filter policy for the subscription.
    """
    subscription_arn: str
    topic_arn: str
    protocol: str
    endpoint: str
    raw_message_delivery: bool = False
    filter_policy: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = {
            "SubscriptionArn": self.subscription_arn,
            "TopicArn": self.topic_arn,
            "Protocol": self.protocol,
            "Endpoint": self.endpoint,
            "RawMessageDelivery": str(self.raw_message_delivery).lower(),
        }
        if self.filter_policy:
            result["FilterPolicy"] = self.filter_policy
        if self.created_at:
            result["CreatedAt"] = self.created_at.isoformat()
        return result


@dataclass
class BatchPublishResult:
    """Result of a batch publish operation.

    Attributes:
        successful: List of successfully published message IDs.
        failed: List of failed messages with their error messages.
    """
    successful: List[str] = field(default_factory=list)
    failed: List[Tuple[SNSMessage, str]] = field(default_factory=list)

    def __init__(self, results: List[Tuple[bool, str, Optional[str]]]) -> None:
        self.successful = []
        self.failed = []

        for success, message_id, error in results:
            if success:
                self.successful.append(message_id)
            else:
                self.failed.append((message_id, error or "Unknown error"))

    @property
    def success_count(self) -> int:
        """Number of successfully published messages."""
        return len(self.successful)

    @property
    def failure_count(self) -> int:
        """Number of failed messages."""
        return len(self.failed)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return {
            "Successful": self.successful,
            "Failed": [(msg.to_dict(), err) for msg, err in self.failed],
            "SuccessCount": self.success_count,
            "FailureCount": self.failure_count,
        }


@dataclass
class BatchSubscribeResult:
    """Result of a batch subscribe operation.

    Attributes:
        successful: List of successful subscription ARNs.
        failed: List of failed subscriptions with their error messages.
    """
    successful: List[str] = field(default_factory=list)
    failed: List[Tuple[Dict[str, Any], str]] = field(default_factory=list)

    def __init__(self, results: List[Tuple[bool, str, Optional[str]]]) -> None:
        self.successful = []
        self.failed = []

        for success, sub_arn, error in results:
            if success:
                self.successful.append(sub_arn)
            else:
                self.failed.append((sub_arn, error or "Unknown error"))

    @property
    def success_count(self) -> int:
        """Number of successful subscriptions."""
        return len(self.successful)

    @property
    def failure_count(self) -> int:
        """Number of failed subscriptions."""
        return len(self.failed)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return {
            "Successful": self.successful,
            "Failed": self.failed,
            "SuccessCount": self.success_count,
            "FailureCount": self.failure_count,
        }
