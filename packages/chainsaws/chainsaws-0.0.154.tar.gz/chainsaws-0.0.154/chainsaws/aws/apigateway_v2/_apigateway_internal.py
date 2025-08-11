import json
import logging
from typing import Any, Optional, Union

import boto3
from botocore.exceptions import ClientError

from chainsaws.aws.apigateway_v2.apigateway_models import (
    APIGatewayV2APIConfig,
    AuthorizerType,
    CreateApiResponse,
    HttpApiConfig,
    IntegrationConfig,
    JwtConfig,
    LambdaAuthorizerConfig,
    RouteConfig,
    VpcLinkConfig,
    WebSocketApiConfig,
    WebSocketMessageConfig,
)

logger = logging.getLogger(__name__)


class APIGatewayV2:
    """Internal implementation of API Gateway v2 operations."""

    def __init__(
        self,
        session: boto3.Session,
        config: Optional[APIGatewayV2APIConfig] = None,
    ) -> None:
        self.session = session
        self.config = config or APIGatewayV2APIConfig()
        self.client = self.session.client("apigatewayv2")

    def create_api(
        self, config: Union[HttpApiConfig, WebSocketApiConfig]
    ) -> CreateApiResponse:
        """Create a new HTTP or WebSocket API.

        Args:
            config: API configuration

        Returns:
            API details including ID
        """
        try:
            kwargs = {
                "Name": config.name,
                "ProtocolType": config.protocol_type,
            }

            if config.description:
                kwargs["Description"] = config.description
            if config.tags:
                kwargs["Tags"] = config.tags

            if isinstance(config, HttpApiConfig):
                if config.cors_configuration:
                    kwargs["CorsConfiguration"] = {
                        "AllowOrigins": config.cors_configuration.allow_origins,
                        "AllowMethods": config.cors_configuration.allow_methods,
                    }
                    if config.cors_configuration.allow_headers:
                        kwargs["CorsConfiguration"]["AllowHeaders"] = config.cors_configuration.allow_headers
                    if config.cors_configuration.expose_headers:
                        kwargs["CorsConfiguration"]["ExposeHeaders"] = config.cors_configuration.expose_headers
                    if config.cors_configuration.max_age is not None:
                        kwargs["CorsConfiguration"]["MaxAge"] = config.cors_configuration.max_age
                    if config.cors_configuration.allow_credentials is not None:
                        kwargs["CorsConfiguration"]["AllowCredentials"] = config.cors_configuration.allow_credentials

                kwargs["DisableExecuteApiEndpoint"] = config.disable_execute_api_endpoint

            elif isinstance(config, WebSocketApiConfig):
                kwargs["RouteSelectionExpression"] = config.route_selection_expression
                if config.api_key_selection_expression:
                    kwargs["ApiKeySelectionExpression"] = config.api_key_selection_expression

            response = self.client.create_api(**kwargs)
            logger.info(f"Created API: {response['Name']} ({response['ApiId']})")
            return response
        except ClientError as e:
            logger.error(f"Failed to create API: {str(e)}")
            raise

    def create_route(self, api_id: str, config: RouteConfig) -> dict[str, Any]:
        """Create a new route.

        Args:
            api_id: API identifier
            config: Route configuration

        Returns:
            Route details
        """
        try:
            kwargs = {
                "ApiId": api_id,
                "RouteKey": config.route_key,
                "Target": f"integrations/{config.target}",
                "AuthorizationType": config.authorization_type,
            }

            if config.authorizer_id:
                kwargs["AuthorizerId"] = config.authorizer_id

            response = self.client.create_route(**kwargs)
            logger.info(
                f"Created route: {config.route_key} for API {api_id}")
            return response
        except ClientError as e:
            logger.error(f"Failed to create route: {str(e)}")
            raise

    def create_integration(
        self, api_id: str, config: IntegrationConfig
    ) -> dict[str, Any]:
        """Create an integration.

        Args:
            api_id: API identifier
            config: Integration configuration

        Returns:
            Integration details
        """
        try:
            kwargs = {
                "ApiId": api_id,
                "IntegrationType": config.integration_type,
                "PayloadFormatVersion": config.payload_format_version,
                "TimeoutInMillis": config.timeout_in_millis,
            }

            if config.integration_uri:
                kwargs["IntegrationUri"] = config.integration_uri
            if config.integration_method:
                kwargs["IntegrationMethod"] = config.integration_method
            if config.credentials_arn:
                kwargs["CredentialsArn"] = config.credentials_arn
            if config.request_parameters:
                kwargs["RequestParameters"] = config.request_parameters
            if config.response_parameters:
                kwargs["ResponseParameters"] = config.response_parameters
            if config.tls_config:
                kwargs["TlsConfig"] = config.tls_config
            if config.connection_id:
                kwargs["ConnectionId"] = config.connection_id

            response = self.client.create_integration(**kwargs)
            logger.info(f"Created integration for API {api_id}")
            return response
        except ClientError as e:
            logger.error(f"Failed to create integration: {str(e)}")
            raise

    def create_stage(
        self,
        api_id: str,
        stage_name: str,
        auto_deploy: bool = True,
        description: Optional[str] = None,
        stage_variables: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a stage.

        Args:
            api_id: API identifier
            stage_name: Stage name
            auto_deploy: Whether to automatically deploy changes
            description: Stage description
            stage_variables: Stage variables

        Returns:
            Stage details
        """
        try:
            kwargs = {
                "ApiId": api_id,
                "StageName": stage_name,
                "AutoDeploy": auto_deploy,
            }

            if description:
                kwargs["Description"] = description
            if stage_variables:
                kwargs["StageVariables"] = stage_variables

            response = self.client.create_stage(**kwargs)
            logger.info(f"Created stage: {stage_name} for API {api_id}")
            return response
        except ClientError as e:
            logger.error(f"Failed to create stage: {str(e)}")
            raise

    def create_jwt_authorizer(
        self, api_id: str, name: str, config: JwtConfig
    ) -> dict[str, Any]:
        """Create a JWT authorizer.

        Args:
            api_id: API identifier
            name: Authorizer name
            config: JWT configuration

        Returns:
            Authorizer details
        """
        try:
            response = self.client.create_authorizer(
                ApiId=api_id,
                AuthorizerType=AuthorizerType.JWT,
                IdentitySource=config.identity_source,
                JwtConfiguration={
                    "Issuer": config.issuer,
                    "Audience": config.audiences,
                },
                Name=name,
            )
            logger.info(f"Created JWT authorizer: {name} for API {api_id}")
            return response
        except ClientError as e:
            logger.error(f"Failed to create JWT authorizer: {str(e)}")
            raise

    def create_lambda_authorizer(
        self, api_id: str, name: str, config: LambdaAuthorizerConfig
    ) -> dict[str, Any]:
        """Create a Lambda authorizer.

        Args:
            api_id: API identifier
            name: Authorizer name
            config: Lambda authorizer configuration

        Returns:
            Authorizer details
        """
        try:
            response = self.client.create_authorizer(
                ApiId=api_id,
                AuthorizerType=AuthorizerType.LAMBDA,
                AuthorizerUri=config.function_arn,
                AuthorizerPayloadFormatVersion=config.payload_format_version,
                EnableSimpleResponses=config.enable_simple_responses,
                IdentitySource=config.identity_sources,
                Name=name,
                AuthorizerResultTtlInSeconds=config.result_ttl,
            )
            logger.info(f"Created Lambda authorizer: {name} for API {api_id}")
            return response
        except ClientError as e:
            logger.error(f"Failed to create Lambda authorizer: {str(e)}")
            raise

    def create_vpc_link(self, config: VpcLinkConfig) -> dict[str, Any]:
        """Create a VPC link.

        Args:
            config: VPC link configuration

        Returns:
            VPC link details
        """
        try:
            kwargs = {
                "Name": config.name,
                "SubnetIds": config.subnet_ids,
                "SecurityGroupIds": config.security_group_ids,
            }
            if config.tags:
                kwargs["Tags"] = config.tags

            response = self.client.create_vpc_link(**kwargs)
            logger.info(f"Created VPC link: {config.name}")
            return response
        except ClientError as e:
            logger.error(f"Failed to create VPC link: {str(e)}")
            raise

    def send_websocket_message(
        self, api_id: str, config: WebSocketMessageConfig
    ) -> dict[str, Any]:
        """Send a message to a WebSocket connection.

        Args:
            api_id: API identifier
            config: WebSocket message configuration

        Returns:
            Message sending details
        """
        try:
            data = config.data
            if isinstance(data, dict):
                data = json.dumps(data)

            response = self.client.post_to_connection(
                ApiId=api_id,
                ConnectionId=config.connection_id,
                Data=data,
            )
            logger.info(
                f"Sent WebSocket message to connection {config.connection_id}")
            return response
        except ClientError as e:
            logger.error(f"Failed to send WebSocket message: {str(e)}")
            raise

    def get_websocket_connection(
        self, api_id: str, connection_id: str
    ) -> dict[str, Any]:
        """Get information about a WebSocket connection.

        Args:
            api_id: API identifier
            connection_id: Connection identifier

        Returns:
            Connection details
        """
        try:
            response = self.client.get_connection(
                ApiId=api_id,
                ConnectionId=connection_id,
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to get WebSocket connection: {str(e)}")
            raise

    def delete_websocket_connection(
        self, api_id: str, connection_id: str
    ) -> dict[str, Any]:
        """Delete a WebSocket connection.

        Args:
            api_id: API identifier
            connection_id: Connection identifier

        Returns:
            Deletion details
        """
        try:
            response = self.client.delete_connection(
                ApiId=api_id,
                ConnectionId=connection_id,
            )
            logger.info(f"Deleted WebSocket connection {connection_id}")
            return response
        except ClientError as e:
            logger.error(f"Failed to delete WebSocket connection: {str(e)}")
            raise
