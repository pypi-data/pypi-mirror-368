# EventBridge API

A high-level API for AWS EventBridge that simplifies event-driven architecture implementation.

## Features

- Event bus management (create, delete, list)
- Event publishing
- Rule management (create, enable/disable)
- Multiple AWS service targets support
- Type-safe API with builder pattern

## Quick Start

```python
from chainsaws.aws.eventbridge import (
    EventBridgeAPI,
    EventPattern,
    TargetBuilder,
    InputTransformer,
    RetryPolicy,
)

# Initialize API client
eventbridge = EventBridgeAPI()

# Create an event bus
bus = eventbridge.create_event_bus(
    name="my-app-events",
    tags={"Environment": "prod"}
)

# Create a rule with event pattern
pattern = EventPattern(
    source=["aws.s3"],
    detail_type=["Object Created"],
    detail={"bucket": {"name": ["my-bucket"]}}
)

rule = eventbridge.create_rule(
    name="s3-object-created",
    event_pattern=pattern,
    event_bus_name=bus.name
)
```

## Setting Up Targets

EventBridge supports various AWS services as targets. Use `TargetBuilder` to configure targets with a fluent interface:

### Lambda Function Target

```python
builder = TargetBuilder("us-east-1", "123456789012")

lambda_target = (builder.lambda_function("process-upload")
    .with_input({"operation": "resize"})
    .with_retry_policy(RetryPolicy(maximum_retry_attempts=5))
    .with_dead_letter_queue("arn:aws:sqs:us-east-1:123456789012:dlq")
    .build())

eventbridge.put_targets(rule="s3-object-created", targets=[lambda_target])
```

### SQS Queue Target

```python
sqs_target = (builder.sqs_queue("notifications.fifo", "uploads")
    .with_input_transformer(InputTransformer(
        input_paths={"bucket": "$.detail.bucket.name", "key": "$.detail.object.key"},
        input_template='{"message": "New file uploaded to <bucket>: <key>"}'
    ))
    .build())
```

### SNS Topic Target

```python
sns_target = (builder.sns_topic("alerts")
    .with_input({"alert": "High CPU usage"})
    .with_dead_letter_queue("arn:aws:sqs:us-east-1:123456789012:dlq")
    .build())
```

### Step Functions Target

```python
sfn_target = (builder.step_functions("order-processing")
    .with_input({"source": "eventbridge"})
    .with_role("arn:aws:iam::123456789012:role/eventbridge-sfn-role")
    .build())
```

### Kinesis Stream Target

```python
kinesis_target = (builder.kinesis_stream("data-stream", "$.detail.userId")
    .with_role("arn:aws:iam::123456789012:role/eventbridge-kinesis-role")
    .build())
```

### ECS Task Target

```python
ecs_target = (builder.ecs_task(
    "my-cluster",
    "task-def:1",
    network_config={
        "awsvpcConfiguration": {
            "subnets": ["subnet-1234"],
            "securityGroups": ["sg-1234"]
        }
    })
    .with_role("arn:aws:iam::123456789012:role/eventbridge-ecs-role")
    .build())
```

## Publishing Events

```python
from chainsaws.aws.eventbridge import PutEventsRequestEntry

# Send a single event
response = eventbridge.put_events([
    PutEventsRequestEntry(
        source="com.myapp",
        detail_type="UserSignup",
        detail={"userId": "123", "email": "user@example.com"}
    )
])

# Check for failed events
if response.failed_entry_count > 0:
    print(f"Failed to send {response.failed_entry_count} events")
```

## Advanced Features

### Input Transformation

EventBridge can transform event data before sending it to targets:

```python
# Static input
target = builder.lambda_function("my-function")
    .with_input({"static": "value"})
    .build()

# Dynamic input using JSONPath
target = builder.lambda_function("my-function")
    .with_input_path("$.detail")
    .build()

# Input transformer
target = builder.lambda_function("my-function")
    .with_input_transformer(InputTransformer(
        input_paths={
            "user": "$.detail.user",
            "action": "$.detail-type"
        },
        input_template='{"user": <user>, "action": <action>}'
    ))
    .build()
```

### Retry Policies

Configure retry policies for handling failed event deliveries:

```python
target = builder.lambda_function("my-function")
    .with_retry_policy(RetryPolicy(
        maximum_retry_attempts=5,
        maximum_event_age_in_seconds=3600
    ))
    .build()
```

### Dead Letter Queues

Set up Dead Letter Queues (DLQ) to handle failed events:

```python
target = builder.lambda_function("my-function")
    .with_dead_letter_queue("arn:aws:sqs:us-east-1:123456789012:dlq")
    .build()
```

## Best Practices

1. **Separate Event Buses**: Use different event buses for different applications or environments.
2. **Meaningful Names**: Use descriptive names for rules and targets.
3. **Retry Policies**: Configure appropriate retry policies for critical events.
4. **DLQ Configuration**: Set up Dead Letter Queues to handle failed events.
5. **IAM Roles**: Follow the principle of least privilege when configuring IAM roles.

## Important Notes

1. **Scheduling**: Use EventBridge Scheduler API for scheduling tasks instead of EventBridge rules.
2. **Case Sensitivity**: Event patterns are case-sensitive.
3. **IAM Permissions**: Ensure proper IAM permissions are set up for targets.
4. **FIFO Queues**: Always set MessageGroupId when using FIFO SQS queues as targets.

## Common Event Patterns

### AWS Service Events

```python
# S3 Object Created
pattern = EventPattern(
    source=["aws.s3"],
    detail_type=["Object Created"],
    detail={"bucket": {"name": ["my-bucket"]}}
)

# EC2 State Change
pattern = EventPattern(
    source=["aws.ec2"],
    detail_type=["EC2 Instance State-change Notification"],
    detail={"state": ["running", "stopped"]}
)

# Custom Application Events
pattern = EventPattern(
    source=["custom.myapp"],
    detail_type=["UserAction"],
    detail={"action": ["login", "logout"]}
)
```

## Error Handling

The API provides detailed error information:

```python
try:
    response = eventbridge.put_events([event])
    if response.failed_entry_count > 0:
        for entry in response.entries:
            if "ErrorCode" in entry:
                print(f"Error: {entry['ErrorCode']} - {entry['ErrorMessage']}")
except Exception as e:
    print(f"Failed to send events: {e}")
```

## Type Safety

The API is designed to be type-safe:

```python
from chainsaws.aws.eventbridge import EventSource

# This will raise a type error if source is not a valid AWS service
event = PutEventsRequestEntry(
    source=EventSource.aws_s3,  # Type checked
    detail_type="ObjectCreated",
    detail={"bucket": "my-bucket"}
)
```

## Target Builder Pattern

The builder pattern provides a fluent interface for configuring targets:

```python
# Chain multiple configurations
target = (builder.lambda_function("my-function")
    .with_input({"key": "value"})
    .with_retry_policy(RetryPolicy(maximum_retry_attempts=3))
    .with_dead_letter_queue("arn:aws:sqs:us-east-1:123456789012:dlq")
    .with_role("arn:aws:iam::123456789012:role/my-role")
    .build())

# Each method returns the builder instance for chaining
# The build() method creates the final Target instance
```
