"""Event handler package for AWS Lambda functions.

Provides utilities for handling various AWS Lambda event sources.
"""

from chainsaws.aws.lambda_client.event_handler.api_gateway import (
    APIGatewayRestResolver,
    APIGatewayHttpResolver,
    HttpMethod,
    Route,
    BaseResolver,
    Router,
)
from chainsaws.aws.lambda_client.event_handler.handler_models import (
    LambdaEvent,
    LambdaResponse,
    HandlerConfig,
)
from chainsaws.aws.lambda_client.event_handler.event_handler import aws_lambda_handler
from chainsaws.aws.lambda_client.event_handler.alb_resolver import (
    ALBEvent,
    ALBResolver,
)
from chainsaws.aws.lambda_client.event_handler.websocket import (
    WebSocketResolver,
    WebSocketRoute,
    WebSocketConnectEvent,
    WebSocketRouteEvent,
    WebSocketEventType,
)
from chainsaws.aws.lambda_client.event_handler.websocket_connection import (
    APIGatewayWSConnectionManager,
)
from chainsaws.aws.lambda_client.event_handler.websocket_models import (
    WebSocketConnection,
    WebSocketGroup,
)
from chainsaws.aws.lambda_client.event_handler.openapi_generator import (
    OpenAPIConfigDict,
    OpenAPIGenerator,
    ResponseSchemaRegistry,
    response_model,
    response,
    create_schema_from_type,
    IS_BUILD_TIME,
)
from chainsaws.aws.lambda_client.event_handler.dependency_injection import (
    Depends,
    Container,
    container,
    inject,
)
from chainsaws.aws.lambda_client.event_handler.exceptions import (
    HTTPException,
    AppError,
)

__all__ = [
    "aws_lambda_handler",
    "APIGatewayRestResolver",
    "APIGatewayHttpResolver",
    "HttpMethod",
    "Route",
    "BaseResolver",
    "Router",
    "LambdaEvent",
    "LambdaResponse",
    "HandlerConfig",
    "ALBEvent",
    "ALBResolver",
    "WebSocketResolver",
    "WebSocketRoute",
    "WebSocketConnectEvent",
    "WebSocketRouteEvent",
    "WebSocketEventType",
    "APIGatewayWSConnectionManager",
    "WebSocketConnection",
    "WebSocketGroup",
    # OpenAPI related
    "OpenAPIConfigDict",
    "OpenAPIGenerator",
    "ResponseSchemaRegistry",
    "response_model",
    "response",
    "create_schema_from_type",
    "IS_BUILD_TIME",
    # Dependency Injection
    "Depends",
    "Container",
    "container",
    "inject",
    'HTTPException',
    'AppError',
]
