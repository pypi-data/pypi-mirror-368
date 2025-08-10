"""AWS SQS high-level client providing simplified interface for queue operations."""
import json
from typing import Any, Optional

from chainsaws.aws.shared import session
from chainsaws.aws.sqs._sqs_internal import SQS
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


class SQSAPI:
    """SQS high-level client."""

    def __init__(
        self,
        queue_url: str,
        config: Optional[SQSAPIConfig] = None,
    ) -> None:
        """Initialize SQS client.

        Args:
            queue_url: The URL of the Amazon SQS queue
            config: Optional SQS configuration

        """
        self.config = config or SQSAPIConfig()
        self.queue_url = queue_url
        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None,
        )
        self._sqs = SQS(
            boto3_session=self.boto3_session,
            config=config,
        )

    def send_message(
        self,
        message_body: str | dict[str, Any],
        delay_seconds: Optional[int] = None,
        message_attributes: Optional[MessageAttributes] = None,
        message_system_attributes: Optional[MessageSystemAttributes] = None,
        message_deduplication_id: Optional[str] = None,
        message_group_id: Optional[str] = None,
    ) -> SendMessageResponse:
        """Send a single message to the queue.

        Args:
            message_body: Message content (string or dict)
            delay_seconds: Optional delay for message visibility
            attributes: Optional message attributes
            deduplication_id: Optional deduplication ID (for FIFO queues)
            group_id: Optional group ID (for FIFO queues)

        """
        if isinstance(message_body, dict):
            message_body = json.dumps(message_body)

        return self._sqs.send_message(
            queue_url=self.queue_url,
            message_body=message_body,
            delay_seconds=delay_seconds,
            message_attributes=message_attributes,
            message_system_attributes=message_system_attributes,
            message_deduplication_id=message_deduplication_id,
            message_group_id=message_group_id,
        )

    def send_message_batch(
        self,
        entries: list[SendMessageBatchRequestEntry],
    ) -> SendMessageBatchResponse:  
        """Send multiple messages in a single request.

        Args:
            messages: List of messages (strings or dicts)
            delay_seconds: Optional delay for all messages

        """
        return self._sqs.send_message_batch(self.queue_url, entries)

    def receive_messages(
        self,
        message_attributes_names: Optional[list[str]] = None,
        message_sytstem_attributes_names: Optional[ReceiveMessageMessageSystemAttributeNames] = None,
        max_number_of_messages: Optional[int] = None,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: Optional[int] = None,
        receive_request_attempt_id: Optional[str] = None,
    ) -> ReceiveMessageResponse:
        """Receive messages from the queue.
        """
        return self._sqs.receive_message(
            queue_url=self.queue_url,
            message_attributes_names=message_attributes_names,
            message_sytstem_attributes_names=message_sytstem_attributes_names,
            max_number_of_messages=max_number_of_messages,
            visibility_timeout=visibility_timeout,
            wait_time_seconds=wait_time_seconds,
            receive_request_attempt_id=receive_request_attempt_id,
        )

    def delete_message(self, receipt_handle: str) -> None:
        """Delete a message from the queue.

        Args:
            receipt_handle: Receipt handle of the message to delete

        """
        self._sqs.delete_message(
            queue_url=self.queue_url,
            receipt_handle=receipt_handle,
        )

    def delete_message_batch(self, entries: list[DeleteMessageBatchRequestEntry]) -> DeleteMessageBatchResponse:
        """Delete multiple messages in a single request.

        Args:
            receipt_handles: List of receipt handles to delete

        """
        return self._sqs.delete_message_batch(
            queue_url=self.queue_url,
            entries=entries,
        )

    def purge_queue(self) -> None:
        """Delete all messages from the queue."""
        self._sqs.purge_queue(self.queue_url)