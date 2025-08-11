# AWS SQS Client

High-level AWS SQS (Simple Queue Service) client wrapper providing simplified interface for queue operations with type safety and error handling.

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.aws.sqs import SQSAPI

# Initialize client
sqs = SQSAPI("https://sqs.ap-northeast-2.amazonaws.com/177715257436/MyQueue")

# Send a message
response = sqs.send_message({"key": "value"})
print(f"Message sent with ID: {response.message_id}")

# Send multiple messages
batch_response = sqs.send_message_batch([
    {"key1": "value1"},
    {"key2": "value2"}
])
print(f"Successfully sent: {len(batch_response.successful)}")

# Receive messages
messages = sqs.receive_messages(max_messages=10)
for msg in messages.messages:
    print(f"Received: {msg.body}")
    sqs.delete_message(msg.receipt_handle)
```

## Detailed Usage

### Configuration

```python
from chainsaws.aws.sqs import SQSAPI, SQSAPIConfig
from chainsaws.aws.shared.config import AWSCredentials

config = SQSAPIConfig(
    region="us-west-2",
    credentials=AWSCredentials(
        aws_access_key_id="YOUR_ACCESS_KEY",
        aws_secret_access_key="YOUR_SECRET_KEY"
    )
)

sqs = SQSAPI(
    queue_url="https://sqs.ap-northeast-2.amazonaws.com/177715257436/MyQueue",
    config=config
)
```

### Message Operations

#### Sending Messages

```python
# Send single message
response = sqs.send_message(
    message_body={"data": "value"},
    delay_seconds=0,
    attributes={"attr1": {"DataType": "String", "StringValue": "value"}}
)

# Send batch messages
responses = sqs.send_message_batch([
    {"data1": "value1"},
    {"data2": "value2"}
])
```

#### Receiving Messages

```python
# Basic receive
messages = sqs.receive_messages()

# Advanced receive with options
messages = sqs.receive_messages(
    max_messages=10,  # 1-10 messages
    visibility_timeout=30,  # 30 seconds
    wait_time_seconds=20  # Long polling 20 seconds
)
```

#### Deleting Messages

```python
# Delete single message
sqs.delete_message(receipt_handle="message-receipt-handle")

# Delete multiple messages
sqs.delete_message_batch([
    "receipt-handle-1",
    "receipt-handle-2"
])
```

### Queue Management

```python
# Get queue attributes
attrs = sqs.get_attributes()
print(f"Messages in queue: {attrs.approximate_number_of_messages}")

# Delete all messages
sqs.delete_all_message()
```

## Response Models

### SQSResponse

- `message_id`: Unique identifier for the message
- `md5_of_message_body`: MD5 hash of the message body
- `sequence_number`: Sequence number (FIFO queues)

### SQSReceivedMessage

- `message_id`: Message identifier
- `receipt_handle`: Receipt handle for deletion
- `body`: Message content
- `attributes`: Message system attributes
- `message_attributes`: Custom message attributes

## Error Handling

The client includes comprehensive error handling:

```python
try:
    response = sqs.send_message({"key": "value"})
except Exception as e:
    print(f"Failed to send message: {str(e)}")
```

## Best Practices

1. **Message Batching**

   - Use `send_message_batch` for multiple messages
   - More efficient than individual sends
   - Maximum 10 messages per batch

2. **Long Polling**

   - Use `wait_time_seconds` in receive_messages
   - Reduces empty responses
   - Recommended value: 20 seconds

3. **Message Cleanup**

   - Always delete processed messages
   - Use batch deletion when possible
   - Handle deletion errors

4. **Error Handling**
   - Implement proper error handling
   - Check batch operation results
   - Monitor failed operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
