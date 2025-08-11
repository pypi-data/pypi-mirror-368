from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from chainsaws.aws.shared.config import APIConfig


@dataclass
class APIGatewayAPIConfig(APIConfig):
    """Configuration for API Gateway API."""


class EndpointType(str, Enum):
    """API Gateway endpoint types."""

    EDGE = "EDGE"
    REGIONAL = "REGIONAL"
    PRIVATE = "PRIVATE"


class IntegrationType(str, Enum):
    """API Gateway integration types."""

    AWS = "AWS"  # For AWS services
    AWS_PROXY = "AWS_PROXY"  # For Lambda proxy
    HTTP = "HTTP"  # For HTTP endpoints
    HTTP_PROXY = "HTTP_PROXY"  # For HTTP proxy
    MOCK = "MOCK"  # For testing


class HttpMethod(str, Enum):
    """HTTP methods supported by API Gateway."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    ANY = "ANY"


@dataclass
class RestAPIConfig:
    """Configuration for creating a REST API."""

    name: str  # API name
    description: Optional[str] = None  # API description
    endpoint_type: EndpointType = field(
        default=EndpointType.REGIONAL)  # API endpoint type
    api_key_required: bool = False  # Whether API key is required
    # List of binary media types
    binary_media_types: Optional[list[str]] = None
    # Minimum size in bytes for compression
    minimum_compression_size: Optional[int] = None
    tags: Optional[dict[str, str]] = None  # Tags for the API

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.minimum_compression_size is not None:
            if not 0 <= self.minimum_compression_size <= 10485760:  # 10MB
                raise ValueError(
                    "minimum_compression_size must be between 0 and 10485760 bytes")


@dataclass
class ResourceConfig:
    """Configuration for API Gateway resource."""

    path_part: str  # Resource path segment
    parent_id: Optional[str] = None  # Parent resource ID (None for root)


@dataclass
class MethodConfig:
    """Configuration for API Gateway method."""

    http_method: HttpMethod
    authorization_type: str = "NONE"  # Authorization type
    api_key_required: bool = False  # Whether API key is required
    request_parameters: Optional[dict[str, bool]
                                 ] = None  # Required request parameters
    # Request models for content types
    request_models: Optional[dict[str, str]] = None


@dataclass
class IntegrationConfig:
    """Configuration for API Gateway integration."""

    type: IntegrationType
    uri: Optional[str] = None  # Integration endpoint URI
    # HTTP method for integration
    integration_http_method: Optional[str] = None
    credentials: Optional[str] = None  # IAM role ARN for integration
    # Integration request parameters
    request_parameters: Optional[dict[str, str]] = None
    # Integration request templates
    request_templates: Optional[dict[str, str]] = None
    # How to handle unmapped content types
    passthrough_behavior: Optional[str] = None
    cache_namespace: Optional[str] = None  # Integration cache namespace

    # Integration cache key parameters
    cache_key_parameters: Optional[list[str]] = None
    content_handling: Optional[str] = None  # How to handle response payload
    # Integration timeout in milliseconds
    timeout_in_millis: Optional[int] = None
