"""High-level interface for AWS CloudWatch Logs operations."""
import logging
import time
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any

from botocore.exceptions import ClientError

from chainsaws.aws.cloudwatch._cloudwatch_internal import CloudWatchError, CloudWatchLogs
from chainsaws.aws.cloudwatch.cloudwatch_models import (
    CloudWatchAPIConfig,
    FilterPattern,
    GetLogsConfig,
    LogEvent,
    LogGroupConfig,
    LogStreamConfig,
    MetricFilter,
    PutLogsConfig,
    RetentionDays,
    SubscriptionFilter,
)
from chainsaws.aws.cloudwatch.logger import CloudWatchLogger
from chainsaws.aws.shared import session

logger = logging.getLogger(__name__)


class CloudWatchAPI:
    """High-level CloudWatch Logs API."""

    def __init__(
        self,
        config: CloudWatchAPIConfig | None = None,
    ) -> None:
        """Initialize CloudWatch Logs API.

        Args:
            config: Optional API configuration

        Example:
            ```python
            logs = CloudWatchAPI(
                config=CloudWatchAPIConfig(
                    region="ap-northeast-2",
                    max_retries=5
                )
            )
            ```

        """
        self.config = config or CloudWatchAPIConfig()
        self.boto3_session = session.get_boto_session(
            self.config.credentials
            if self.config.credentials else None,
        )
        self.logs = CloudWatchLogs(
            self.boto3_session,
            self.config.region,
        )

    # Log Group Operations
    def create_log_group(
        self,
        name: str,
        retention_days: RetentionDays | None = None,
        kms_key_id: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create a new log group.

        Args:
            name: Log group name
            retention_days: Optional retention period
            kms_key_id: Optional KMS key for encryption
            tags: Optional resource tags

        Returns:
            Created log group details

        Example:
            ```python
            group = logs.create_log_group(
                name="/aws/lambda/my-function",
                retention_days=RetentionDays.ONE_WEEK,
                tags={"Environment": "Production"}
            )
            ```

        """
        config = LogGroupConfig(
            log_group_name=name,
            retention_days=retention_days,
            kms_key_id=kms_key_id,
            tags=tags or {},
        )
        return self.logs.create_log_group(config)

    def create_log_stream(
        self,
        group_name: str,
        stream_name: str,
    ) -> dict[str, Any]:
        """Create a new log stream in a log group.

        Args:
            group_name: Log group name
            stream_name: Log stream name

        Returns:
            Created log stream details

        Example:
            ```python
            stream = logs.create_log_stream(
                group_name="/aws/lambda/my-function",
                stream_name="2024/03/15"
            )
            ```

        """
        config = LogStreamConfig(
            log_group_name=group_name,
            log_stream_name=stream_name,
        )
        return self.logs.create_log_stream(config)

    def describe_log_group(
        self,
        name: str,
    ) -> dict[str, Any]:
        """Get details of a log group.

        Args:
            name: Log group name

        Returns:
            Log group details

        Example:
            ```python
            group = logs.describe_log_group("/aws/lambda/my-function")
            print(f"Retention days: {group.get('retentionInDays')}")
            ```

        """
        return self.logs.describe_log_group(name)

    def describe_log_stream(
        self,
        group_name: str,
        stream_name: str,
    ) -> dict[str, Any]:
        """Get details of a log stream.

        Args:
            group_name: Log group name
            stream_name: Log stream name

        Returns:
            Log stream details

        Example:
            ```python
            stream = logs.describe_log_stream(
                group_name="/aws/lambda/my-function",
                stream_name="2024/03/15"
            )
            print(f"Last event: {stream.get('lastEventTimestamp')}")
            ```

        """
        return self.logs.describe_log_stream(group_name, stream_name)

    # Logging Operations
    def put_logs(
        self,
        group_name: str,
        stream_name: str,
        events: list[LogEvent],
        sequence_token: str | None = None,
    ) -> str:
        """Put log events to a log stream.

        Args:
            group_name: Log group name
            stream_name: Log stream name
            events: List of log events
            sequence_token: Optional sequence token for next batch

        Returns:
            Next sequence token

        Note:
            This method automatically handles AWS limitations:
            - Maximum batch size: 1MB
            - Maximum events per batch: 10,000
            - Maximum event size: 256KB
            - Time constraints:
              * Events must be within -14 days to +2 hours from now
              * Events must be within log group retention period
              * Events in a batch must span less than 24 hours

        Example:
            ```python
            events = [
                LogEvent(
                    timestamp=datetime.now(),
                    message="Process started",
                    level=LogLevel.INFO
                )
            ]
            next_token = logs.put_logs(
                group_name="/aws/lambda/my-function",
                stream_name="2024/03/15",
                events=events
            )
            ```

        """
        config = PutLogsConfig(
            log_group_name=group_name,
            log_stream_name=stream_name,
            events=events,
            sequence_token=sequence_token,
        )
        return self.logs.put_logs(config)

    def get_logs(
        self,
        group_name: str,
        stream_name: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int | None = None,
        next_token: str | None = None,
    ) -> Generator[LogEvent, None, None]:
        """Get log events from a log stream.

        Args:
            group_name: Log group name
            stream_name: Log stream name
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Optional maximum number of events
            next_token: Optional pagination token

        Yields:
            Log events

        Example:
            ```python
            for event in logs.get_logs(
                group_name="/aws/lambda/my-function",
                stream_name="2024/03/15",
                start_time=datetime.now() - timedelta(hours=1)
            ):
                print(f"{event.timestamp}: {event.message}")
            ```

        """
        config = GetLogsConfig(
            log_group_name=group_name,
            log_stream_name=stream_name,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            next_token=next_token,
        )
        yield from self.logs.get_logs(config)

    def search_logs(
        self,
        pattern: str,
        group_names: list[str],
        start_time: datetime | None = None,
        case_sensitive: bool = False,
        context_lines: int = 0,
    ) -> Generator[dict[str, Any], None, None]:
        """Search logs across multiple groups with context.

        Args:
            pattern: Search pattern
            group_names: List of log group names
            start_time: Optional start time
            case_sensitive: Case sensitive search
            context_lines: Number of context lines

        Example:
            ```python
            # Search for error messages with context
            results = logs.search_logs(
                pattern="DatabaseError",
                group_names=["/aws/lambda/my-function"],
                context_lines=2
            )
            for result in results:
                print(f"Found in {result['group']}:")
                for line in result['context']:
                    print(f"  {line}")
            ```

        """
        for group_name in group_names:
            events = list(self.get_logs(
                group_name=group_name,
                start_time=start_time,
                pattern=pattern if case_sensitive else f"(?i){pattern}",
            ))

            for i, event in enumerate(events):
                context = []
                start_idx = max(0, i - context_lines)
                context.extend(events[j].message for j in range(start_idx, i))

                context.append(f">>> {event.message}")

                end_idx = min(len(events), i + context_lines + 1)
                context.extend(
                    events[j].message for j in range(i + 1, end_idx))

                yield {
                    "group": group_name,
                    "timestamp": event.timestamp,
                    "message": event.message,
                    "context": context,
                }

    # Filtering & Metrics
    def create_metric_filter(
        self,
        name: str,
        group_name: str,
        pattern: str,
        metric_namespace: str,
        metric_name: str,
        metric_value: str,
        default_value: float | None = None,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a metric filter.

        Args:
            name: Filter name
            group_name: Log group name
            pattern: Filter pattern
            metric_namespace: CloudWatch metric namespace
            metric_name: CloudWatch metric name
            metric_value: Metric value expression
            default_value: Optional default value
            fields: Optional fields to extract

        Returns:
            Created metric filter details

        Example:
            ```python
            filter = logs.create_metric_filter(
                name="ErrorCount",
                group_name="/aws/lambda/my-function",
                pattern="[timestamp, level=ERROR, message]",
                metric_namespace="MyApp",
                metric_name="Errors",
                metric_value="1",
                fields=["timestamp", "message"]
            )
            ```

        """
        config = MetricFilter(
            filter_name=name,
            log_group_name=group_name,
            filter_pattern=FilterPattern(
                pattern=pattern,
                fields=fields or [],
            ),
            metric_namespace=metric_namespace,
            metric_name=metric_name,
            metric_value=metric_value,
            default_value=default_value,
        )
        return self.logs.create_metric_filter(config)

    def create_subscription_filter(
        self,
        name: str,
        group_name: str,
        pattern: str,
        destination_arn: str,
        role_arn: str | None = None,
        distribution: str | None = None,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a subscription filter.

        Args:
            name: Filter name
            group_name: Log group name
            pattern: Filter pattern
            destination_arn: Destination ARN (Lambda/Kinesis/Firehose)
            role_arn: Optional IAM role ARN
            distribution: Optional distribution option
            fields: Optional fields to extract

        Returns:
            Created subscription filter details

        Example:
            ```python
            filter = logs.create_subscription_filter(
                name="ErrorNotifier",
                group_name="/aws/lambda/my-function",
                pattern="[level=ERROR]",
                destination_arn="arn:aws:lambda:region:account:function:notifier",
                fields=["timestamp", "message"]
            )
            ```

        """
        config = SubscriptionFilter(
            filter_name=name,
            log_group_name=group_name,
            filter_pattern=FilterPattern(
                pattern=pattern,
                fields=fields or [],
            ),
            destination_arn=destination_arn,
            role_arn=role_arn,
            distribution=distribution,
        )
        return self.logs.create_subscription_filter(config)

    # Logger Interface
    def get_logger(
        self,
        name: str,
        tags: dict[str, str] | None = None,
    ) -> CloudWatchLogger:
        """Get a logger for the specified name.

        Args:
            name: Logger name (used as log group name)
            tags: Optional tags for log group

        Returns:
            CloudWatch logger instance

        Example:
            ```python
            logger = logs.get_logger("/my-app/production")
            logger.info("Application started")
            logger.error("Error occurred", exc_info=True)
            ```

        """
        return CloudWatchLogger(self, name, tags=tags)

    @contextmanager
    def batch_logger(
        self,
        group_name: str,
        stream_name: str | None = None,
        batch_size: int = 100,
        tags: dict[str, str] | None = None,
    ) -> Generator[CloudWatchLogger, None, None]:
        """Context manager for batch logging.

        Args:
            group_name: Log group name
            stream_name: Optional stream name
            batch_size: Maximum events per batch
            tags: Optional tags

        Yields:
            CloudWatch logger instance

        Example:
            ```python
            with logs.batch_logger("/my-app/production") as logger:
                logger.info("Batch process started")
                for item in items:
                    process_item(item)
                    logger.info(f"Processed item {item.id}")
                logger.info("Batch process completed")
            ```

        """
        logger = CloudWatchLogger(
            api=self,
            log_group=group_name,
            stream_name=stream_name,
            batch_size=batch_size,
            tags=tags,
        )
        try:
            yield logger
        finally:
            logger.flush()

    # Utility Methods

    def tail_logs(
        self,
        group_name: str,
        stream_name: str | None = None,
        filter_pattern: str | None = None,
        start_time: datetime | None = None,
        follow: bool = True,
        interval: float = 1.0,
    ) -> Generator[LogEvent, None, None]:
        """Tail log events in real-time.

        Args:
            group_name: Log group name
            stream_name: Optional specific stream name
            filter_pattern: Optional filter pattern
            start_time: Optional start time (default: 5 min ago)
            follow: Whether to follow logs in real-time
            interval: Polling interval in seconds

        Yields:
            Log events as they arrive

        Example:
            ```python
            # Tail all ERROR logs
            for event in logs.tail_logs(
                group_name="/aws/lambda/my-function",
                filter_pattern="[level=ERROR]"
            ):
                print(f"{event.timestamp}: {event.message}")
            ```

        """
        start = start_time or datetime.now() - timedelta(minutes=5)
        last_time = start

        try:
            while True:
                events = self.get_logs(
                    group_name=group_name,
                    stream_name=stream_name,
                    start_time=last_time,
                    filter_pattern=filter_pattern,
                )

                for event in events:
                    last_time = event.timestamp
                    yield event

                if not follow:
                    break

                time.sleep(interval)
        except KeyboardInterrupt:
            return

    def delete_old_streams(
        self,
        group_name: str,
        older_than_days: int = 30,
        dry_run: bool = True,
    ) -> list[str]:
        """Delete old log streams from a group.

        Args:
            group_name: Log group name
            older_than_days: Delete streams older than this
            dry_run: Only list streams without deleting

        Returns:
            List of deleted stream names

        Example:
            ```python
            # List old streams first
            old_streams = logs.delete_old_streams(
                group_name="/aws/lambda/my-function",
                older_than_days=60,
                dry_run=True
            )
            print(f"Found {len(old_streams)} old streams")

            # Actually delete them
            deleted = logs.delete_old_streams(
                group_name="/aws/lambda/my-function",
                older_than_days=60,
                dry_run=False
            )
            ```

        """
        cutoff = datetime.now() - timedelta(days=older_than_days)
        deleted_streams = []

        paginator = self.logs.logs_client.get_paginator("describe_log_streams")
        for page in paginator.paginate(logGroupName=group_name):
            for stream in page["logStreams"]:
                last_event = stream.get("lastEventTimestamp", 0)
                if last_event == 0:  # Empty stream
                    continue

                last_time = datetime.fromtimestamp(last_event / 1000)
                if last_time < cutoff:
                    deleted_streams.append(stream["logStreamName"])
                    if not dry_run:
                        self.logs.logs_client.delete_log_stream(
                            logGroupName=group_name,
                            logStreamName=stream["logStreamName"],
                        )

        return deleted_streams

    def export_logs(
        self,
        group_name: str,
        destination_bucket: str,
        prefix: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        wait: bool = True,
        timeout: int = 300,
    ) -> str:
        """Export logs to S3 bucket.

        Args:
            group_name: Log group name
            destination_bucket: S3 bucket name
            prefix: Optional S3 key prefix
            start_time: Optional start time
            end_time: Optional end time
            wait: Wait for export to complete
            timeout: Timeout in seconds when waiting

        Returns:
            Task ID of the export task

        Example:
            ```python
            # Export last 24 hours of logs
            task_id = logs.export_logs(
                group_name="/aws/lambda/my-function",
                destination_bucket="my-logs-bucket",
                prefix="lambda-logs/",
                start_time=datetime.now() - timedelta(days=1)
            )
            ```

        """
        params = {
            "logGroupName": group_name,
            "destination": destination_bucket,
            "from": int(start_time.timestamp() * 1000) if start_time else 0,
            "to": int(end_time.timestamp() * 1000) if end_time else int(time.time() * 1000),
        }

        if prefix:
            params["destinationPrefix"] = prefix

        response = self.logs.logs_client.create_export_task(**params)
        task_id = response["taskId"]

        if wait:
            start = time.time()
            while time.time() - start < timeout:
                response = self.logs.logs_client.describe_export_tasks(
                    taskId=task_id,
                )
                status = response["exportTasks"][0]["status"]["code"]
                if status == "COMPLETED":
                    break
                if status in ["FAILED", "CANCELLED"]:
                    msg = f"Export failed with status: {status}"
                    raise CloudWatchError(
                        msg)
                time.sleep(5)

        return task_id

    def get_log_insights_query_templates(self) -> dict[str, str]:
        """Get predefined CloudWatch Logs Insights query templates.

        Returns:
            Dictionary of query templates

        Example:
            ```python
            templates = logs.get_log_insights_query_templates()
            results = logs.query_logs(
                query_string=templates['lambda_performance'],
                log_group_names=["/aws/lambda/my-function"]
            )
            ```

        """
        return {
            "lambda_performance": """
                filter @type = "REPORT"
                | parse @message /Duration: (?<duration>.*?) ms/
                | parse @message /Memory Size: (?<memory>.*?) MB/
                | parse @message /Max Memory Used: (?<memory_used>.*?) MB/
                | stats
                    avg(duration) as avg_duration,
                    max(duration) as max_duration,
                    avg(memory_used / memory * 100) as memory_utilization
                by bin(5m)
                | sort @timestamp desc
            """,
            "api_gateway_latency": """
                filter @type = "END"
                | parse @message '"status": (?<status>[0-9]{3})'
                | stats
                    count(*) as requests,
                    count(status >= 500) as errors,
                    avg(duration) as avg_latency
                by status, bin(1m)
                | sort @timestamp desc
            """,
            "error_patterns": """
                filter level = "ERROR" or level = "CRITICAL"
                | parse @message "Error: *" as error_message
                | stats
                    count(*) as error_count,
                    earliest(@timestamp) as first_seen,
                    latest(@timestamp) as last_seen
                by error_message
                | sort error_count desc
                | limit 100
            """,
        }

    def setup_error_alerting(
        self,
        group_name: str,
        sns_topic_arn: str,
        error_threshold: int = 5,
        period_minutes: int = 5,
        include_patterns: list[str] | None = None,
    ) -> dict[str, Any]:
        """Setup error monitoring and alerting.

        Args:
            group_name: Log group name
            sns_topic_arn: SNS topic ARN for notifications
            error_threshold: Number of errors to trigger alert
            period_minutes: Time window in minutes
            include_patterns: Optional error patterns to match

        Example:
            ```python
            logs.setup_error_alerting(
                group_name="/aws/lambda/my-function",
                sns_topic_arn="arn:aws:sns:region:account:topic",
                error_threshold=10,
                include_patterns=["DatabaseError", "TimeoutError"]
            )
            ```

        """
        pattern = "ERROR" if not include_patterns else f"ERROR {
            ' '.join(include_patterns)}"

        # Create metric filter
        self.create_metric_filter(
            name=f"ErrorCount-{group_name.split('/')[-1]}",
            group_name=group_name,
            pattern=pattern,
            metric_namespace="ErrorMetrics",
            metric_name="ErrorCount",
            metric_value="1",
        )

        # Create CloudWatch alarm
        alarm_name = f"HighErrorRate-{group_name.split('/')[-1]}"
        self.logs.logs_client.put_metric_alarm(
            AlarmName=alarm_name,
            MetricName="ErrorCount",
            Namespace="ErrorMetrics",
            Period=period_minutes * 60,
            EvaluationPeriods=1,
            Threshold=error_threshold,
            ComparisonOperator="GreaterThanThreshold",
            AlarmActions=[sns_topic_arn],
        )

        return {"alarm_name": alarm_name}

    def create_lambda_subscription(
        self,
        group_name: str,
        lambda_function_arn: str,
        filter_pattern: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Setup Lambda subscription for log events."""
        from chainsaws.aws.lambda_client import LambdaAPI

        if not name:
            name = f"lambda-sub-{str(uuid.uuid4())[:8]}"

        try:
            lambda_api = LambdaAPI(self.config)
            try:
                lambda_api.add_permission(
                    function_name=lambda_function_arn,
                    statement_id=f"CloudWatchLogs-{name}",
                    action="lambda:InvokeFunction",
                    principal="logs.amazonaws.com",
                    source_arn=f"arn:aws:logs:{self.config.region}:{
                        self.config.account_id}"
                    f":log-group:{group_name}:*",
                )
            except Exception as e:
                if "ResourceConflictException" not in str(e):
                    raise

            return self.create_subscription_filter(
                name=name,
                group_name=group_name,
                pattern=filter_pattern or "",
                destination_arn=lambda_function_arn,
            )

        except Exception as e:
            logger.exception(f"Failed to setup Lambda subscription: {e!s}")
            msg = f"Lambda subscription setup failed: {e!s}"
            raise CloudWatchError(
                msg) from e

    def list_lambda_subscriptions(
        self,
        group_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """List Lambda subscriptions for log groups.

        Args:
            group_name: Optional specific log group name

        Returns:
            List of subscription details

        Example:
            ```python
            # List all Lambda subscriptions
            subscriptions = logs.list_lambda_subscriptions()
            for sub in subscriptions:
                print(f"Group: {sub['group_name']}")
                print(f"Lambda: {sub['lambda_function']}")
                print(f"Pattern: {sub['filter_pattern']}")
            ```

        """
        subscriptions = []
        paginator = self.logs.logs_client.get_paginator("describe_log_groups")

        params = {}
        if group_name:
            params["logGroupNamePrefix"] = group_name

        try:
            for page in paginator.paginate(**params):
                for group in page["logGroups"]:
                    group_name = group["logGroupName"]

                    response = self.logs.logs_client.describe_subscription_filters(
                        logGroupName=group_name,
                    )

                    for filter in response["subscriptionFilters"]:
                        if filter["destinationArn"].startswith("arn:aws:lambda:"):
                            subscriptions.append({
                                "name": filter["filterName"],
                                "group_name": group_name,
                                "lambda_function": filter["destinationArn"],
                                "filter_pattern": filter["filterPattern"],
                                "creation_time": filter["creationTime"],
                            })

            return subscriptions

        except ClientError as e:
            logger.exception(f"Failed to list Lambda subscriptions: {e!s}")
            msg = f"Failed to list subscriptions: {e!s}"
            raise CloudWatchError(
                msg) from e

    def delete_lambda_subscription(
        self,
        group_name: str,
        name: str,
        remove_permissions: bool = True,
    ) -> None:
        """Delete a Lambda subscription.

        Args:
            group_name: Log group name
            name: Subscription filter name
            remove_permissions: Whether to remove Lambda permissions

        Example:
            ```python
            logs.delete_lambda_subscription(
                group_name="/aws/lambda/my-function",
                name="ErrorProcessor",
                remove_permissions=True
            )
            ```

        """
        from chainsaws.aws.lambda_client.lambda_client import LambdaAPI

        try:
            response = self.logs.logs_client.describe_subscription_filters(
                logGroupName=group_name,
                filterNamePrefix=name,
            )

            if not response["subscriptionFilters"]:
                msg = f"Subscription {name} not found"
                raise CloudWatchError(msg)

            subscription = response["subscriptionFilters"][0]
            lambda_arn = subscription["destinationArn"]

            # Delete subscription filter
            self.logs.logs_client.delete_subscription_filter(
                logGroupName=group_name,
                filterName=name,
            )

            if remove_permissions:
                lambda_api = LambdaAPI(self.config)
                try:
                    lambda_api.remove_permission(
                        function_name=lambda_arn,
                        statement_id=f"CloudWatchLogs-{name}",
                    )
                except Exception as e:
                    if "ResourceNotFoundException" not in str(e):
                        logger.warning(
                            f"Failed to remove Lambda permissions: {e!s}")

        except Exception as e:
            logger.exception(f"Failed to delete Lambda subscription: {e!s}")
            msg = f"Subscription deletion failed: {e!s}"
            raise CloudWatchError(
                msg) from e
