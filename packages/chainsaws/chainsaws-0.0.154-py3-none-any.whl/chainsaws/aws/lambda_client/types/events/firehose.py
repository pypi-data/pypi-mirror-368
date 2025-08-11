"""Firehose event types for AWS Lambda."""

from typing import List, TypedDict


class FirehoseRecordMetadata(TypedDict):
    """Metadata for a record from a Kinesis stream.

    Args:
        shardId (str): The shard ID within the Kinesis stream.
        partitionKey (str): The key used to partition the record.
        approximateArrivalTimestamp (str): When the record arrived in the stream.
        sequenceNumber (str): The unique identifier of the record within its shard.
        subsequenceNumber (str): Used for de-aggregated records.
    """
    shardId: str
    partitionKey: str
    approximateArrivalTimestamp: str
    sequenceNumber: str
    subsequenceNumber: str


class FirehoseRecord(TypedDict):
    """Individual record in a Firehose delivery stream.

    Args:
        data (str): Base64-encoded record data.
        recordId (str): Unique identifier for this record.
        approximateArrivalTimestamp (int): When the record arrived in the delivery stream.
        kinesisRecordMetadata (FirehoseRecordMetadata): Metadata when source is a Kinesis stream.
    """
    data: str
    recordId: str
    approximateArrivalTimestamp: int
    kinesisRecordMetadata: FirehoseRecordMetadata


class FirehoseEvent(TypedDict):
    """Event sent by Firehose to Lambda for data transformation.

    Args:
        invocationId (str): Unique identifier for this Lambda invocation.
        deliveryStreamArn (str): ARN of the Firehose delivery stream.
        region (str): AWS region of the delivery stream.
        records (List[FirehoseRecord]): The records to be processed.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html
    """
    invocationId: str
    deliveryStreamArn: str
    region: str
    records: List[FirehoseRecord]
