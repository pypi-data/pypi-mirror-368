"""High-level AWS SNS client implementation.

This module provides a user-friendly interface for working with AWS SNS.
It wraps the low-level boto3 client and provides additional functionality
like automatic pagination and model validation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Union


from chainsaws.aws.shared import session
from chainsaws.aws.sns._sns_internal import SNS
from chainsaws.aws.sns.sns_models import (
    SNSAPIConfig,
    SNSMessage,
    SNSSubscription,
    SNSTopic,
    BatchPublishResult,
    BatchSubscribeResult,
)

logger = logging.getLogger(__name__)


class SNSAPI:
    """High-level SNS client for managing topics and publishing messages.

    This class provides a simplified interface for working with AWS SNS,
    with support ford automatic pagination.

    Args:
        credentials: Optional AWS credentials.
        region_name: Optional AWS region name.
        boto3_session: Optional pre-configured boto3 session.
    """

    def __init__(
        self,
        config: Optional[SNSAPIConfig] = None,
    ) -> None:
        """Initialize the SNS client."""
        self.config = config or SNSAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.sns = SNS(
            boto3_session=self.boto3_session,
            region_name=self.config.region,
        )

    def create_topic(
        self,
        name: str,
        display_name: Optional[str] = None,
        policy: Optional[Dict] = None,
        delivery_policy: Optional[Dict] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> SNSTopic:
        """Create a new SNS topic.

        Args:
            name: Name of the topic.
            display_name: Optional display name for the topic.
            policy: Optional access policy for the topic.
            delivery_policy: Optional delivery policy for the topic.
            tags: Optional tags to attach to the topic.

        Returns:
            SNSTopic model representing the created topic.
        """
        attributes = {}
        if display_name:
            attributes["DisplayName"] = display_name
        if policy:
            attributes["Policy"] = str(policy)
        if delivery_policy:
            attributes["DeliveryPolicy"] = str(delivery_policy)

        topic_attrs = self.sns.create_topic(
            name=name,
            attributes=attributes,
            tags=tags,
        )

        return SNSTopic(
            topic_arn=topic_attrs["TopicArn"],
            topic_name=name,
            display_name=display_name,
            policy=policy,
            delivery_policy=delivery_policy,
            tags=tags,
            created_at=datetime.now(),
        )

    def delete_topic(self, topic_arn: str) -> None:
        """Delete an SNS topic.

        Args:
            topic_arn: ARN of the topic to delete.
        """
        self.sns.delete_topic(topic_arn)

    def publish(
        self,
        topic_arn: str,
        message: Union[str, SNSMessage],
    ) -> str:
        """Publish a message to an SNS topic.

        Args:
            topic_arn: ARN of the topic to publish to.
            message: Message to publish (string or SNSMessage model).

        Returns:
            Message ID of the published message.
        """
        if isinstance(message, str):
            message = SNSMessage(message=message)

        return self.sns.publish(
            topic_arn=topic_arn,
            message=message.message,
            subject=message.subject,
            message_attributes={
                k: v.to_dict() for k, v in (message.message_attributes or {}).items()
            } if message.message_attributes else None,
            message_structure=message.message_structure,
        )

    def subscribe(
        self,
        topic_arn: str,
        protocol: str,
        endpoint: str,
        raw_message_delivery: bool = False,
        filter_policy: Optional[Dict] = None,
    ) -> SNSSubscription:
        """Subscribe an endpoint to an SNS topic.

        Args:
            topic_arn: ARN of the topic to subscribe to.
            protocol: Protocol to use (http/https/email/sms/etc.).
            endpoint: Endpoint to subscribe.
            raw_message_delivery: Whether to enable raw message delivery.
            filter_policy: Optional message filtering policy.

        Returns:
            SNSSubscription model representing the subscription.
        """
        attributes = {}
        if raw_message_delivery:
            attributes["RawMessageDelivery"] = "true"
        if filter_policy:
            attributes["FilterPolicy"] = str(filter_policy)

        subscription_arn = self.sns.subscribe(
            topic_arn=topic_arn,
            protocol=protocol,
            endpoint=endpoint,
            attributes=attributes,
        )

        return SNSSubscription(
            subscription_arn=subscription_arn,
            topic_arn=topic_arn,
            protocol=protocol,
            endpoint=endpoint,
            raw_message_delivery=raw_message_delivery,
            filter_policy=filter_policy,
            created_at=datetime.now(),
        )

    def unsubscribe(self, subscription_arn: str) -> None:
        """Unsubscribe from an SNS topic.

        Args:
            subscription_arn: ARN of the subscription to remove.
        """
        self.sns.unsubscribe(subscription_arn)

    def list_topics(self) -> Generator[SNSTopic, None, None]:
        """List all SNS topics.

        Yields:
            SNSTopic models for each topic.
        """
        next_token = None
        while True:
            topics, next_token = self.sns.list_topics(next_token=next_token)
            for topic in topics:
                topic_arn = topic["TopicArn"]
                topic_name = topic_arn.split(":")[-1]
                yield SNSTopic(
                    topic_arn=topic_arn,
                    topic_name=topic_name,
                )

            if not next_token:
                break

    def list_subscriptions(
        self,
        topic_arn: str,
    ) -> Generator[SNSSubscription, None, None]:
        """List all subscriptions for a topic.

        Args:
            topic_arn: ARN of the topic to list subscriptions for.

        Yields:
            SNSSubscription models for each subscription.
        """
        next_token = None
        while True:
            subs, next_token = self.sns.list_subscriptions_by_topic(
                topic_arn=topic_arn,
                next_token=next_token,
            )
            for sub in subs:
                yield SNSSubscription(
                    subscription_arn=sub["SubscriptionArn"],
                    topic_arn=sub["TopicArn"],
                    protocol=sub["Protocol"],
                    endpoint=sub["Endpoint"],
                )

            if not next_token:
                break

    def batch_publish(
        self,
        topic_arn: str,
        messages: List[Union[str, SNSMessage]],
    ) -> BatchPublishResult:
        """Publish multiple messages to an SNS topic in parallel.

        Args:
            topic_arn: ARN of the topic to publish to.
            messages: List of messages (strings or SNSMessage models).

        Returns:
            BatchPublishResult containing successful and failed messages.

        Example:
            ```python
            messages = [
                "Simple message",
                SNSMessage(
                    message="Complex message",
                    subject="Test",
                    message_attributes={"priority": SNSMessageAttributes(string_value="high")}
                )
            ]
            result = sns.batch_publish(topic_arn, messages)
            print(f"Published {result.success_count} messages")
            for msg_id in result.successful:
                print(f"Successfully published: {msg_id}")
            for msg, error in result.failed:
                print(f"Failed to publish: {error}")
            ```
        """
        # Convert string messages to SNSMessage objects
        message_models = [
            msg if isinstance(msg, SNSMessage) else SNSMessage(message=msg)
            for msg in messages
        ]

        # Convert to dictionaries for internal API
        message_dicts = [
            {
                "message": msg.message,
                "subject": msg.subject,
                "message_attributes": {
                    k: v.to_dict()
                    for k, v in (msg.message_attributes or {}).items()
                } if msg.message_attributes else None,
                "message_structure": msg.message_structure,
            }
            for msg in message_models
        ]

        results = self.sns.batch_publish(
            topic_arn=topic_arn,
            messages=message_dicts,
        )

        return BatchPublishResult(results)

    def batch_subscribe(
        self,
        topic_arn: str,
        subscriptions: List[Dict[str, Any]],
    ) -> BatchSubscribeResult:
        """Subscribe multiple endpoints to an SNS topic in parallel.

        Args:
            topic_arn: ARN of the topic to subscribe to.
            subscriptions: List of subscription dictionaries containing:
                - protocol: Protocol to use (http/https/email/sms/etc.)
                - endpoint: Endpoint to subscribe
                - raw_message_delivery: Whether to enable raw message delivery
                - filter_policy: Optional message filtering policy

        Returns:
            BatchSubscribeResult containing successful and failed subscriptions.

        Example:
            ```python
            subscriptions = [
                {
                    "protocol": "email",
                    "endpoint": "user1@example.com"
                },
                {
                    "protocol": "https",
                    "endpoint": "https://example.com/webhook",
                    "raw_message_delivery": True,
                    "filter_policy": {"priority": ["high"]}
                }
            ]
            result = sns.batch_subscribe(topic_arn, subscriptions)
            print(f"Created {result.success_count} subscriptions")
            ```
        """
        # Convert subscription configs to internal format
        sub_configs = []
        for sub in subscriptions:
            attributes = {}
            if sub.get("raw_message_delivery"):
                attributes["RawMessageDelivery"] = "true"
            if sub.get("filter_policy"):
                attributes["FilterPolicy"] = str(sub["filter_policy"])

            sub_configs.append({
                "protocol": sub["protocol"],
                "endpoint": sub["endpoint"],
                "attributes": attributes if attributes else None,
            })

        results = self.sns.batch_subscribe(
            topic_arn=topic_arn,
            subscriptions=sub_configs,
        )

        return BatchSubscribeResult(results)

    def batch_unsubscribe(
        self,
        subscription_arns: List[str],
    ) -> BatchSubscribeResult:
        """Unsubscribe multiple subscriptions in parallel.

        Args:
            subscription_arns: List of subscription ARNs to unsubscribe.

        Returns:
            BatchSubscribeResult containing successful and failed unsubscriptions.

        Example:
            ```python
            arns = ["arn:aws:sns:...:1", "arn:aws:sns:...:2"]
            result = sns.batch_unsubscribe(arns)
            print(f"Removed {result.success_count} subscriptions")
            ```
        """
        results = self.sns.batch_unsubscribe(
            subscription_arns=subscription_arns,
        )

        return BatchSubscribeResult(results)
