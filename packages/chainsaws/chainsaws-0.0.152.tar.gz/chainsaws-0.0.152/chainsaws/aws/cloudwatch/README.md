# CloudWatch API

High-level interface for AWS CloudWatch Logs operations. This package provides an easy-to-use API for managing CloudWatch Logs, including log groups, streams, subscriptions, and queries.

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.aws.cloudwatch import CloudWatchAPI, LogLevel, RetentionDays
from datetime import datetime, timedelta

# Initialize API
logs = CloudWatchAPI()

# Create log group with retention
logs.create_log_group("/my-app/prod", retention_days=RetentionDays.ONE_MONTH)

# Get logger interface
logger = logs.get_logger("/my-app/prod")
logger.info("Application started")
logger.error("Error occurred")
```

## Core Components

### CloudWatchAPI

Main interface for CloudWatch Logs operations.

#### Log Group Operations

```python
# Create log group
logs.create_log_group(
    name="/aws/lambda/my-function",
    retention_days=RetentionDays.ONE_WEEK,
    tags={"Environment": "Production"}
)

# Create log stream
logs.create_log_stream(
    group_name="/aws/lambda/my-function",
    stream_name="2024/03/15"
)

# Describe log stream
stream = logs.describe_log_stream(
    group_name="/aws/lambda/my-function",
    stream_name="2024/03/15"
)
```

#### Logging Operations

```python
# Direct logging
logs.put_logs(
    group_name="/my-app/prod",
    stream_name="2024/03/15",
    events=[LogEvent(
        timestamp=datetime.now(),
        message="Application error",
        level=LogLevel.ERROR
    )]
)

# Using logger interface
logger = logs.get_logger("/my-app/prod")
logger.info("Application started")
logger.error("Error occurred")
logger.critical("Critical failure")
```

#### Lambda Subscriptions

```python
# Create Lambda subscription
logs.create_lambda_subscription(
    group_name="/my-app/prod",
    lambda_function_arn="arn:aws:lambda:region:account:function:error-processor",
    filter_pattern="[level=ERROR]"
)

# Delete subscription
logs.delete_lambda_subscription(
    group_name="/my-app/prod",
    name="ErrorProcessor",
    remove_permissions=True
)
```

#### Log Queries

```python
# Using QueryBuilder
from chainsaws.aws.cloudwatch import QueryBuilder

query = (QueryBuilder(logs)
    .log_groups("/my-app/prod")
    .filter(level="ERROR")
    .time_range(start=datetime.now() - timedelta(hours=1))
    .stats("count(*) as error_count")
    .group_by("@logStream")
    .sort("error_count", desc=True)
    .limit(10)
    .execute())

# Real-time log tailing
for event in logs.tail_logs(
    group_name="/my-app/prod",
    filter_pattern="[level=ERROR]",
    follow=True
):
    print(f"{event.timestamp}: {event.message}")
```

#### Log Export

```python
# Export logs to S3
task_id = logs.export_logs(
    group_name="/my-app/prod",
    destination_bucket="my-logs-bucket",
    prefix="app-logs/",
    start_time=datetime.now() - timedelta(days=1)
)
```

### CloudWatchLogger

Logger-style interface for CloudWatch Logs.

```python
logger = CloudWatchLogger(
    api=logs,
    log_group="/my-app/prod",
    batch_size=100,
    flush_interval=5.0
)

# Log methods
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Manual flush
logger.flush()
```

### QueryBuilder

Fluent interface for building CloudWatch Logs Insights queries.

```python
builder = QueryBuilder(logs)

# Building queries
query = (builder
    .log_groups("/my-app/prod", "/my-app/staging")
    .filter(level="ERROR")
    .parse_message("error_code=* status=*" as "error_data")
    .stats("count(*) as error_count")
    .group_by("error_data.error_code")
    .sort("error_count", desc=True)
    .limit(10)
    .time_range(
        start=datetime.now() - timedelta(hours=24)
    ))

# Execute query
results = query.execute()
```

### Integrate with builtin logger

```python
import logging
from chainsaws.aws.cloudwatch import CloudWatchAPI, CloudWatchHandler

# Setup CloudWatch handler
handler = CloudWatchHandler(
    api=CloudWatchAPI(),
    log_group="/my-app/prod",
    batch_size=100,
    tags={"Environment": "Production"}
)

# Configure logger
logger = logging.getLogger("my_app")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Use standard logging
logger.info("Application started")
logger.error("An error occurred", exc_info=True)
logger.warning("Resource usage high", extra={"memory": "85%"})

# Cleanup
handler.close()
```

## Data Models

### LogLevel

- `DEBUG`
- `INFO`
- `WARN`
- `ERROR`
- `CRITICAL`

### RetentionDays

- `ONE_DAY = 1`
- `THREE_DAYS = 3`
- `FIVE_DAYS = 5`
- `ONE_WEEK = 7`
- `TWO_WEEKS = 14`
- `ONE_MONTH = 30`
- `TWO_MONTHS = 60`
- `THREE_MONTHS = 90`
- `FOUR_MONTHS = 120`
- `FIVE_MONTHS = 150`
- `SIX_MONTHS = 180`
- `ONE_YEAR = 365`
- `FOREVER = 0`

### Configuration Models

- `CloudWatchAPIConfig`: API configuration
- `LogGroupConfig`: Log group creation settings
- `LogStreamConfig`: Log stream creation settings
- `LogEvent`: Individual log event
- `PutLogsConfig`: Log putting configuration
- `GetLogsConfig`: Log retrieval configuration
- `FilterPattern`: Log filter pattern
- `MetricFilter`: Metric filter configuration
- `SubscriptionFilter`: Subscription filter settings

### Query Models

- `QueryStatus`: Query execution status
- `QuerySortBy`: Query result sorting options
- `LogsInsightsQuery`: Query configuration
- `QueryResult`: Query execution results

## Error Handling

The API uses custom exceptions for error handling:

```python
try:
    logs.create_log_group("/my-app/prod")
except CloudWatchError as e:
    print(f"CloudWatch operation failed: {str(e)}")
```

## Best Practices

1. Use the logger interface for regular logging:

```python
logger = logs.get_logger("/my-app/prod")
```

2. Batch log events when possible:

```python
logger.batch_size = 100  # Default
logger.flush_interval = 5.0  # Seconds
```

3. Use appropriate retention periods:

```python
logs.create_log_group(
    name="/my-app/prod",
    retention_days=RetentionDays.ONE_MONTH
)
```

4. Clean up subscriptions when no longer needed:

```python
logs.delete_lambda_subscription(
    group_name="/my-app/prod",
    name="ErrorProcessor",
    remove_permissions=True
)
```
