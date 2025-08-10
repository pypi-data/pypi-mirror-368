"""Apache Kafka event types for AWS Lambda."""


from typing import Dict, List, Literal, TypedDict


class ApacheKafkaRecord(TypedDict):
    """Represents a single record from an Apache Kafka topic.

    Args:
        topic (str): The Kafka topic name.
        partition (int): The partition number within the topic.
        offset (int): The offset of the record in the partition.
        timestamp (int): The timestamp of the record.
        timestampType (str): The type of timestamp ("CREATE_TIME" or "LOG_APPEND_TIME").
        key (str): The record key.
        value (str): The record value/content.
        headers (List[Dict]): List of Kafka record headers.
    """
    topic: str
    partition: int
    offset: int
    timestamp: int
    timestampType: Literal["CREATE_TIME", "LOG_APPEND_TIME"]
    key: str
    value: str
    headers: List[Dict]


class ApacheKafkaEvent(TypedDict):
    """Event sent by AWS Lambda's Apache Kafka trigger.

    Args:
        eventSource (str): Must be "SelfManagedKafka".
        bootstrapServers (str): Comma-separated list of Kafka broker addresses.
        records (Dict[str, List[ApacheKafkaRecord]]): Records grouped by topic partition.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/with-kafka.html
    """
    eventSource: Literal["SelfManagedKafka"]
    bootstrapServers: str
    records: Dict[str, List[ApacheKafkaRecord]]
