import functools
import json
import logging
import random
import sys
import time
import traceback
from typing import Any, Callable, Optional, Literal, TypedDict, Annotated, Dict

from chainsaws.aws.lambda_client.types import Context as LambdaContext

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

LambdaHandler = Callable[[Dict[str, Any], LambdaContext], Any]


class LogExtra(TypedDict, total=False):
    """Type for extra fields in log records."""
    cold_start: bool
    correlation_id: str
    function_name: str
    function_version: str
    function_arn: str
    memory_limit: int
    aws_request_id: str
    log_group: str
    log_stream: str
    event: dict
    response: Any
    duration_ms: int
    error: str


JsonPath = str  # Type alias for JSON path strings like "headers.x-correlation-id"
SampleRate = Annotated[float, "Value between 0.0 and 1.0"]


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(
        self,
        service: str,
        **kwargs: Any,
    ) -> None:
        """Initialize formatter.

        Args:
            service: Service name
            **kwargs: Additional fields to include in logs
        """
        super().__init__()
        self.service = service
        self.additional_fields = kwargs

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record

        Returns:
            JSON formatted log string
        """
        # Base log fields
        log_dict = {
            "level": record.levelname,
            "message": record.getMessage(),
            "service": self.service,
            "timestamp": int(record.created * 1000),  # milliseconds
            "logger": record.name,
        }

        # Add location info
        if record.pathname and record.lineno:
            log_dict["location"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info if present
        if record.exc_info:
            log_dict["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "stacktrace": traceback.format_exception(*record.exc_info),
            }

        # Add additional fields
        log_dict.update(self.additional_fields)

        # Add extra fields from record
        if hasattr(record, "extra"):
            log_dict.update(record.extra)

        return json.dumps(log_dict)


class Logger:
    """Lambda logger with structured logging and context injection."""

    # Keep track of cold starts
    _cold_start = True

    def __init__(
        self,
        service: str,
        level: LogLevel = "INFO",
        sample_rate: SampleRate = 1.0,
        **kwargs: Any,
    ) -> None:
        """Initialize logger.

        Args:
            service: Service name
            level: Log level (one of "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
            sample_rate: Sampling rate for debug logs (0.0 to 1.0)
            **kwargs: Additional fields to include in logs

        Raises:
            ValueError: If sample_rate is not between 0.0 and 1.0
        """
        if not 0.0 <= sample_rate <= 1.0:
            raise ValueError("sample_rate must be between 0.0 and 1.0")

        self.service = service
        self.sample_rate = sample_rate
        self.logger = logging.getLogger(service)

        # Set log level
        self.logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        self.logger.handlers.clear()

        # Add JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter(service, **kwargs))
        self.logger.addHandler(handler)

    def inject_lambda_context(
        self,
        correlation_id_path: Optional[JsonPath] = None,
    ) -> Callable[[LambdaHandler], LambdaHandler]:
        """Inject Lambda context into logs.

        Args:
            correlation_id_path: JSON path to correlation ID in event (e.g. "headers.x-correlation-id")

        Example:
            ```python
            logger = Logger(service="my-service")

            @logger.inject_lambda_context(
                correlation_id_path="headers.x-correlation-id"
            )
            def handler(event, context):
                logger.info("Processing event")
                return {"statusCode": 200}
            ```
        """
        def decorator(handler: LambdaHandler) -> LambdaHandler:
            @functools.wraps(handler)
            def wrapper(event: dict, context: LambdaContext) -> Any:
                # Add Lambda context
                extra = {
                    "function_name": context.function_name,
                    "function_version": context.function_version,
                    "function_arn": context.invoked_function_arn,
                    "memory_limit": context.memory_limit_in_mb,
                    "aws_request_id": context.aws_request_id,
                    "log_group": context.log_group_name,
                    "log_stream": context.log_stream_name,
                }

                # Add cold start indicator
                if Logger._cold_start:
                    extra["cold_start"] = True
                    Logger._cold_start = False

                # Extract correlation ID if path provided
                if correlation_id_path:
                    correlation_id = self._extract_correlation_id(
                        event, correlation_id_path)
                    if correlation_id:
                        extra["correlation_id"] = correlation_id

                # Create child logger with context
                child_logger = self.logger.getChild(context.aws_request_id)
                child_logger.extra = extra

                # Replace logger for this invocation
                self.logger = child_logger

                # Log invocation
                start_time = time.time()
                self.info("Lambda invocation started", extra={
                    "event": event,
                })

                try:
                    response = handler(event, context)
                    duration_ms = int((time.time() - start_time) * 1000)
                    self.info("Lambda invocation completed", extra={
                        "duration_ms": duration_ms,
                        "response": response,
                    })
                    return response
                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)
                    self.error("Lambda invocation failed", exc_info=True, extra={
                        "duration_ms": duration_ms,
                        "error": str(e),
                    })
                    raise

            return wrapper
        return decorator

    def _extract_correlation_id(
        self, event: dict, path: str
    ) -> Optional[str]:
        """Extract correlation ID from event using JSON path.

        Args:
            event: Lambda event
            path: JSON path to correlation ID

        Returns:
            Correlation ID if found
        """
        try:
            value = event
            for key in path.split("."):
                value = value[key]
            return str(value)
        except (KeyError, TypeError):
            return None

    def debug(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log debug message with sampling.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        if self.sample_rate < 1.0:
            if random.random() > self.sample_rate:
                return
        self.logger.debug(msg, *args, extra=extra, **kwargs)

    def info(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log info message.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        self.logger.info(msg, *args, extra=extra, **kwargs)

    def warning(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log warning message.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        self.logger.warning(msg, *args, extra=extra, **kwargs)

    def error(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log error message.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        self.logger.error(msg, *args, extra=extra, **kwargs)

    def critical(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log critical message.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        self.logger.critical(msg, *args, extra=extra, **kwargs)

    def exception(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log exception message.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        kwargs["exc_info"] = True
        self.logger.exception(msg, *args, extra=extra, **kwargs)
