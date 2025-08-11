from typing import Any, Optional

from chainsaws.aws.apigateway_v1._apigateway_internal import APIGateway
from chainsaws.aws.apigateway_v1.apigateway_models import (
    APIGatewayAPIConfig,
    IntegrationConfig,
    IntegrationType,
    MethodConfig,
    ResourceConfig,
    RestAPIConfig,
)
from chainsaws.aws.shared import session


class APIGatewayAPI:
    """High-level API Gateway operations."""

    def __init__(self, config: Optional[APIGatewayAPIConfig] = None) -> None:
        """Initialize API Gateway API.

        Args:
            config: Optional API Gateway configuration
        """
        self.config = config or APIGatewayAPIConfig()
        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None
        )
        self.api_gateway = APIGateway(self.boto3_session, config=self.config)

    def create_rest_api(
        self,
        name: str,
        description: Optional[str] = None,
        endpoint_type: str = "REGIONAL",
        api_key_required: bool = False,
        binary_media_types: Optional[list[str]] = None,
        minimum_compression_size: Optional[int] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a new REST API.

        Args:
            name: Name of the API
            description: API description
            endpoint_type: Endpoint type (EDGE, REGIONAL, PRIVATE)
            api_key_required: Whether API key is required
            binary_media_types: List of binary media types
            minimum_compression_size: Minimum size for compression
            tags: Tags for the API

        Returns:
            API details including ID
        """
        config = RestAPIConfig(
            name=name,
            description=description,
            endpoint_type=endpoint_type,
            api_key_required=api_key_required,
            binary_media_types=binary_media_types,
            minimum_compression_size=minimum_compression_size,
            tags=tags,
        )
        return self.api_gateway.create_rest_api(config)

    def create_resource(
        self,
        api_id: str,
        path_part: str,
        parent_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new resource.

        Args:
            api_id: API identifier
            path_part: Resource path segment
            parent_id: Parent resource ID (None for root)

        Returns:
            Created resource details
        """
        config = ResourceConfig(
            path_part=path_part,
            parent_id=parent_id,
        )
        return self.api_gateway.create_resource(api_id, config)

    def create_method(
        self,
        api_id: str,
        resource_id: str,
        http_method: str,
        authorization_type: str = "NONE",
        api_key_required: bool = False,
        request_parameters: Optional[dict[str, bool]] = None,
        request_models: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a method on a resource.

        Args:
            api_id: API identifier
            resource_id: Resource identifier
            http_method: HTTP method
            authorization_type: Authorization type
            api_key_required: Whether API key is required
            request_parameters: Required request parameters
            request_models: Request models for content types

        Returns:
            Method details
        """
        config = MethodConfig(
            http_method=http_method,
            authorization_type=authorization_type,
            api_key_required=api_key_required,
            request_parameters=request_parameters,
            request_models=request_models,
        )
        return self.api_gateway.put_method(api_id, resource_id, config)

    def create_lambda_integration(
        self,
        api_id: str,
        resource_id: str,
        http_method: str,
        lambda_arn: str,
        role_arn: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a Lambda proxy integration.

        Args:
            api_id: API identifier
            resource_id: Resource identifier
            http_method: HTTP method
            lambda_arn: Lambda function ARN
            role_arn: Optional IAM role ARN for integration

        Returns:
            Integration details
        """
        config = IntegrationConfig(
            type=IntegrationType.AWS_PROXY,
            uri=f"arn:aws:apigateway:{
                self.config.region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations",
            integration_http_method="POST",
            credentials=role_arn,
        )
        return self.api_gateway.put_integration(
            api_id, resource_id, http_method, config)

    def create_http_integration(
        self,
        api_id: str,
        resource_id: str,
        http_method: str,
        endpoint_url: str,
        proxy: bool = True,
    ) -> dict[str, Any]:
        """Create an HTTP integration.

        Args:
            api_id: API identifier
            resource_id: Resource identifier
            http_method: HTTP method
            endpoint_url: HTTP endpoint URL
            proxy: Whether to use HTTP_PROXY integration

        Returns:
            Integration details
        """
        config = IntegrationConfig(
            type=IntegrationType.HTTP_PROXY if proxy else IntegrationType.HTTP,
            uri=endpoint_url,
            integration_http_method=http_method,
        )
        return self.api_gateway.put_integration(
            api_id, resource_id, http_method, config)

    def deploy_api(
        self,
        api_id: str,
        stage_name: str,
        stage_description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Deploy the API to a stage.

        Args:
            api_id: API identifier
            stage_name: Stage name to deploy to
            stage_description: Optional stage description

        Returns:
            Deployment details
        """
        return self.api_gateway.create_deployment(
            api_id, stage_name, stage_description)

    def get_resources(self, api_id: str) -> list[dict[str, Any]]:
        """Get all resources for an API.

        Args:
            api_id: API identifier

        Returns:
            List of resources
        """
        return self.api_gateway.get_resources(api_id)
