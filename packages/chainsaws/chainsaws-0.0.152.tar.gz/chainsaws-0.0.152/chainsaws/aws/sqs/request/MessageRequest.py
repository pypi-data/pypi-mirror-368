from typing import Literal, TypedDict, List
from chainsaws.aws.sqs.sqs_models import MessageAttributesValue

MessageAttributes = dict[str, MessageAttributesValue]
MessageSystemAttributes = dict[str, MessageAttributesValue]

class SendMessageBatchRequestEntry(TypedDict):
  Id: str
  MessageBody: str
  DelaySeconds: int
  MessageAttributes: MessageAttributes
  MessageSystemAttributes: MessageSystemAttributes
  MessageDeduplicationId: str
  MessageGroupId: str

ReceiveMessageMessageSystemAttributeNames = List[
  Literal[
    'All',
    'SenderId',
    'SentTimestamp',
    'ApproximateReceiveCount',
    'ApproximateFirstReceiveTimestamp',
    'SequenceNumber',
    'MessageDeduplicationId',
    'MessageGroupId',
    'AWSTraceHeader',
    'DeadLetterQueueSourceArn'
  ]
]

class DeleteMessageBatchRequestEntry(TypedDict):
  Id: str
  ReceiptHandle: str