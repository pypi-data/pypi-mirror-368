"""AWS Lambda client for managing Lambda functions and providing structured logging.

This module provides:
1. Lambda Management:
   - Function creation and configuration
   - Function invocation and trigger management
   - Runtime and code management

2. Structured Logging:
   - JSON formatted logs
   - Lambda context injection
   - Correlation ID tracking
   - Cold start detection
   - Debug sampling

3. Event Handling:
   - API Gateway (REST/HTTP) event handling
   - ALB event handling
   - Request/Response formatting
   - Error handling with status codes
   - WebSocket connection management

4. API Documentation:
   - Automatic OpenAPI spec generation
   - Type-safe response models
   - Memory-efficient schema handling
   - S3-based schema storage
   - ReDoc UI integration

5. Dependency Injection:
   - FastAPI-style dependency system
   - Lambda context optimization
   - Singleton management
   - Request-scoped dependencies
   - Testing support
"""

from chainsaws.aws.lambda_client.lambda_client import LambdaAPI
from chainsaws.aws.lambda_client.lambda_models import (
    CreateFunctionRequest,
    FunctionCode,
    FunctionConfiguration,
    InvocationType,
    LambdaAPIConfig,
    LambdaHandler,
    PythonRuntime,
    TriggerType,
)
from chainsaws.aws.lambda_client.logger import (
    Logger,
    LogLevel,
    LogExtra,
    JsonPath,
    SampleRate,
)
from chainsaws.aws.lambda_client.types import Event, Context
from chainsaws.aws.lambda_client.event_handler import (
    aws_lambda_handler,
    APIGatewayRestResolver,
    APIGatewayHttpResolver,
    HttpMethod,
    Route,
    BaseResolver,
    Router,
    WebSocketResolver,
    WebSocketRoute,
    WebSocketConnectEvent,
    WebSocketRouteEvent,
    WebSocketEventType,
    LambdaEvent,
    LambdaResponse,
    HandlerConfig,
    ALBEvent,
    ALBResolver,
    APIGatewayWSConnectionManager,
    WebSocketConnection,
    WebSocketGroup,
    # OpenAPI related
    OpenAPIConfigDict,
    OpenAPIGenerator,
    ResponseSchemaRegistry,
    response_model,
    response,
    create_schema_from_type,
    IS_BUILD_TIME,
    # Dependency Injection
    Depends,
    Container,
    container,
    inject,
    HTTPException,
    AppError
)

__all__ = [
    # Lambda Management
    "CreateFunctionRequest",
    "FunctionCode",
    "FunctionConfiguration",
    "InvocationType",
    "LambdaAPI",
    "LambdaAPIConfig",
    "LambdaHandler",
    "PythonRuntime",
    "TriggerType",
    "Event",
    "Context",

    # Structured Logging
    "Logger",
    "LogLevel",
    "LogExtra",
    "JsonPath",
    "SampleRate",

    # Event Handling
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

    # OpenAPI Documentation
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

    # Exceptions
    "HTTPException",
    "AppError",
]
