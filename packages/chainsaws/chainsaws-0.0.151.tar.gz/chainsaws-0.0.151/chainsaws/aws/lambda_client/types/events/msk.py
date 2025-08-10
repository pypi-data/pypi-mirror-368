"""MSK (Managed Streaming for Apache Kafka) event types for AWS Lambda."""


from typing import Dict, List, Literal, TypedDict


class MSKRecord(TypedDict):
    """Individual record from an MSK topic partition.

    Args:
        topic (str): The Kafka topic that contains the record.
        partition (str): The topic partition number.
        offset (int): The record's offset within its partition.
        timestamp (int): The record timestamp.
        timestampType (str): How the timestamp was generated.
        value (str): Base64-encoded record value.
        headers (List[Dict]): Kafka record headers.
    """
    topic: str
    partition: str
    offset: int
    timestamp: int
    timestampType: Literal[
        "CREATE_TIME",  # Set by the producer
        "LOG_APPEND_TIME",  # Set by the broker
    ]
    value: str
    headers: List[Dict]


class MSKEvent(TypedDict):
    """Event sent by MSK to Lambda.

    Args:
        eventSource (str): Must be "aws:kafka".
        eventSourceArn (str): The ARN of the MSK cluster.
        records (Dict[str, List[MSKRecord]]): Records grouped by topic partition.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/with-msk.html
    """
    eventSource: Literal["aws:kafka"]
    eventSourceArn: str
    records: Dict[str, List[MSKRecord]]
