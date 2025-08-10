"""SNS (Simple Notification Service) event types for AWS Lambda."""

from typing import Dict, List, TypedDict


class SNSMessageAttribute(TypedDict):
    """SNS message attribute value.

    Args:
        Type (str): The data type of the attribute value.
        Value (str): The attribute value.

    Reference:
        https://docs.aws.amazon.com/sns/latest/api/API_MessageAttributeValue.html
    """
    Type: str
    Value: str


class SNSMessage(TypedDict):
    """Information about an SNS message.

    Args:
        SignatureVersion (str): Version of the SNS signature.
        Timestamp (str): When the message was published.
        Signature (str): The message signature.
        SigningCertUrl (str): URL of the certificate used for signing.
        MessageId (str): Unique identifier for the message.
        Message (str): The message content.
        MessageAttributes (Dict[str, SNSMessageAttribute]): Custom attributes.
        Type (str): The type of message.
        UnsubscribeUrl (str): URL to unsubscribe from the topic.
        TopicArn (str): ARN of the SNS topic.
        Subject (str): The message subject.
    """
    SignatureVersion: str
    Timestamp: str
    Signature: str
    SigningCertUrl: str
    MessageId: str
    Message: str
    MessageAttributes: Dict[str, SNSMessageAttribute]
    Type: str
    UnsubscribeUrl: str
    TopicArn: str
    Subject: str


class SNSEventRecord(TypedDict):
    """Individual SNS event record.

    Args:
        EventVersion (str): Version of the event structure.
        EventSubscriptionArn (str): ARN of the subscription.
        EventSource (str): The AWS service that generated the event.
        Sns (SNSMessage): The SNS message information.
    """
    EventVersion: str
    EventSubscriptionArn: str
    EventSource: str
    Sns: SNSMessage


class SNSEvent(TypedDict):
    """Event sent by SNS to Lambda.

    Args:
        Records (List[SNSEventRecord]): The list of SNS records.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/with-sns.html
    """
    Records: List[SNSEventRecord]
