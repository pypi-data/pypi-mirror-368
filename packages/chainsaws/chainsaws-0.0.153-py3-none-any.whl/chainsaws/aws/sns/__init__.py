"""AWS SNS (Simple Notification Service) client for chainsaws.

This module provides a high-level interface for working with AWS SNS,
making it easier to manage topics, subscriptions, and message publishing.

Example:
    ```python
    from chainsaws.aws.sns import SNSClient
    
    # Initialize the client
    sns = SNSClient()
    
    # Create a topic
    topic_arn = sns.create_topic("my-topic")
    
    # Publish a message
    sns.publish(topic_arn, "Hello from chainsaws!")
    ```
"""

from chainsaws.aws.sns.sns import SNSClient
from chainsaws.aws.sns.sns_models import (
    SNSMessage,
    SNSMessageAttributes,
    SNSSubscription,
    SNSTopic,
)

__all__ = [
    "SNSClient",
    "SNSMessage",
    "SNSMessageAttributes",
    "SNSSubscription",
    "SNSTopic",
]
