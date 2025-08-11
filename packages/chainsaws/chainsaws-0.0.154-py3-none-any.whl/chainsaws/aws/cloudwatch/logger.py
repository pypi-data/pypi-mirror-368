from datetime import datetime

from chainsaws.aws.cloudwatch.cloudwatch import CloudWatchAPI
from chainsaws.aws.cloudwatch.cloudwatch_models import LogEvent, LogLevel


class CloudWatchLogger:
    """Logger-style interface for CloudWatch Logs."""

    def __init__(
        self,
        api: CloudWatchAPI,
        log_group: str,
        stream_name: str | None = None,
        batch_size: int = 100,
        flush_interval: float = 5.0,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Initialize CloudWatch Logger.

        Args:
            api: CloudWatch API instance
            log_group: Log group name
            stream_name: Optional stream name (default: YYYY/MM/DD)
            batch_size: Maximum events to batch (default: 100)
            flush_interval: Seconds between auto-flush (default: 5.0)
            tags: Optional tags for log group

        """
        self.api = api
        self.log_group = log_group
        self._stream_name = stream_name
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._event_buffer = []
        self._last_flush = datetime.now()
        self._sequence_token = None

        # Ensure log group exists
        try:
            self.api.create_log_group(name=log_group, tags=tags)
        except Exception:
            pass  # Group already exists

    @property
    def stream_name(self) -> str:
        """Get current log stream name."""
        if not self._stream_name:
            self._stream_name = datetime.now().strftime("%Y/%m/%d")
            try:
                self.api.create_log_stream(
                    group_name=self.log_group,
                    stream_name=self._stream_name,
                )
            except Exception:
                pass  # Stream already exists
        return self._stream_name

    def _log(self, message: str, level: LogLevel) -> None:
        """Add log event to buffer."""
        event = LogEvent(
            timestamp=datetime.now(),
            message=message,
            level=level,
        )
        self._event_buffer.append(event)

        # Auto-flush if needed
        if (len(self._event_buffer) >= self.batch_size or
                (datetime.now() - self._last_flush).total_seconds() >= self.flush_interval):
            self.flush()

    def debug(self, message: str) -> None:
        """Log debug message."""
        self._log(message, LogLevel.DEBUG)

    def info(self, message: str) -> None:
        """Log info message."""
        self._log(message, LogLevel.INFO)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self._log(message, LogLevel.WARN)

    def error(self, message: str) -> None:
        """Log error message."""
        self._log(message, LogLevel.ERROR)

    def critical(self, message: str) -> None:
        """Log critical message."""
        self._log(message, LogLevel.CRITICAL)

    def flush(self) -> None:
        """Flush buffered events to CloudWatch."""
        if not self._event_buffer:
            return

        try:
            self._sequence_token = self.api.put_logs(
                group_name=self.log_group,
                stream_name=self.stream_name,
                events=self._event_buffer,
                sequence_token=self._sequence_token,
            )
            self._event_buffer.clear()
            self._last_flush = datetime.now()
        except Exception as e:
            # Log locally if CloudWatch fails
            import logging
            logging.exception(f"Failed to flush logs to CloudWatch: {e!s}")
