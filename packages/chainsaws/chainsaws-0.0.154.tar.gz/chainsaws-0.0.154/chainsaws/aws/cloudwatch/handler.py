import logging
from datetime import datetime

from chainsaws.aws.cloudwatch.cloudwatch import CloudWatchAPI
from chainsaws.aws.cloudwatch.cloudwatch_models import LogEvent, LogLevel
from chainsaws.aws.cloudwatch.logger import CloudWatchLogger


class CloudWatchHandler(logging.Handler):
    """Python logging handler that sends logs to CloudWatch Logs.

    Example:
        ```python
        import logging
        from chainsaws.aws.cloudwatch import CloudWatchHandler, CloudWatchAPI

        # Setup handler
        handler = CloudWatchHandler(
            api=CloudWatchAPI(),
            log_group="/my-app/prod",
            stream_name="app.log",  # Optional
            batch_size=100,  # Optional
            flush_interval=5.0,  # Optional
            tags={"Environment": "Production"}  # Optional
        )

        # Add to logger
        logger = logging.getLogger("my_app")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        # Use logger
        logger.info("Application started")
        logger.error("An error occurred", exc_info=True)
        ```

    """

    def __init__(
        self,
        api: CloudWatchAPI,
        log_group: str,
        stream_name: str | None = None,
        batch_size: int = 100,
        flush_interval: float = 5.0,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Initialize CloudWatch handler.

        Args:
            api: CloudWatch API instance
            log_group: Log group name
            stream_name: Optional stream name (default: YYYY/MM/DD)
            batch_size: Maximum events to batch (default: 100)
            flush_interval: Seconds between auto-flush (default: 5.0)
            tags: Optional tags for log group

        """
        super().__init__()
        self.logger = CloudWatchLogger(
            api=api,
            log_group=log_group,
            stream_name=stream_name,
            batch_size=batch_size,
            flush_interval=flush_interval,
            tags=tags,
        )

    def _get_level(self, record: logging.LogRecord) -> LogLevel:
        """Convert Python logging level to CloudWatch level."""
        if record.levelno >= logging.CRITICAL:
            return LogLevel.CRITICAL
        if record.levelno >= logging.ERROR:
            return LogLevel.ERROR
        if record.levelno >= logging.WARNING:
            return LogLevel.WARN
        if record.levelno >= logging.INFO:
            return LogLevel.INFO
        return LogLevel.DEBUG

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record.

        Args:
            record: logging.LogRecord instance

        """
        try:
            # Format message
            msg = self.format(record)

            # Add exception info if available
            if record.exc_info:
                if not record.exc_text:
                    record.exc_text = self.formatter.formatException(
                        record.exc_info)
                if record.exc_text:
                    msg = f"{msg}\n{record.exc_text}"

            # Add stack info if available
            if record.stack_info:
                msg = f"{msg}\n{self.formatter.formatStack(record.stack_info)}"

            # Create log event
            event = LogEvent(
                timestamp=datetime.fromtimestamp(record.created),
                message=msg,
                level=self._get_level(record),
            )

            # Add to buffer
            self.logger._event_buffer.append(event)

            # Check if we need to flush
            if len(self.logger._event_buffer) >= self.logger.batch_size:
                self.flush()

        except Exception:
            self.handleError(record)

    def flush(self) -> None:
        """Flush the buffer."""
        self.logger.flush()

    def close(self) -> None:
        """Close the handler."""
        self.flush()
        super().close()
