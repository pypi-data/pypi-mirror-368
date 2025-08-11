import json
import logging
from time import sleep
from typing import Any, Optional

from chainsaws.aws.firehose._firehose_internal import Firehose
from chainsaws.aws.firehose.firehose_models import (
    FirehoseAPIConfig,
)
from chainsaws.aws.firehose.response.RecordResponse import PutRecordBatchResponse, PutRecordResponse
from chainsaws.aws.shared.session import get_boto_session

logger = logging.getLogger(__name__)


class FirehoseAPI:
    """High-level Kinesis Firehose operations."""

    def __init__(
        self,
        delivery_stream_name: str,
        config: Optional[FirehoseAPIConfig] = None,
    ) -> None:
        self.config = config or FirehoseAPIConfig()
        self.delivery_stream_name = delivery_stream_name
        self.boto3_session = get_boto_session(
            self.config.credentials if self.config.credentials else None,
        )
        self.firehose = Firehose(boto3_session=self.boto3_session, config=self.config)


    def put_record(self, data: str | bytes | dict | list) -> PutRecordResponse:
        """Put record into delivery stream."""
        if isinstance(data, dict | list):
            data = json.dumps(data)

        return self.firehose.put_record(
            stream_name=self.delivery_stream_name,
            data=data,
        )

    def put_record_batch(
        self,
        records: list[str | bytes | dict | list],
        batch_size: int = 500,
        retry_failed: bool = True,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Put multiple records into delivery stream with automatic batching.

        Args:
            records: List of records to put (strings, bytes, or JSON-serializable objects)
            batch_size: Maximum size of each batch (default: 500, max: 500)
            retry_failed: Whether to retry failed records (default: True)
            max_retries: Maximum number of retries for failed records (default: 3)

        Returns:
            Dict containing:
                - total_records: Total number of records processed
                - successful_records: Number of successfully delivered records
                - failed_records: List of failed records with their error messages
                - batch_responses: List of raw responses from each batch operation

        Example:
            >>> records = [{"id": i, "message": f"Test {i}"} for i in range(1000)]
            >>> result = firehose.put_record_batch(records)
            >>> print(f"Successfully delivered {result['successful_records']} records")

        """
        if batch_size > 500:
            msg = "Maximum batch size is 500 records"
            raise ValueError(msg)

        prepared_records = [
            json.dumps(record) if isinstance(record, dict | list) else record
            for record in records
        ]

        total_records = len(prepared_records)
        successful_records = 0
        failed_records = []
        batch_responses: list[PutRecordBatchResponse] = []

        for attempt in range(max_retries):
            if not prepared_records:
                break

            current_batch_records = []

            for i in range(0, len(prepared_records), batch_size):
                batch = prepared_records[i:i + batch_size]

                try:
                    response = self.firehose.put_record_batch(
                        stream_name=self.delivery_stream_name,
                        records=batch,
                    )
                    batch_responses.append(response)

                    # Process results
                    failed_count = response.get("FailedPutCount", 0)
                    if failed_count > 0:
                        # Collect failed records for retry
                        request_responses = response.get(
                            "RequestResponses", [])
                        for idx, resp in enumerate(request_responses):
                            if "ErrorCode" in resp:
                                failed_records.append({
                                    "record": batch[idx],
                                    "error": resp.get("ErrorMessage", "Unknown error"),
                                    "attempt": attempt + 1,
                                })
                                current_batch_records.append(batch[idx])
                            else:
                                successful_records += 1
                    else:
                        successful_records += len(batch)

                except Exception as ex:
                    logger.exception(f"Batch processing failed: {ex!s}")
                    current_batch_records.extend(batch)
                    failed_records.extend([{
                        "record": record,
                        "error": str(ex),
                        "attempt": attempt + 1,
                    } for record in batch])

            # Update records for next retry attempt
            if retry_failed and current_batch_records:
                prepared_records = current_batch_records
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Retrying {len(prepared_records)} failed records. "
                        f"Attempt {attempt + 2}/{max_retries}",
                    )
                    # Exponential backoff
                    sleep(2 ** attempt)
            else:
                break

        result = batch_responses

        # Log final status
        if failed_records:
            logger.warning(
                f"Completed with {len(failed_records)} failed records out of {
                    total_records}",
            )
        else:
            logger.info(f"Successfully delivered all {total_records} records")

        return result