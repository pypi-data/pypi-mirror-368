"""AWS EventBridge API wrapper.

This module provides a high-level API for AWS EventBridge operations.
It includes support for:
- Event bus management
- Event pattern creation
- Rule management
- Target configuration with builder pattern
- Input transformation
- Retry policies and DLQ configuration

Example:
    >>> from chainsaws.aws.eventbridge import EventBridgeAPI, TargetBuilder
    >>> eventbridge = EventBridgeAPI()
    >>> builder = TargetBuilder("ap-northeast-2", "123456789012")
    >>> target = (builder.lambda_function("my-function")
    ...     .with_input({"key": "value"})
    ...     .build())
"""

from chainsaws.aws.eventbridge.eventbridge import EventBridgeAPI
from chainsaws.aws.eventbridge.eventbridge_models import (
    DeadLetterConfig,
    EventBridgeAPIConfig,
    EventBusResponse,
    EventPattern,
    EventSource,
    InputTransformer,
    PutEventsRequestEntry,
    PutEventsResponse,
    PutTargetsResponse,
    RetryPolicy,
    Target,
    TargetBuilder,
)

__all__ = [
    # Main API
    "EventBridgeAPI",
    "EventBridgeAPIConfig",

    # Event related
    "EventPattern",
    "EventSource",
    "PutEventsRequestEntry",
    "PutEventsResponse",

    # Target related
    "Target",
    "TargetBuilder",
    "InputTransformer",
    "RetryPolicy",
    "DeadLetterConfig",

    # Response types
    "EventBusResponse",
    "PutTargetsResponse",
]
