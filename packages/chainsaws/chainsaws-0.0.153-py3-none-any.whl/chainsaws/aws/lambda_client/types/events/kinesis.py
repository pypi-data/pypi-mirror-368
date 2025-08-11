"""Kinesis Stream event types for AWS Lambda."""
from typing import List, TypedDict


class KinesisRecord(TypedDict):
    """Information about a record in a Kinesis stream.

    Args:
        kinesisSchemaVersion (str): Version number of the schema.
        partitionKey (str): Key used to determine which shard receives the record.
        sequenceNumber (str): Unique identifier for the record within its shard.
        data (str): Base64-encoded record data.
        approximateArrivalTimestamp (float): When the record arrived in the stream.
    """
    kinesisSchemaVersion: str
    partitionKey: str
    sequenceNumber: str
    data: str
    approximateArrivalTimestamp: float


class KinesisStreamRecord(TypedDict):
    """A record from a Kinesis stream event.

    Args:
        kinesis (KinesisRecord): The record data and metadata.
        eventSource (str): The AWS service that generated this event.
        eventVersion (str): The version number of the event structure.
        eventID (str): A unique identifier for this event.
        eventName (str): The type of event (e.g., "aws:kinesis:record").
        invokeIdentityArn (str): The ARN of the Lambda function's execution role.
        awsRegion (str): The AWS region where the event originated.
        eventSourceARN (str): The ARN of the Kinesis stream.
    """
    kinesis: KinesisRecord
    eventSource: str
    eventVersion: str
    eventID: str
    eventName: str
    invokeIdentityArn: str
    awsRegion: str
    eventSourceARN: str


class KinesisStreamEvent(TypedDict):
    """Event sent by Kinesis Streams to Lambda.

    Args:
        Records (List[KinesisStreamRecord]): The list of records from the stream.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html
    """
    Records: List[KinesisStreamRecord]
