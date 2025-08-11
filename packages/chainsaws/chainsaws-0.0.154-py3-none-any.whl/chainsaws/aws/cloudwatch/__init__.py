"""CloudWatch Logs API package.

This package provides a high-level interface for AWS CloudWatch Logs operations.

Example:
    ```python
    from chainsaws.aws.cloudwatch import CloudWatchAPI, LogLevel, RetentionDays

    # Initialize API
    logs = CloudWatchAPI()

    # Create log group with retention
    logs.create_log_group("/my-app/prod", retention_days=RetentionDays.ONE_MONTH)

    # Get logger interface
    logger = logs.get_logger("/my-app/prod")
    logger.info("Application started")
    logger.error("Error occurred")

    # Query logs
    from chainsaws.aws.cloudwatch import QueryBuilder
    query = (QueryBuilder(logs)
        .log_groups("/my-app/prod")
        .filter(level="ERROR")
        .time_range(start=datetime.now() - timedelta(hours=1))
        .execute())

    # Setup Lambda subscription
    logs.create_lambda_subscription(
        group_name="/my-app/prod",
        lambda_function_arn="arn:aws:lambda:region:account:function:processor",
        filter_pattern="[level=ERROR]"
    )
    ```

"""

from chainsaws.aws.cloudwatch.cloudwatch import CloudWatchAPI
from chainsaws.aws.cloudwatch.cloudwatch_models import (
    CloudWatchAPIConfig,
    FilterPattern,
    GetLogsConfig,
    LogEvent,
    LogGroupConfig,
    LogLevel,
    LogsInsightsQuery,
    LogStreamConfig,
    MetricFilter,
    PutLogsConfig,
    QueryResult,
    QuerySortBy,
    QueryStatus,
    RetentionDays,
    SubscriptionFilter,
)
from chainsaws.aws.cloudwatch.handler import CloudWatchHandler
from chainsaws.aws.cloudwatch.logger import CloudWatchLogger
from chainsaws.aws.cloudwatch.query import QueryBuilder

__all__ = [
    "CloudWatchAPI",
    "CloudWatchAPIConfig",
    "CloudWatchHandler",
    "CloudWatchLogger",
    "FilterPattern",
    "GetLogsConfig",
    "LogEvent",
    "LogGroupConfig",
    "LogLevel",
    "LogStreamConfig",
    "LogsInsightsQuery",
    "MetricFilter",
    "PutLogsConfig",
    "QueryBuilder",
    "QueryResult",
    "QuerySortBy",
    "QueryStatus",
    "RetentionDays",
    "SubscriptionFilter",
]

__version__ = "0.1.0"
