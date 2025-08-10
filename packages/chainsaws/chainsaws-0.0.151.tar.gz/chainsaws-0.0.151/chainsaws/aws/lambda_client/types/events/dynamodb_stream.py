"""DynamoDB Stream event types for AWS Lambda."""

from typing import Any, Dict, List, Literal, TypedDict


class AttributeValue(TypedDict, total=False):
    """DynamoDB attribute value representation.

    Args:
        B (str, optional): Binary data.
        BS (List[str], optional): Set of binary values.
        BOOL (bool, optional): Boolean value.
        L (List, optional): List of values.
        M (Dict, optional): Map of attribute names and values.
        N (str, optional): Number as string.
        NS (List[str], optional): Set of number strings.
        NULL (bool, optional): Null value indicator.
        S (str, optional): String value.
        SS (List[str], optional): Set of strings.

    Reference:
        https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_streams_AttributeValue.html
    """
    B: str
    BS: List[str]
    BOOL: bool
    L: List
    M: Dict
    N: str
    NS: List[str]
    NULL: bool
    S: str
    SS: List[str]


class StreamRecord(TypedDict, total=False):
    """Information about a DynamoDB Stream record.

    Args:
        ApproximateCreationDateTime (int, optional): The approximate time the record was created.
        Keys (Dict[str, AttributeValue], optional): The primary key attributes for the DynamoDB item.
        NewImage (Dict[str, AttributeValue], optional): The item's attributes after the change.
        OldImage (Dict[str, AttributeValue], optional): The item's attributes before the change.
        SequenceNumber (str, optional): A unique identifier for the stream record.
        SizeBytes (int, optional): The size of the stream record in bytes.
        StreamViewType (str, optional): Determines what information is written to the stream.

    Reference:
        https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_streams_StreamRecord.html
    """
    ApproximateCreationDateTime: int
    Keys: Dict[str, AttributeValue]
    NewImage: Dict[str, AttributeValue]
    OldImage: Dict[str, AttributeValue]
    SequenceNumber: str
    SizeBytes: int
    StreamViewType: Literal[
        "KEYS_ONLY",
        "NEW_IMAGE",
        "OLD_IMAGE",
        "NEW_AND_OLD_IMAGES",
    ]


class DynamodbRecord(TypedDict, total=False):
    """A DynamoDB Stream record.

    Args:
        awsRegion (str, optional): The AWS region where the change occurred.
        dynamodb (StreamRecord, optional): The stream record information.
        eventID (str, optional): A unique identifier for this event.
        eventName (str, optional): The type of change that occurred.
        eventSource (str, optional): The AWS service that generated this event.
        eventSourceARN (str, optional): The ARN of the DynamoDB stream.
        eventVersion (str, optional): The version number of the stream record format.
        userIdentity (Any, optional): Identity information for the user that made the change.

    Reference:
        https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_streams_Record.html
    """
    awsRegion: str
    dynamodb: StreamRecord
    eventID: str
    eventName: Literal["INSERT", "MODIFY", "REMOVE"]
    eventSource: str
    eventSourceARN: str
    eventVersion: str
    userIdentity: Any


class DynamoDBStreamEvent(TypedDict):
    """Event sent to Lambda from a DynamoDB Stream.

    Args:
        Records (List[DynamodbRecord]): The list of DynamoDB Stream records.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html
    """
    Records: List[DynamodbRecord]
