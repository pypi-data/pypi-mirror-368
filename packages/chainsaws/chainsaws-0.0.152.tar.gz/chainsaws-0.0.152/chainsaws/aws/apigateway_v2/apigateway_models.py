from enum import Enum
from typing import Any, Literal, Optional, TypedDict, Union
from dataclasses import dataclass, field
import datetime

from chainsaws.aws.shared.config import APIConfig


@dataclass
class APIGatewayV2APIConfig(APIConfig):
    """Configuration for API Gateway v2 API."""


class ProtocolType(str, Enum):
    """API Gateway v2 protocol types."""

    HTTP = "HTTP"
    WEBSOCKET = "WEBSOCKET"


class AuthorizationType(str, Enum):
    """API Gateway v2 authorization types."""

    NONE = "NONE"
    JWT = "JWT"
    AWS_IAM = "AWS_IAM"
    CUSTOM = "CUSTOM"


class IntegrationType(str, Enum):
    """API Gateway v2 integration types."""

    AWS_PROXY = "AWS_PROXY"  # For Lambda proxy
    HTTP_PROXY = "HTTP_PROXY"  # For HTTP proxy
    MOCK = "MOCK"  # For testing
    VPC_LINK = "VPC_LINK"  # For private integrations


class PayloadFormatVersion(str, Enum):
    """API Gateway v2 payload format versions."""

    VERSION_1_0 = "1.0"  # REST API compatibility
    VERSION_2_0 = "2.0"  # Optimized for HTTP APIs


@dataclass
class CorsConfig:
    """CORS configuration for HTTP APIs."""

    allow_origins: list[str]  # Allowed origins
    allow_methods: list[str]  # Allowed HTTP methods
    allow_headers: Optional[list[str]] = None  # Allowed headers
    expose_headers: Optional[list[str]] = None  # Exposed headers
    max_age: Optional[int] = None  # Max age in seconds
    allow_credentials: Optional[bool] = None  # Whether to allow credentials


@dataclass
class HttpApiConfig:
    """Configuration for creating an HTTP API."""

    name: str  # API name
    # Protocol type
    protocol_type: Literal[ProtocolType.HTTP] = ProtocolType.HTTP
    cors_configuration: Optional[CorsConfig] = None  # CORS configuration
    # Whether to disable the default endpoint
    disable_execute_api_endpoint: bool = False
    description: Optional[str] = None  # API description
    tags: Optional[dict[str, str]] = None  # Tags for the API


@dataclass
class WebSocketApiConfig:
    """Configuration for creating a WebSocket API."""

    name: str  # API name
    # Protocol type
    protocol_type: Literal[ProtocolType.WEBSOCKET] = ProtocolType.WEBSOCKET
    route_selection_expression: str = "$request.body.action"  # Route selection expression
    # API key selection expression
    api_key_selection_expression: Optional[str] = None
    description: Optional[str] = None  # API description
    tags: Optional[dict[str, str]] = None  # Tags for the API


@dataclass
class RouteConfig:
    """Configuration for API route."""

    route_key: str  # Route key (e.g., 'GET /items')
    target: str  # Integration target (e.g., Lambda ARN)
    authorization_type: AuthorizationType = AuthorizationType.NONE  # Authorization type
    # Authorizer ID if using custom authorizer
    authorizer_id: Optional[str] = None


@dataclass
class IntegrationConfig:
    """Configuration for v2 integration."""

    integration_type: IntegrationType  # Integration type
    integration_uri: Optional[str] = None  # Integration URI (e.g., Lambda ARN)
    integration_method: Optional[str] = None  # Integration HTTP method
    # Payload format version
    payload_format_version: PayloadFormatVersion = PayloadFormatVersion.VERSION_2_0
    timeout_in_millis: int = 30000  # Integration timeout in milliseconds
    credentials_arn: Optional[str] = None  # IAM role ARN for the integration
    request_parameters: Optional[dict[str, str]
                                 ] = None  # Request parameter mappings
    # Response parameter mappings
    response_parameters: Optional[dict[str, dict[str, str]]] = None
    # TLS configuration for integration
    tls_config: Optional[dict[str, Any]] = None
    connection_id: Optional[str] = None  # VPC link ID for private integration


class AuthorizerType(str, Enum):
    """API Gateway v2 authorizer types."""

    JWT = "JWT"
    LAMBDA = "REQUEST"  # REQUEST type for Lambda authorizer


@dataclass
class JwtConfig:
    """Configuration for JWT authorizer."""

    issuer: str  # JWT token issuer URL
    audiences: list[str]  # List of allowed audiences
    identity_source: list[str] = field(
        # Where to extract the token from
        default_factory=lambda: ["$request.header.Authorization"])


@dataclass
class LambdaAuthorizerConfig:
    """Configuration for Lambda authorizer."""

    function_arn: str  # Lambda function ARN
    identity_sources: list[str]  # Where to extract identity from
    result_ttl: int = 300  # Time to cache authorizer result
    enable_simple_responses: bool = True  # Whether to enable simple IAM responses
    payload_format_version: str = "2.0"  # Authorizer payload version


@dataclass
class VpcLinkConfig:
    """Configuration for VPC Link."""

    name: str  # VPC Link name
    subnet_ids: list[str]  # Subnet IDs for the VPC link
    security_group_ids: list[str]  # Security group IDs
    tags: Optional[dict[str, str]] = None  # Tags for VPC link


@dataclass
class WebSocketMessageConfig:
    """Configuration for WebSocket message."""

    connection_id: str  # WebSocket connection ID
    data: Union[str, dict[str, Any]]  # Message data to send

    def __post_init__(self) -> None:
        """Validate message data."""
        if not isinstance(self.data, (str, dict)):
            raise ValueError("Data must be either string or dictionary")


class CorsConfigurationResponse(TypedDict, total=False):
    """CORS configuration response."""

    AllowCredentials: bool
    AllowHeaders: list[str]
    AllowMethods: list[str]
    AllowOrigins: list[str]
    ExposeHeaders: list[str]
    MaxAge: int


class CreateApiResponse(TypedDict, total=False):
    """API Gateway v2 create_api response."""

    ApiEndpoint: str
    ApiGatewayManaged: bool
    ApiId: str
    ApiKeySelectionExpression: str
    CorsConfiguration: CorsConfigurationResponse
    CreatedDate: datetime
    Description: str
    DisableSchemaValidation: bool
    DisableExecuteApiEndpoint: bool
    ImportInfo: list[str]
    Name: str
    ProtocolType: Literal["WEBSOCKET", "HTTP"]
    RouteSelectionExpression: str
    Tags: dict[str, str]
    Version: str
    Warnings: list[str]


class IntegrationResponse(TypedDict, total=False):
    """Integration response."""

    ApiGatewayManaged: bool
    ConnectionId: str
    ConnectionType: str
    ContentHandlingStrategy: str
    CredentialsArn: str
    Description: str
    IntegrationId: str
    IntegrationMethod: str
    IntegrationResponseSelectionExpression: str
    IntegrationType: str
    IntegrationUri: str
    PassthroughBehavior: str
    PayloadFormatVersion: str
    RequestParameters: dict[str, str]
    RequestTemplates: dict[str, str]
    ResponseParameters: dict[str, dict[str, str]]
    TemplateSelectionExpression: str
    TimeoutInMillis: int
    TlsConfig: dict[str, Any]


class RouteResponse(TypedDict, total=False):
    """Route response."""

    ApiGatewayManaged: bool
    ApiKeyRequired: bool
    AuthorizationScopes: list[str]
    AuthorizationType: str
    AuthorizerId: str
    ModelSelectionExpression: str
    OperationName: str
    RequestModels: dict[str, str]
    RequestParameters: dict[str, dict[str, bool]]
    RouteId: str
    RouteKey: str
    RouteResponseSelectionExpression: str
    Target: str


class StageResponse(TypedDict, total=False):
    """Stage response."""

    AccessLogSettings: dict[str, str]
    ApiGatewayManaged: bool
    AutoDeploy: bool
    ClientCertificateId: str
    CreatedDate: datetime
    DefaultRouteSettings: dict[str, Any]
    DeploymentId: str
    Description: str
    LastDeploymentStatusMessage: str
    LastUpdatedDate: datetime
    RouteSettings: dict[str, Any]
    StageName: str
    StageVariables: dict[str, str]
    Tags: dict[str, str]


class AuthorizerResponse(TypedDict, total=False):
    """Authorizer response."""

    AuthorizerId: str
    AuthorizerCredentialsArn: str
    AuthorizerPayloadFormatVersion: str
    AuthorizerResultTtlInSeconds: int
    AuthorizerType: str
    AuthorizerUri: str
    EnableSimpleResponses: bool
    IdentitySource: list[str]
    IdentityValidationExpression: str
    JwtConfiguration: dict[str, Any]
    Name: str


class VpcLinkResponse(TypedDict, total=False):
    """VPC Link response."""

    CreatedDate: datetime
    Name: str
    SecurityGroupIds: list[str]
    SubnetIds: list[str]
    Tags: dict[str, str]
    VpcLinkId: str
    VpcLinkStatus: str
    VpcLinkStatusMessage: str
    VpcLinkVersion: str
