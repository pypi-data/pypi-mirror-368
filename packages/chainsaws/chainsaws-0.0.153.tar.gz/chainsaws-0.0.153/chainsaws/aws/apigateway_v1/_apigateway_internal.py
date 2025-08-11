import logging
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

from chainsaws.aws.apigateway_v1.apigateway_models import (
    APIGatewayAPIConfig,
    IntegrationConfig,
    MethodConfig,
    ResourceConfig,
    RestAPIConfig,
)

logger = logging.getLogger(__name__)


class APIGateway:
    """Internal implementation of API Gateway operations."""

    def __init__(
        self,
        session: boto3.Session,
        config: Optional[APIGatewayAPIConfig] = None,
    ) -> None:
        self.session = session
        self.config = config or APIGatewayAPIConfig()
        self.client = self.session.client("apigateway")

    def create_rest_api(self, config: RestAPIConfig) -> dict[str, Any]:
        """Create a new REST API.

        Args:
            config: REST API configuration

        Returns:
            API details including ID
        """
        try:
            kwargs = {
                "name": config.name,
                "endpointConfiguration": {"types": [config.endpoint_type]},
                "apiKeySource": "HEADER" if config.api_key_required else "NONE",
            }

            if config.description:
                kwargs["description"] = config.description
            if config.binary_media_types:
                kwargs["binaryMediaTypes"] = config.binary_media_types
            if config.minimum_compression_size:
                kwargs["minimumCompressionSize"] = config.minimum_compression_size
            if config.tags:
                kwargs["tags"] = config.tags

            response = self.client.create_rest_api(**kwargs)
            logger.info(f"Created REST API: {
                        response['name']} ({response['id']})")
            return response
        except ClientError as e:
            logger.error(f"Failed to create REST API: {str(e)}")
            raise

    def get_resources(self, api_id: str) -> list[dict[str, Any]]:
        """Get all resources for an API.

        Args:
            api_id: API identifier

        Returns:
            List of resources
        """
        try:
            response = self.client.get_resources(restApiId=api_id)
            return response["items"]
        except ClientError as e:
            logger.error(f"Failed to get resources: {str(e)}")
            raise

    def create_resource(
        self, api_id: str, config: ResourceConfig
    ) -> dict[str, Any]:
        """Create a new resource.

        Args:
            api_id: API identifier
            config: Resource configuration

        Returns:
            Created resource details
        """
        try:
            parent_id = config.parent_id
            if not parent_id:
                # Get root resource ID if parent not specified
                resources = self.get_resources(api_id)
                parent_id = next(r["id"]
                                 for r in resources if r["path"] == "/")

            response = self.client.create_resource(
                restApiId=api_id,
                parentId=parent_id,
                pathPart=config.path_part,
            )
            logger.info(
                f"Created resource: {response['path']} ({response['id']})")
            return response
        except ClientError as e:
            logger.error(f"Failed to create resource: {str(e)}")
            raise

    def put_method(
        self, api_id: str, resource_id: str, config: MethodConfig
    ) -> dict[str, Any]:
        """Put a method on a resource.

        Args:
            api_id: API identifier
            resource_id: Resource identifier
            config: Method configuration

        Returns:
            Method details
        """
        try:
            kwargs = {
                "restApiId": api_id,
                "resourceId": resource_id,
                "httpMethod": config.http_method,
                "authorizationType": config.authorization_type,
                "apiKeyRequired": config.api_key_required,
            }

            if config.request_parameters:
                kwargs["requestParameters"] = config.request_parameters
            if config.request_models:
                kwargs["requestModels"] = config.request_models

            response = self.client.put_method(**kwargs)
            logger.info(
                f"Created method: {config.http_method} on resource {resource_id}")
            return response
        except ClientError as e:
            logger.error(f"Failed to put method: {str(e)}")
            raise

    def put_integration(
        self,
        api_id: str,
        resource_id: str,
        http_method: str,
        config: IntegrationConfig,
    ) -> dict[str, Any]:
        """Put an integration on a method.

        Args:
            api_id: API identifier
            resource_id: Resource identifier
            http_method: HTTP method
            config: Integration configuration

        Returns:
            Integration details
        """
        try:
            kwargs = {
                "restApiId": api_id,
                "resourceId": resource_id,
                "httpMethod": http_method,
                "type": config.type,
            }

            if config.uri:
                kwargs["uri"] = config.uri
            if config.integration_http_method:
                kwargs["integrationHttpMethod"] = config.integration_http_method
            if config.credentials:
                kwargs["credentials"] = config.credentials
            if config.request_parameters:
                kwargs["requestParameters"] = config.request_parameters
            if config.request_templates:
                kwargs["requestTemplates"] = config.request_templates
            if config.passthrough_behavior:
                kwargs["passthroughBehavior"] = config.passthrough_behavior
            if config.cache_namespace:
                kwargs["cacheNamespace"] = config.cache_namespace
            if config.cache_key_parameters:
                kwargs["cacheKeyParameters"] = config.cache_key_parameters
            if config.content_handling:
                kwargs["contentHandling"] = config.content_handling
            if config.timeout_in_millis:
                kwargs["timeoutInMillis"] = config.timeout_in_millis

            response = self.client.put_integration(**kwargs)
            logger.info(
                f"Created integration for {http_method} method on resource {resource_id}")
            return response
        except ClientError as e:
            logger.error(f"Failed to put integration: {str(e)}")
            raise

    def create_deployment(
        self, api_id: str, stage_name: str, stage_description: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a deployment of the API.

        Args:
            api_id: API identifier
            stage_name: Stage name to deploy to
            stage_description: Optional stage description

        Returns:
            Deployment details
        """
        try:
            kwargs = {
                "restApiId": api_id,
                "stageName": stage_name,
            }

            if stage_description:
                kwargs["stageDescription"] = stage_description

            response = self.client.create_deployment(**kwargs)
            logger.info(f"Created deployment to stage: {stage_name}")
            return response
        except ClientError as e:
            logger.error(f"Failed to create deployment: {str(e)}")
            raise
