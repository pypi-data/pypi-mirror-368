"""AWS Lambda handler utilities for request/response handling and error management.

Provides structured request parsing and response formatting with error handling.
"""

import traceback
from collections.abc import Callable
from functools import wraps
from typing import Any, Optional
from http import HTTPStatus
import logging

from chainsaws.utils.error_utils.error_utils import make_error_description
from chainsaws.aws.lambda_client.event_handler.handler_models import (
    HandlerConfig,
    LambdaEvent,
    LambdaResponse,
)
from chainsaws.aws.lambda_client.event_handler.exceptions import (
    AppError,
    HTTPException,
)

logger = logging.getLogger(__name__)


def aws_lambda_handler(
    error_receiver: Optional[Callable[[str], Any]] = None,
    content_type: str = "application/json",
    use_traceback: bool = True,
    ignore_error_codes: Optional[list[int | str]] = None,
) -> Callable:
    """Decorator for AWS Lambda handlers with error handling and response formatting.

    Args:
        error_receiver: Callback function for error notifications
        content_type: Response content type
        use_traceback: Include traceback in error responses
        ignore_error_codes: List of error codes (HTTP status codes or AppError codes) to ignore for notifications

    Example:
        @aws_lambda_handler(
            error_receiver=notify_slack,
            ignore_error_codes=[404, "USER_NOT_FOUND"]  # HTTP status codes or AppError codes
        )
        def handler(event, context):
            body = LambdaEvent.parse_obj(event).get_json_body()
            return {"message": "Success"}
    """
    config = HandlerConfig(
        error_receiver=error_receiver,
        content_type=content_type,
        use_traceback=use_traceback,
        ignore_error_codes=ignore_error_codes or [],
    )

    def should_notify_error(error_code: int | str) -> bool:
        """Check if error should trigger notification."""
        return error_code not in config.ignore_error_codes

    def decorator(func: Callable[..., Any]) -> Callable[..., dict]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> dict:
            event = args[0] if args else {}

            # API Gateway를 통한 호출인지 확인
            is_api_gateway = LambdaEvent.is_api_gateway_event(event)

            try:
                result = func(*args, **kwargs) or {}

                # Return if it is already in LambdaResponse format
                if isinstance(result, dict) and LambdaResponse.is_lambda_response(response=result):
                    return result

                return LambdaResponse.create(
                    body=result,
                    status_code=HTTPStatus.OK,
                    content_type=config.content_type,
                    serialize=is_api_gateway
                )

            except HTTPException as ex:
                # Handle HTTP exceptions (including AppError)
                error_info = {
                    "type": ex.__class__.__name__,
                    "status_code": ex.status_code,
                    "headers": ex.headers
                }

                if isinstance(ex, AppError):
                    error_info["code"] = ex.code
                    error_info["type"] = "AppError"

                error_body = {
                    "error": error_info,
                    "detail": ex.detail,
                }

                if config.use_traceback:
                    error_body["traceback"] = str(traceback.format_exc())

                # Notify based on error code
                if config.error_receiver:
                    error_code = ex.code if isinstance(
                        ex, AppError) else ex.status_code
                    if should_notify_error(error_code):
                        try:
                            message = make_error_description(event)
                            config.error_receiver(message)
                        except Exception as err:
                            error_body["error_receiver_failed"] = str(err)

                return LambdaResponse.create(
                    error_body,
                    status_code=ex.status_code,
                    headers=ex.headers,
                    content_type=config.content_type,
                    serialize=is_api_gateway
                )

            except Exception as ex:
                error_body = {
                    "detail": str(ex),
                }

                # AWS 서비스 에러 처리
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                if hasattr(ex, "response"):
                    # Boto3/AWS SDK 에러
                    error_info = getattr(ex, "response", {})
                    error_body.update({
                        "service_error": {
                            "code": error_info.get("Error", {}).get("Code"),
                            "message": error_info.get("Error", {}).get("Message"),
                            "request_id": error_info.get("ResponseMetadata", {}).get("RequestId"),
                            "http_status": error_info.get("ResponseMetadata", {}).get("HTTPStatusCode")
                        }
                    })
                    aws_status = error_info.get(
                        "ResponseMetadata", {}).get("HTTPStatusCode")
                    if aws_status:
                        status_code = aws_status

                if config.use_traceback:
                    error_body["traceback"] = str(traceback.format_exc())

                # Notify based on status code
                if config.error_receiver and should_notify_error(status_code):
                    try:
                        message = make_error_description(event)
                        config.error_receiver(message)
                    except Exception as err:
                        error_body["error_receiver_failed"] = str(err)

                return LambdaResponse.create(
                    body=error_body,
                    status_code=status_code,
                    content_type=config.content_type,
                    serialize=is_api_gateway
                )

        return wrapper
    return decorator


def get_event_data(event: dict[str, Any]) -> LambdaEvent:
    """Get event data."""
    return LambdaEvent.from_dict(event)


def get_body(event: dict[str, Any]) -> dict[str, Any] | None:
    """Get JSON body from event."""
    return get_event_data(event).get_json_body()


def get_headers(event: dict[str, Any]) -> dict[str, str]:
    """Get request headers."""
    return get_event_data(event).headers


def get_source_ip(event: dict[str, Any]) -> str | None:
    """Get source IP address from event."""
    return get_event_data(event).requestContext.get_source_ip()
