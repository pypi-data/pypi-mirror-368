"""Application Load Balancer event resolver."""

from typing import Any, Dict, Optional, Union

from chainsaws.aws.lambda_client.types import Event
from chainsaws.aws.lambda_client.types.events import ALBEvent
from chainsaws.aws.lambda_client.event_handler.handler_models import LambdaResponse

import base64


class ALBResolver:
    """Resolver for Application Load Balancer events."""

    def __init__(self) -> None:
        """Initialize ALB resolver."""
        pass

    def format_response(
        self,
        status_code: int,
        body: Union[str, dict, list],
        headers: Optional[Dict[str, str]] = None,
        status_description: Optional[str] = None,
        is_base64_encoded: bool = False,
    ) -> dict:
        """Format response for ALB.

        Args:
            status_code: HTTP status code
            body: Response body (string or JSON-serializable object)
            headers: Response headers
            status_description: Optional status description (e.g. "200 OK")
            is_base64_encoded: Whether the body is base64 encoded

        Returns:
            Formatted ALB response
        """
        return LambdaResponse.create(
            body=body,
            status_code=status_code,
            headers=headers,
            status_description=status_description,
            is_base64_encoded=is_base64_encoded,
            serialize=True
        )

    def get_query_parameter(
        self, event: ALBEvent, name: str, default: Any = None
    ) -> Any:
        """Get query parameter from event.

        Args:
            event: ALB event
            name: Parameter name
            default: Default value if parameter not found

        Returns:
            Parameter value or default
        """
        params = event.get("queryStringParameters", {})
        if not params:
            return default
        return params.get(name, default)

    def get_header(
        self, event: ALBEvent, name: str, default: Any = None
    ) -> Any:
        """Get header from event.

        Args:
            event: ALB event
            name: Header name
            default: Default value if header not found

        Returns:
            Header value or default
        """
        headers = event.get("headers", {})
        # Headers are case-insensitive
        name = name.lower()
        for key, value in headers.items():
            if key.lower() == name:
                return value
        return default

    def get_body(self, event: ALBEvent) -> Optional[str]:
        """Get request body from event.

        Args:
            event: ALB event

        Returns:
            Request body or None
        """
        body = event.get("body")
        if not body:
            return None

        if event.get("isBase64Encoded", False):
            body = base64.b64decode(body).decode("utf-8")

        return body

    def get_json_body(self, event: ALBEvent) -> Optional[Dict[str, Any]]:
        """Get JSON body from event.

        Args:
            event: ALB event

        Returns:
            Parsed JSON body or None
        """
        import json

        body = self.get_body(event)
        if not body:
            return None

        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def is_alb_event(self, event: Event) -> bool:
        """Check if event is an ALB event.

        Args:
            event: Lambda event

        Returns:
            True if event is an ALB event
        """
        return (
            isinstance(event, dict)
            and "requestContext" in event
            and "elb" in event.get("requestContext", {})
        ) 