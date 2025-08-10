"""CodeCommit event types for AWS Lambda."""

from typing import List, TypedDict


class Reference(TypedDict):
    """Git reference information.

    Args:
        commit (str): The commit ID.
        ref (str): The full reference name (e.g., refs/heads/main).
    """
    commit: str
    ref: str


class CodeCommit(TypedDict):
    """CodeCommit repository information.

    Args:
        references (List[Reference]): List of references that triggered the event.
    """
    references: List[Reference]


class CodeCommitMessage(TypedDict):
    """Individual CodeCommit event message.

    Args:
        awsRegion (str): The AWS region where the repository exists.
        codecommit (CodeCommit): Information about the CodeCommit repository.
        eventId (str): A unique identifier for the event.
        eventName (str): The name of the event that triggered the notification.
        eventPartNumber (int): The part number of the event if split across multiple messages.
        eventSource (str): The AWS service that generated the event.
        eventSourceARN (str): The ARN of the repository that triggered the event.
        eventTime (str): The time when the event occurred.
        eventTotalParts (int): Total number of parts if the event is split.
        eventTriggerConfigId (str): The ID of the trigger configuration.
        eventTriggerName (str): The name of the trigger that generated the event.
        eventVersion (str): The version of the event format.
        userIdentityARN (str): The ARN of the AWS identity that triggered the event.
    """
    awsRegion: str
    codecommit: CodeCommit
    eventId: str
    eventName: str
    eventPartNumber: int
    eventSource: str
    eventSourceARN: str
    eventTime: str
    eventTotalParts: int
    eventTriggerConfigId: str
    eventTriggerName: str
    eventVersion: str
    userIdentityARN: str


class CodeCommitMessageEvent(TypedDict):
    """CodeCommit event sent to Lambda functions.

    Args:
        Records (List[CodeCommitMessage]): List of CodeCommit event messages.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/services-codecommit.html
    """
    Records: List[CodeCommitMessage]
