# AWS Kinesis Firehose Client

High-level client for AWS Kinesis Firehose operations with S3 destination support.

## Quick Start

```python
from chainsaws.aws.firehose import FirehoseAPI, FirehoseAPIConfig
from chainsaws.aws.s3 import S3APIConfig

# Initialize Firehose client
firehose = FirehoseAPI(
    delivery_stream_name="my-stream",
    bucket_name="my-bucket",
    object_key_prefix="logs/"
)

# Create resources (S3 bucket and Firehose delivery stream)
firehose.create_resource()

# Put records
firehose.put_record({"message": "Hello, World!", "timestamp": "2024-01-01T00:00:00Z"})
```

## Configuration

### Basic Configuration

```python
config = FirehoseAPIConfig(
    region="ap-northeast-2",
    max_retries=3,
    timeout=30
)

s3_config = S3APIConfig(
    region="ap-northeast-2",
    acl="private"
)

firehose = FirehoseAPI(
    delivery_stream_name="my-stream",
    bucket_name="my-bucket",
    object_key_prefix="logs/", # Optional, defaults to "logs/"
    error_prefix="error/",  # Optional, defaults to "error/"
    config=config,
    s3_config=s3_config
)
```

### AWS Credentials

The client uses the standard AWS credential chain. You can also explicitly provide credentials:

```python
from chainsaws.aws.shared.shared import AWSCredentials

config = FirehoseAPIConfig(
    credentials=AWSCredentials(
        "aws_access_key_id": "AKIAXXXXXXXXXXXXXXXX",
        "aws_secret_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "region_name": "ap-northeast-2",
        "profile_name": "default"
    )
)
```

## Features

### Create Delivery Stream

```python
# Creates S3 bucket, IAM role, and Firehose delivery stream
firehose.create_resource(
    max_retries=3,  # Number of retries for stream creation
    retry_delay=4   # Delay between retries in seconds
)
```

### Put Records

```python
# Put string data
firehose.put_record("raw string data")

# Put JSON data (automatically serialized)
firehose.put_record({
    "id": 123,
    "message": "Hello",
    "timestamp": "2024-01-01T00:00:00Z"
})

# Put binary data
firehose.put_record(b"binary data")
```

### Put Records in Batch

```python
# Put multiple records in batch
records = [
    {"id": 1, "message": "Hello"},
    {"id": 2, "message": "World"},
    {"id": 3, "message": "!"}
]

result = firehose.put_record_batch(records)
print(f"Successfully delivered {result['successful_records']} out of {result['total_records']} records")

# Customize batch processing
result = firehose.put_record_batch(
    records,
    batch_size=100,        # Default: 500 (max: 500)
    retry_failed=True,     # Default: True
    max_retries=3         # Default: 3
)

# Handle batch results
if result['failed_records']:
    print("Failed records:")
    for failure in result['failed_records']:
        print(f"Record: {failure['record']}")
        print(f"Error: {failure['error']}")
        print(f"Attempt: {failure['attempt']}")
```

The batch API provides several advantages:

- Process up to 500 records in a single request
- Automatic retry of failed records
- Exponential backoff between retries
- Detailed failure reporting
- Memory-efficient processing of large datasets

#### Batch Response Structure

```python
{
    'total_records': 1000,          # Total number of records processed
    'successful_records': 995,      # Number of successfully delivered records
    'failed_records': [             # List of failed records with details
        {
            'record': '{"id": 1}',  # The original record
            'error': 'Error message',# Error description
            'attempt': 2            # Retry attempt number
        }
        # ... more failed records ...
    ],
    'batch_responses': [            # Raw responses from each batch operation
        {
            'FailedPutCount': 0,
            'RequestResponses': [...]
        }
        # ... more batch responses ...
    ]
}
```

#### Best Practices for Batch Operations

1. Choose appropriate batch size:

   - Larger batches (up to 500) are more efficient
   - Smaller batches provide better error isolation

2. Configure retry behavior:

   - Enable retries for improved reliability
   - Adjust max_retries based on your requirements
   - Consider implementing custom backoff logic for failed batches

3. Monitor batch operations:

   - Track failed_records for error patterns
   - Log batch statistics for performance monitoring
   - Implement alerts for high failure rates

4. Handle partial failures:
   - Check FailedPutCount in each batch response
   - Process failed_records list for detailed error information
   - Consider storing failed records for later retry

### Read Logs from S3

```python
# Generate JSON logs from S3 objects
for objects, key in firehose.generate_log_json_list():
    for log in objects:
        print(f"Log from {key}: {log}")

# Start after specific key
for objects, key in firehose.generate_log_json_list(key_start_after="logs/2024/01/01"):
    print(f"Processing logs from {key}")
```

## Error Handling

The client includes built-in error handling and retries:

- Automatic retries for delivery stream creation
- IAM role creation with existence check
- S3 bucket initialization with existence check
- Detailed error logging

## Logging

The module uses Python's standard logging system. To enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. Always use `create_resource()` before putting records
2. Handle rate limits by implementing appropriate delays
3. Monitor error logs for delivery failures
4. Use appropriate prefixes for better S3 organization
5. Configure appropriate IAM permissions
