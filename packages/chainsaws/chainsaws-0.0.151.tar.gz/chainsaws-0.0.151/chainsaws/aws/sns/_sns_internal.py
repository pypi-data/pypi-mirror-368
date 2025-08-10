"""Internal implementation of AWS SNS client.

This module contains the low-level implementation of SNS operations.
It handles direct interactions with boto3 and implements retry logic and error handling.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

import boto3
from botocore.exceptions import ClientError

from chainsaws.aws.sns.sns_exception import SNSException


logger = logging.getLogger(__name__)


class SNS:
    """Internal SNS client implementation.

    This class provides low-level access to SNS operations through boto3.
    It handles AWS credentials and implements basic error handling.

    Args:
        boto3_session: Boto3 session to use for AWS operations.
        region_name: AWS region name.
    """

    def __init__(
        self,
        boto3_session: Optional[boto3.Session] = None,
        region_name: Optional[str] = None,
    ) -> None:
        """Initialize the SNS client."""
        self.session = boto3_session or boto3.Session()
        self.client = self.session.client("sns", region_name=region_name)

    def create_topic(
        self,
        name: str,
        attributes: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create an SNS topic.

        Args:
            name: Name of the topic.
            attributes: Topic attributes.
            tags: Tags to attach to the topic.

        Returns:
            Dict containing the topic ARN and attributes.

        Raises:
            SNSException: If topic creation fails.
        """
        try:
            kwargs: Dict[str, Any] = {"Name": name}
            if attributes:
                kwargs["Attributes"] = attributes
            if tags:
                kwargs["Tags"] = [{"Key": k, "Value": v}
                                  for k, v in tags.items()]

            response = self.client.create_topic(**kwargs)
            topic_arn = response["TopicArn"]

            # Get topic attributes
            attrs = self.client.get_topic_attributes(TopicArn=topic_arn)
            return attrs["Attributes"]

        except ClientError as e:
            logger.exception("Failed to create SNS topic: %s", name)
            raise SNSException(f"Failed to create SNS topic: {str(e)}") from e

    def delete_topic(self, topic_arn: str) -> None:
        """Delete an SNS topic.

        Args:
            topic_arn: ARN of the topic to delete.

        Raises:
            SNSException: If topic deletion fails.
        """
        try:
            self.client.delete_topic(TopicArn=topic_arn)
        except ClientError as e:
            logger.exception("Failed to delete SNS topic: %s", topic_arn)
            raise SNSException(f"Failed to delete SNS topic: {str(e)}") from e

    def publish(
        self,
        topic_arn: str,
        message: str,
        subject: Optional[str] = None,
        message_attributes: Optional[Dict[str, Dict[str, Any]]] = None,
        message_structure: Optional[str] = None,
    ) -> str:
        """Publish a message to an SNS topic.

        Args:
            topic_arn: ARN of the topic to publish to.
            message: Message to publish.
            subject: Optional message subject.
            message_attributes: Optional message attributes.
            message_structure: Optional message structure (json/string).

        Returns:
            Message ID of the published message.

        Raises:
            SNSException: If message publication fails.
        """
        try:
            kwargs: Dict[str, Any] = {
                "TopicArn": topic_arn,
                "Message": message,
            }
            if subject:
                kwargs["Subject"] = subject
            if message_attributes:
                kwargs["MessageAttributes"] = message_attributes
            if message_structure:
                kwargs["MessageStructure"] = message_structure

            response = self.client.publish(**kwargs)
            return response["MessageId"]

        except ClientError as e:
            logger.exception(
                "Failed to publish message to SNS topic: %s", topic_arn)
            raise SNSException(f"Failed to publish message: {str(e)}") from e

    def subscribe(
        self,
        topic_arn: str,
        protocol: str,
        endpoint: str,
        attributes: Optional[Dict[str, str]] = None,
    ) -> str:
        """Subscribe an endpoint to an SNS topic.

        Args:
            topic_arn: ARN of the topic to subscribe to.
            protocol: Protocol to use (http/https/email/sms/etc.).
            endpoint: Endpoint to subscribe.
            attributes: Optional subscription attributes.

        Returns:
            ARN of the subscription.

        Raises:
            SNSException: If subscription fails.
        """
        try:
            kwargs: Dict[str, Any] = {
                "TopicArn": topic_arn,
                "Protocol": protocol,
                "Endpoint": endpoint,
            }
            if attributes:
                kwargs["Attributes"] = attributes

            response = self.client.subscribe(**kwargs)
            return response["SubscriptionArn"]

        except ClientError as e:
            logger.exception(
                "Failed to subscribe %s to SNS topic: %s",
                endpoint,
                topic_arn,
            )
            raise SNSException(
                f"Failed to create subscription: {str(e)}") from e

    def unsubscribe(self, subscription_arn: str) -> None:
        """Unsubscribe from an SNS topic.

        Args:
            subscription_arn: ARN of the subscription to remove.

        Raises:
            SNSException: If unsubscribe operation fails.
        """
        try:
            self.client.unsubscribe(SubscriptionArn=subscription_arn)
        except ClientError as e:
            logger.exception(
                "Failed to unsubscribe from subscription: %s",
                subscription_arn,
            )
            raise SNSException(f"Failed to unsubscribe: {str(e)}") from e

    def list_topics(self, next_token: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """List SNS topics.

        Args:
            next_token: Token for pagination.

        Returns:
            Tuple of (list of topics, next token for pagination).

        Raises:
            SNSException: If listing topics fails.
        """
        try:
            kwargs: Dict[str, Any] = {}
            if next_token:
                kwargs["NextToken"] = next_token

            response = self.client.list_topics(**kwargs)
            topics = response["Topics"]
            next_token = response.get("NextToken")

            return topics, next_token

        except ClientError as e:
            logger.exception("Failed to list SNS topics")
            raise SNSException(f"Failed to list topics: {str(e)}") from e

    def list_subscriptions_by_topic(
        self,
        topic_arn: str,
        next_token: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """List subscriptions for a specific topic.

        Args:
            topic_arn: ARN of the topic.
            next_token: Token for pagination.

        Returns:
            Tuple of (list of subscriptions, next token for pagination).

        Raises:
            SNSException: If listing subscriptions fails.
        """
        try:
            kwargs: Dict[str, Any] = {"TopicArn": topic_arn}
            if next_token:
                kwargs["NextToken"] = next_token

            response = self.client.list_subscriptions_by_topic(**kwargs)
            subscriptions = response["Subscriptions"]
            next_token = response.get("NextToken")

            return subscriptions, next_token

        except ClientError as e:
            logger.exception(
                "Failed to list subscriptions for topic: %s",
                topic_arn,
            )
            raise SNSException(
                f"Failed to list subscriptions: {str(e)}") from e

    def batch_publish(
        self,
        topic_arn: str,
        messages: List[Dict[str, Any]],
    ) -> List[Tuple[bool, str, Optional[str]]]:
        """Publish multiple messages to an SNS topic in parallel.

        Args:
            topic_arn: ARN of the topic to publish to.
            messages: List of message dictionaries containing message parameters.

        Returns:
            List of tuples containing (success, message_id, error_message).
            For each message:
                - success: True if published successfully, False otherwise
                - message_id: Message ID if successful, empty string if failed
                - error_message: Error message if failed, None if successful
        """
        results: List[Tuple[bool, str, Optional[str]]] = []

        def publish_single(message: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
            try:
                message_id = self.publish(
                    topic_arn=topic_arn,
                    message=message["message"],
                    subject=message.get("subject"),
                    message_attributes=message.get("message_attributes"),
                    message_structure=message.get("message_structure"),
                )
                return True, message_id, None
            except Exception as e:
                logger.exception(
                    "Failed to publish message to SNS topic: %s",
                    topic_arn,
                )
                return False, "", str(e)

        with ThreadPoolExecutor() as executor:
            results.extend(executor.map(publish_single, messages))

        return results

    def batch_subscribe(
        self,
        topic_arn: str,
        subscriptions: List[Dict[str, Any]],
    ) -> List[Tuple[bool, str, Optional[str]]]:
        """Subscribe multiple endpoints to an SNS topic in parallel.

        Args:
            topic_arn: ARN of the topic to subscribe to.
            subscriptions: List of subscription dictionaries containing:
                - protocol: Protocol to use (http/https/email/sms/etc.)
                - endpoint: Endpoint to subscribe
                - attributes: Optional subscription attributes

        Returns:
            List of tuples containing (success, subscription_arn, error_message).
            For each subscription:
                - success: True if subscribed successfully, False otherwise
                - subscription_arn: Subscription ARN if successful, empty string if failed
                - error_message: Error message if failed, None if successful
        """
        results: List[Tuple[bool, str, Optional[str]]] = []

        def subscribe_single(subscription: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
            try:
                subscription_arn = self.subscribe(
                    topic_arn=topic_arn,
                    protocol=subscription["protocol"],
                    endpoint=subscription["endpoint"],
                    attributes=subscription.get("attributes"),
                )
                return True, subscription_arn, None
            except Exception as e:
                logger.exception(
                    "Failed to subscribe %s to SNS topic: %s",
                    subscription["endpoint"],
                    topic_arn,
                )
                return False, "", str(e)

        with ThreadPoolExecutor() as executor:
            results.extend(executor.map(subscribe_single, subscriptions))

        return results

    def batch_unsubscribe(
        self,
        subscription_arns: List[str],
    ) -> List[Tuple[bool, str, Optional[str]]]:
        """Unsubscribe multiple subscriptions in parallel.

        Args:
            subscription_arns: List of subscription ARNs to unsubscribe.

        Returns:
            List of tuples containing (success, subscription_arn, error_message).
            For each unsubscription:
                - success: True if unsubscribed successfully, False otherwise
                - subscription_arn: The ARN that was unsubscribed
                - error_message: Error message if failed, None if successful
        """
        results: List[Tuple[bool, str, Optional[str]]] = []

        def unsubscribe_single(arn: str) -> Tuple[bool, str, Optional[str]]:
            try:
                self.unsubscribe(subscription_arn=arn)
                return True, arn, None
            except Exception as e:
                logger.exception(
                    "Failed to unsubscribe from subscription: %s",
                    arn,
                )
                return False, arn, str(e)

        with ThreadPoolExecutor() as executor:
            results.extend(executor.map(unsubscribe_single, subscription_arns))

        return results
