"""Internal implementation of CloudWatch Logs operations."""
import logging
import sys
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Any

from boto3.session import Session
from botocore.exceptions import ClientError

from chainsaws.aws.cloudwatch.cloudwatch_models import (
    GetLogsConfig,
    LogEvent,
    LogGroupConfig,
    LogStreamConfig,
    MetricFilter,
    PutLogsConfig,
    SubscriptionFilter,
)

logger = logging.getLogger(__name__)


class CloudWatchError(Exception):
    """Base exception for CloudWatch operations."""


class CloudWatchLogs:
    """Internal CloudWatch Logs implementation."""

    def __init__(
        self,
        boto3_session: Session,
        region: str,
    ) -> None:
        """Initialize CloudWatch Logs client."""
        self.logs_client = boto3_session.client("logs", region_name=region)

    def _handle_client_error(
        self,
        error: ClientError,
        operation: str,
    ) -> None:
        """Handle boto3 client errors."""
        logger.error(f"Failed to {operation}: {error!s}")
        msg = f"CloudWatch operation failed: {error!s}"
        raise CloudWatchError(msg)

    def _validate_event_time(
        self,
        event: LogEvent,
        past_limit: datetime,
        future_limit: datetime,
    ) -> bool:
        """Validate event timestamp."""
        return past_limit <= event.timestamp <= future_limit

    def _calculate_event_size(self, event: LogEvent) -> int:
        """Calculate size of event in bytes."""
        message = f"[{event.level.value}] {event.message}"
        return sys.getsizeof(message.encode("utf-8")) + 26

    def _should_start_new_batch(
        self,
        event: LogEvent,
        batch_start_time: datetime,
        current_size: int,
        current_batch_size: int,
        event_size: int,
    ) -> bool:
        """Check if a new batch should be started."""
        return (
            event.timestamp - batch_start_time > timedelta(hours=24) or
            current_size + event_size > 1_048_576 or
            current_batch_size >= 10_000
        )

    def _validate_and_split_events(
        self,
        events: list[LogEvent],
        log_group_retention: int | None,
    ) -> list[list[LogEvent]]:
        """Validate and split events into valid batches."""
        if not events:
            return []

        # Time validation
        now = datetime.now(UTC)
        future_limit = now + timedelta(hours=2)
        past_limit = now - timedelta(days=14)
        if log_group_retention:
            retention_limit = now - timedelta(days=log_group_retention)
            past_limit = max(past_limit, retention_limit)

        # Sort and filter valid events
        valid_events = sorted(
            [
                event for event in events
                if self._validate_event_time(event, past_limit, future_limit)
            ],
            key=lambda x: x.timestamp,
        )

        if not valid_events:
            msg = "No valid events within time constraints"
            raise CloudWatchError(msg)

        # Split into batches
        batches = []
        current_batch = []
        current_size = 0
        batch_start_time = valid_events[0].timestamp

        for event in valid_events:
            event_size = self._calculate_event_size(event)

            if event_size > 256 * 1024:
                logger.warning("Skipping event: size exceeds 256KB limit")
                continue

            if self._should_start_new_batch(
                event,
                batch_start_time,
                current_size,
                len(current_batch),
                event_size,
            ) and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_size = 0
                batch_start_time = event.timestamp

            current_batch.append(event)
            current_size += event_size

        if current_batch:
            batches.append(current_batch)

        return batches

    def _format_log_events(
        self,
        events: list[LogEvent],
    ) -> list[dict[str, Any]]:
        """Format events for AWS API."""
        return [
            {
                "timestamp": int(event.timestamp.timestamp() * 1000),
                "message": f"[{event.level.value}] {event.message}",
            }
            for event in events
        ]

    def create_log_group(self, config: LogGroupConfig) -> dict[str, Any]:
        """Create a new log group."""
        try:
            params = {"logGroupName": config.log_group_name}
            if config.kms_key_id:
                params["kmsKeyId"] = config.kms_key_id
            if config.tags:
                params["tags"] = config.tags

            self.logs_client.create_log_group(**params)

            if config.retention_days:
                self.logs_client.put_retention_policy(
                    logGroupName=config.log_group_name,
                    retentionInDays=config.retention_days.value,
                )

            return self.describe_log_group(config.log_group_name)
        except ClientError as e:
            self._handle_client_error(e, "create log group")

    def create_log_stream(self, config: LogStreamConfig) -> dict[str, Any]:
        """Create a new log stream."""
        try:
            self.logs_client.create_log_stream(
                logGroupName=config.log_group_name,
                logStreamName=config.log_stream_name,
            )
            return self.describe_log_stream(
                config.log_group_name,
                config.log_stream_name,
            )
        except ClientError as e:
            self._handle_client_error(e, "create log stream")

    def put_logs(self, config: PutLogsConfig) -> str:
        """Put log events to a log stream with batching."""
        try:
            # Get retention policy
            retention_days = None
            try:
                log_group = self.describe_log_group(config.log_group_name)
                retention_days = log_group.get("retentionInDays")
            except CloudWatchError:
                pass

            # Process events
            batches = self._validate_and_split_events(
                config.events,
                retention_days,
            )

            if not batches:
                msg = "No valid events to send"
                raise CloudWatchError(msg)

            # Send batches
            sequence_token = config.sequence_token
            for batch in batches:
                sequence_token = self._put_log_batch(
                    config.log_group_name,
                    config.log_stream_name,
                    batch,
                    sequence_token,
                )

            return sequence_token
        except Exception:
            logger.exception("Failed to put log events")
            raise

    def _put_log_batch(
        self,
        group_name: str,
        stream_name: str,
        events: list[LogEvent],
        sequence_token: str | None,
    ) -> str:
        """Put a single batch of log events."""
        params = {
            "logGroupName": group_name,
            "logStreamName": stream_name,
            "logEvents": self._format_log_events(events),
        }

        if sequence_token:
            params["sequenceToken"] = sequence_token

        try:
            response = self.logs_client.put_log_events(**params)
            return response.get("nextSequenceToken", "")
        except ClientError as e:
            if e.response["Error"]["Code"] == "InvalidSequenceTokenException":
                sequence_token = e.response["Error"]["Message"].split()[-1]
                params["sequenceToken"] = sequence_token
                response = self.logs_client.put_log_events(**params)
                return response.get("nextSequenceToken", "")
            raise

    def get_logs(
        self,
        config: GetLogsConfig,
    ) -> Generator[LogEvent, None, None]:
        """Get log events from a log stream."""
        try:
            params = {
                "logGroupName": config.log_group_name,
                "logStreamName": config.log_stream_name,
                "startFromHead": True,
            }

            if config.start_time:
                params["startTime"] = int(config.start_time.timestamp() * 1000)
            if config.end_time:
                params["endTime"] = int(config.end_time.timestamp() * 1000)
            if config.limit:
                params["limit"] = config.limit
            if config.next_token:
                params["nextToken"] = config.next_token

            while True:
                response = self.logs_client.get_log_events(**params)
                for event in response["events"]:
                    yield LogEvent(
                        timestamp=datetime.fromtimestamp(
                            event["timestamp"] / 1000,
                            tz=UTC,
                        ),
                        message=event["message"],
                    )

                next_token = response.get("nextForwardToken")
                if not next_token or next_token == params.get("nextToken"):
                    break
                params["nextToken"] = next_token
        except ClientError as e:
            self._handle_client_error(e, "get log events")

    def create_metric_filter(self, config: MetricFilter) -> dict[str, Any]:
        """Create a metric filter."""
        try:
            return self.logs_client.put_metric_filter(
                logGroupName=config.log_group_name,
                filterName=config.filter_name,
                filterPattern=config.filter_pattern.pattern,
                metricTransformations=[{
                    "metricName": config.metric_name,
                    "metricNamespace": config.metric_namespace,
                    "metricValue": config.metric_value,
                    "defaultValue": config.default_value,
                }],
            )
        except ClientError as e:
            self._handle_client_error(e, "create metric filter")

    def create_subscription_filter(
        self,
        config: SubscriptionFilter,
    ) -> dict[str, Any]:
        """Create a subscription filter."""
        try:
            params = {
                "logGroupName": config.log_group_name,
                "filterName": config.filter_name,
                "filterPattern": config.filter_pattern.pattern,
                "destinationArn": config.destination_arn,
            }

            if config.role_arn:
                params["roleArn"] = config.role_arn
            if config.distribution:
                params["distribution"] = config.distribution

            return self.logs_client.put_subscription_filter(**params)
        except ClientError as e:
            self._handle_client_error(e, "create subscription filter")

    def describe_log_group(self, log_group_name: str) -> dict[str, Any]:
        """Get log group details."""
        try:
            response = self.logs_client.describe_log_groups(
                logGroupNamePrefix=log_group_name,
                limit=1,
            )
            for group in response["logGroups"]:
                if group["logGroupName"] == log_group_name:
                    return group
            msg = f"Log group {log_group_name} not found"
            raise CloudWatchError(msg)
        except ClientError as e:
            self._handle_client_error(e, "describe log group")

    def describe_log_stream(
        self,
        log_group_name: str,
        log_stream_name: str,
    ) -> dict[str, Any]:
        """Get log stream details."""
        try:
            response = self.logs_client.describe_log_streams(
                logGroupName=log_group_name,
                logStreamNamePrefix=log_stream_name,
                limit=1,
            )
            for stream in response["logStreams"]:
                if stream["logStreamName"] == log_stream_name:
                    return stream
            msg = f"Log stream {log_stream_name} not found in {log_group_name}"
            raise CloudWatchError(
                msg)
        except ClientError as e:
            self._handle_client_error(e, "describe log stream")
