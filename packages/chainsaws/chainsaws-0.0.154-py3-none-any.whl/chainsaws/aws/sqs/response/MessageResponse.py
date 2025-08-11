from typing import Dict, TypedDict
from chainsaws.aws.sqs.sqs_models import MessageAttributesValue

class MessageResponse(TypedDict):
    MD5OfMessageBody: str
    MD5OfMessageAttributes: str
    MD5OfMessageSystemAttributes: str
    MessageId: str
    SequenceNumber: str

SendMessageResponse = MessageResponse

class SendMessageBatchResultSuccessEntry(MessageResponse):
    Id: str

class SendMessageBatchResultErrorEntry(TypedDict):
    Id: str
    Code: str
    Message: str
    SenderFault: bool

class SendMessageBatchResponse(TypedDict):
    Successful: list[SendMessageBatchResultSuccessEntry]
    Failed: list[SendMessageBatchResultErrorEntry]


class ReceiveMessageResponseMessage(MessageResponse):
    ReceiptHandle: str
    MD5OfBody: str
    Body: str
    Attributes: Dict[str, str]
    MD5OfMessageAttributes: str
    MessageAttributes: dict[str, MessageAttributesValue]


class ReceiveMessageResponse(TypedDict):
    Messages: list[MessageResponse]


class DeleteMessageBatchSuccessResponseEntry(TypedDict):
    Id: str

class DeleteMessageBatchFailedResponseEntry(TypedDict):
    Id: str
    Code: str
    Message: str
    SenderFault: bool

class DeleteMessageBatchResponse(TypedDict):
    Successful: list[DeleteMessageBatchSuccessResponseEntry]
    Failed: list[DeleteMessageBatchFailedResponseEntry]