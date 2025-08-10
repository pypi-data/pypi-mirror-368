import logging
import boto3
from typing import Optional
from chainsaws.aws.sqs.sqs_models import (
    SQSAPIConfig,
)
from chainsaws.aws.sqs.request.MessageRequest import (
  MessageAttributes,
  MessageSystemAttributes,
  SendMessageBatchRequestEntry,
  ReceiveMessageMessageSystemAttributeNames,
  DeleteMessageBatchRequestEntry,
)
from chainsaws.aws.sqs.response.MessageResponse import (
    SendMessageResponse,
    SendMessageBatchResponse,
    ReceiveMessageResponse,
    DeleteMessageBatchResponse,
)

logger = logging.getLogger(__name__)


class SQS:
    def __init__(
        self,
        boto3_session: boto3.Session,
        config: Optional[SQSAPIConfig] = None,
    ) -> None:
        self.config = config or SQSAPIConfig()
        self.client = boto3_session.client("sqs", region_name=self.config.region)

    def send_message(
        self,
        queue_url: str,
        message_body: str,
        delay_seconds: Optional[int] = None,
        message_attributes: Optional[MessageAttributes] = None,
        message_system_attributes: Optional[MessageSystemAttributes] = None,
        message_deduplication_id: Optional[str] = None,
        message_group_id: Optional[str] = None,
    ) -> SendMessageResponse:
        """Send a single message to the queue."""
        params = {
            "QueueUrl": queue_url,
            "MessageBody": message_body,
        }

        if delay_seconds:
            params["DelaySeconds"] = delay_seconds
        if message_attributes:
            params["MessageAttributes"] = message_attributes
        if message_system_attributes:
            params["MessageSystemAttributes"] = message_system_attributes
        if message_deduplication_id:
            params["MessageDeduplicationId"] = message_deduplication_id
        if message_group_id:
            params["MessageGroupId"] = message_group_id

        return self.client.send_message(**params)
       

    def send_message_batch(
        self,
        queue_url: str,
        entries: list[SendMessageBatchRequestEntry],
    ) -> SendMessageBatchResponse:
        params = {
            "QueueUrl": queue_url,
            "Entries": entries,
        }
        return self.client.send_message_batch(**params)

    def receive_message(
        self,
        queue_url: str,
        message_attributes_names: Optional[list[str]] = None,
        message_sytstem_attributes_names: Optional[ReceiveMessageMessageSystemAttributeNames] = None,
        max_number_of_messages: Optional[int] = None,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: Optional[int] = None,
        receive_request_attempt_id: Optional[str] = None,
    ) -> ReceiveMessageResponse:
        params = {
            "QueueUrl": queue_url,
        }
        if message_attributes_names:
            params["MessageSystemAttributeNames"] = message_attributes_names
        if message_sytstem_attributes_names:
            params["MessageSystemAttributeNames"] = message_sytstem_attributes_names
        if max_number_of_messages:
            params["MaxNumberOfMessages"] = max_number_of_messages
        if visibility_timeout:
            params["VisibilityTimeout"] = visibility_timeout
        if wait_time_seconds:
            params["WaitTimeSeconds"] = wait_time_seconds
        if receive_request_attempt_id:
            params["ReceiveRequestAttemptId"] = receive_request_attempt_id

        return self.client.receive_message(**params)

    def delete_message(
        self,
        queue_url: str,
        receipt_handle: str,
    ) -> None:
        params = {
            "QueueUrl": queue_url,
            "ReceiptHandle": receipt_handle,
        }

        return self.client.delete_message(**params)

    def delete_message_batch(
        self,
        queue_url: str,
        entries: list[DeleteMessageBatchRequestEntry],
    ) -> DeleteMessageBatchResponse:
        params = {
            "QueueUrl": queue_url,
            "Entries": entries,
        }
        return self.client.delete_message_batch(**params)

    def purge_queue(self, queue_url: str) -> None:
        """Delete all messages from the queue."""
        self.client.purge_queue(QueueUrl=queue_url)

