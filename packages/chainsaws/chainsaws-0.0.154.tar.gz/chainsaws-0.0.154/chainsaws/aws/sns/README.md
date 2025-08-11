# AWS SNS Client

This package provides a high-level interface for working with AWS Simple Notification Service (SNS).

## Features

- Easy topic creation and management
- Message publishing with support for attributes and filtering
- Subscription management with multiple protocols
- Pydantic models for type safety
- Automatic pagination for listing operations
- Comprehensive error handling
- **Batch operations support**
  - Parallel message publishing
  - Bulk subscription management
  - Error handling and result tracking
- Dataclasses for type safety

## Installation

This module is part of the `chainsaws` package. Install it using pip:

```bash
pip install chainsaws
```

## Usage

### Basic Usage

```python
from chainsaws.aws.sns import SNSClient

# Initialize the client
sns = SNSClient()

# Create a topic
topic = sns.create_topic(
    name="my-notifications",
    display_name="My Notifications",
)

# Publish a simple message
message_id = sns.publish(
    topic_arn=topic.topic_arn,
    message="Hello from chainsaws!",
)

# Subscribe an email endpoint
subscription = sns.subscribe(
    topic_arn=topic.topic_arn,
    protocol="email",
    endpoint="user@example.com",
)
```

### Batch Operations

```python
from chainsaws.aws.sns import SNSClient, SNSMessage, SNSMessageAttributes

# Initialize client
sns = SNSClient()

# Batch publish messages
messages = [
    "Simple message 1",
    "Simple message 2",
    SNSMessage(
        message="Complex message",
        subject="Test",
        message_attributes={
            "priority": SNSMessageAttributes(
                string_value="high",
                data_type="String",
            ),
        },
    ),
]

result = sns.batch_publish(topic_arn, messages)
print(f"Successfully published {result.success_count} messages")
print(f"Failed to publish {result.failure_count} messages")

# Batch subscribe endpoints
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
    },
    {
        "protocol": "sms",
        "endpoint": "+1234567890"
    }
]

result = sns.batch_subscribe(topic_arn, subscriptions)
print(f"Created {result.success_count} subscriptions")
for sub_arn in result.successful:
    print(f"Successfully subscribed: {sub_arn}")
for sub, error in result.failed:
    print(f"Failed to subscribe {sub['endpoint']}: {error}")

# Batch unsubscribe
subscription_arns = [
    "arn:aws:sns:region:account:topic:subscription1",
    "arn:aws:sns:region:account:topic:subscription2"
]
result = sns.batch_unsubscribe(subscription_arns)
print(f"Successfully unsubscribed {result.success_count} endpoints")
```

### Advanced Usage

```python
from chainsaws.aws.sns import SNSClient, SNSMessage, SNSMessageAttributes

# Initialize client with specific credentials
sns = SNSClient(
    credentials=AWSCredentials(
        access_key_id="your-access-key",
        secret_access_key="your-secret-key",
    ),
    region_name="us-west-2",
)

# Create a topic with tags and policy
topic = sns.create_topic(
    name="notifications",
    display_name="System Notifications",
    tags={"environment": "production"},
    policy={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "SNS:Publish",
                "Resource": "arn:aws:sns:*:*:notifications",
            }
        ],
    },
)

# Create a message with attributes
message = SNSMessage(
    message="Hello with attributes!",
    subject="Greeting",
    message_attributes={
        "priority": SNSMessageAttributes(
            string_value="high",
            data_type="String",
        ),
    },
)

# Publish the message
sns.publish(topic.topic_arn, message)

# Subscribe with message filtering
subscription = sns.subscribe(
    topic_arn=topic.topic_arn,
    protocol="https",
    endpoint="https://example.com/webhook",
    raw_message_delivery=True,
    filter_policy={
        "priority": ["high"],
    },
)

# List all topics
for topic in sns.list_topics():
    print(f"Found topic: {topic.topic_name}")

# List subscriptions for a topic
for sub in sns.list_subscriptions(topic.topic_arn):
    print(f"Found subscription: {sub.endpoint}")

# Cleanup
sns.unsubscribe(subscription.subscription_arn)
sns.delete_topic(topic.topic_arn)
```

## Models

### SNSTopic

Represents an SNS topic with the following attributes:

- `topic_arn`: The ARN of the topic
- `topic_name`: The name of the topic
- `display_name`: Optional display name
- `policy`: Optional access policy
- `delivery_policy`: Optional delivery policy
- `tags`: Optional tags
- `created_at`: Creation timestamp

### SNSMessage

Represents a message to be published with:

- `message`: The message content
- `subject`: Optional subject
- `message_attributes`: Optional message attributes
- `message_structure`: Optional message structure
- `message_deduplication_id`: Optional deduplication ID
- `message_group_id`: Optional message group ID

### SNSSubscription

Represents a topic subscription with:

- `subscription_arn`: The ARN of the subscription
- `topic_arn`: The ARN of the topic
- `protocol`: The subscription protocol
- `endpoint`: The subscription endpoint
- `raw_message_delivery`: Whether raw message delivery is enabled
- `filter_policy`: Optional message filter policy
- `created_at`: Creation timestamp

## Error Handling

The client wraps all AWS errors in custom exceptions:

```python
from chainsaws.aws.shared.exceptions import AWSError

try:
    sns.publish(topic_arn, "Hello!")
except AWSError as e:
    print(f"Failed to publish message: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
