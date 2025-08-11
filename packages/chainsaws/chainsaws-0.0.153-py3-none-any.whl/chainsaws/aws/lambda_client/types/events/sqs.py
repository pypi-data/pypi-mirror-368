"""SQS (Simple Queue Service) event types for AWS Lambda."""
from typing import Dict, List, Literal, TypedDict


class SQSAttributes(TypedDict, total=False):
    """Message system attributes.

    Args:
        ApproximateReceiveCount (str, optional): Number of times message was received.
        SentTimestamp (str, optional): When the message was sent to the queue.
        SenderId (str, optional): AWS account number of the message sender.
        ApproximateFirstReceiveTimestamp (str, optional): When message was first received.
        SequenceNumber (str, optional): Sequence number (FIFO queues only).
        MessageGroupId (str, optional): Message group ID (FIFO queues only).
        MessageDeduplicationId (str, optional): Deduplication ID (FIFO queues only).
        DeadLetterQueueSourceArn (str, optional): ARN of source DLQ.
        AWSTraceHeader (str, optional): X-Ray tracing header.
    """
    ApproximateReceiveCount: str
    SentTimestamp: str
    SenderId: str
    ApproximateFirstReceiveTimestamp: str
    SequenceNumber: str
    MessageGroupId: str
    MessageDeduplicationId: str
    DeadLetterQueueSourceArn: str
    AWSTraceHeader: str


class SQSMessageAttribute(TypedDict, total=False):
    """Custom message attribute.

    Args:
        binaryValue (str, optional): Binary attribute value.
        dataType (str): The attribute data type.
        stringValue (str): String attribute value.
        stringListValues (List[str]): List of string values.
        binaryListValues (List[str]): List of binary values.

    Reference:
        https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_MessageAttributeValue.html
    """
    binaryValue: str
    dataType: Literal["String", "Number", "Binary"]
    stringValue: str
    stringListValues: List[str]
    binaryListValues: List[str]


class SQSMessage(TypedDict, total=False):
    """Individual SQS message.

    Args:
        messageId (str, optional): Unique identifier for the message.
        receiptHandle (str, optional): Handle used to delete the message.
        body (str, optional): The message body.
        attributes (SQSAttributes, optional): System attributes.
        messageAttributes (Dict[str, SQSMessageAttribute], optional): Custom attributes.
        md5OfBody (str, optional): MD5 hash of the message body.
        md5OfMessageAttributes (str, optional): MD5 hash of message attributes.
        eventSource (str, optional): The AWS service that generated the event.
        eventSourceARN (str, optional): ARN of the SQS queue.
        awsRegion (str, optional): AWS region of the queue.

    Reference:
        https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_Message.html
    """
    messageId: str
    receiptHandle: str
    body: str
    attributes: SQSAttributes
    messageAttributes: Dict[str, SQSMessageAttribute]
    md5OfBody: str
    md5OfMessageAttributes: str
    eventSource: str
    eventSourceARN: str
    awsRegion: str


class SQSEvent(TypedDict):
    """Event sent by SQS to Lambda.

    Args:
        Records (List[SQSMessage]): The list of SQS messages.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
    """
    Records: List[SQSMessage]
