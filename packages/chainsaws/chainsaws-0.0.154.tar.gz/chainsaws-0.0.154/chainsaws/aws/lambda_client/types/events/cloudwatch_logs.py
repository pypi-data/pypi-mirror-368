"""CloudWatch Logs event types for AWS Lambda."""

from typing import List, TypedDict


class LogEvent(TypedDict):
    """Individual log event information.

    Args:
        id (str): Unique identifier for the log event.
        timestamp (int): The time the event occurred, expressed as number of milliseconds.
        message (str): The log event message.
    """
    id: str
    timestamp: int
    message: str


class CloudWatchLogsDecodedData(TypedDict):
    """Decoded CloudWatch Logs data after processing.

    Args:
        messageType (str): Type of the message. Usually "DATA_MESSAGE" for actual log data,
            or "CONTROL_MESSAGE" for CloudWatch Logs system messages.
        owner (str): The AWS account ID of the originating log data.
        logGroup (str): The log group name where the log data originated.
        logStream (str): The log stream name where the log data originated.
        subscriptionFilters (List[str]): The subscription filters that matched with this log data.
        logEvents (List[LogEvent]): The actual log events.

    Reference:
        https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/SubscriptionFilters.html
    """
    messageType: str
    owner: str
    logGroup: str
    logStream: str
    subscriptionFilters: List[str]
    logEvents: List[LogEvent]


class AWSLogs(TypedDict):
    """Container for the compressed and encoded log data.

    Args:
        data (str): The log data, base64 encoded and compressed in gzip format.
    """
    data: str


class CloudWatchLogsEvent(TypedDict):
    """CloudWatch Logs event sent to Lambda functions.

    Args:
        awslogs (AWSLogs): Container for the encoded and compressed log data.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchlogs.html
    """
    awslogs: AWSLogs
