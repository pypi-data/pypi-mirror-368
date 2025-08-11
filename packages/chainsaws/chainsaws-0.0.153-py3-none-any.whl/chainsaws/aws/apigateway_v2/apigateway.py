from typing import Any, Optional, Union

from chainsaws.aws.apigateway_v2._apigateway_internal import APIGatewayV2
from chainsaws.aws.apigateway_v2.apigateway_models import (
    APIGatewayV2APIConfig,
    CreateApiResponse,
    AuthorizerResponse,
    CorsConfig,
    HttpApiConfig,
    IntegrationConfig,
    IntegrationResponse,
    IntegrationType,
    JwtConfig,
    LambdaAuthorizerConfig,
    RouteConfig,
    RouteResponse,
    StageResponse,
    VpcLinkConfig,
    VpcLinkResponse,
    WebSocketApiConfig,
    WebSocketMessageConfig,
)
from chainsaws.aws.shared import session


class APIGatewayV2API:
    """High-level API Gateway v2 operations."""

    def __init__(self, config: Optional[APIGatewayV2APIConfig] = None) -> None:
        """Initialize API Gateway v2 API.

        Args:
            config: Optional API Gateway v2 configuration

        Example:
            ```python
            # Initialize with default configuration
            api_gateway = APIGatewayV2API()

            # Initialize with custom configuration
            config = APIGatewayV2APIConfig(
                region="us-west-2",
                credentials={"access_key": "...", "secret_key": "..."}
            )
            api_gateway = APIGatewayV2API(config)
            ```
        """
        self.config = config or APIGatewayV2APIConfig()
        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None
        )
        self.api_gateway = APIGatewayV2(self.boto3_session, config=self.config)

    def create_http_api(
        self,
        name: str,
        cors_enabled: bool = False,
        cors_origins: Optional[list[str]] = None,
        cors_methods: Optional[list[str]] = None,
        cors_headers: Optional[list[str]] = None,
        cors_expose_headers: Optional[list[str]] = None,
        cors_max_age: Optional[int] = None,
        cors_allow_credentials: Optional[bool] = None,
        description: Optional[str] = None,
        disable_execute_api_endpoint: bool = False,
        tags: Optional[dict[str, str]] = None,
    ) -> CreateApiResponse:
        """Create a new HTTP API.

        Args:
            name: API name
            cors_enabled: Whether to enable CORS
            cors_origins: Allowed origins for CORS
            cors_methods: Allowed methods for CORS
            cors_headers: Allowed headers for CORS
            cors_expose_headers: Headers to expose in CORS
            cors_max_age: Max age for CORS preflight
            cors_allow_credentials: Whether to allow credentials
            description: API description
            disable_execute_api_endpoint: Whether to disable execute-api endpoint
            tags: API tags

        Returns:
            API details

        Example:
            ```python
            # Create a simple HTTP API
            api = api_gateway.create_http_api(
                name="my-api",
                description="My HTTP API"
            )

            # Create an HTTP API with CORS
            api = api_gateway.create_http_api(
                name="my-cors-api",
                cors_enabled=True,
                cors_origins=["https://example.com"],
                cors_methods=["GET", "POST"],
                cors_headers=["Content-Type", "Authorization"],
                tags={"Environment": "prod"}
            )
            ```
        """
        cors_config = None
        if cors_enabled:
            cors_config = CorsConfig(
                allow_origins=cors_origins or ["*"],
                allow_methods=cors_methods or ["*"],
                allow_headers=cors_headers,
                expose_headers=cors_expose_headers,
                max_age=cors_max_age,
                allow_credentials=cors_allow_credentials,
            )

        config = HttpApiConfig(
            name=name,
            cors_configuration=cors_config,
            disable_execute_api_endpoint=disable_execute_api_endpoint,
            description=description,
            tags=tags,
        )
        return self.api_gateway.create_api(config)

    def create_websocket_api(
        self,
        name: str,
        route_selection_expression: str = "$request.body.action",
        api_key_selection_expression: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> CreateApiResponse:
        """Create a new WebSocket API.

        Args:
            name: API name
            route_selection_expression: Expression to select route
            api_key_selection_expression: Expression to select API key
            description: API description
            tags: API tags

        Returns:
            API details

        Example:
            ```python
            # Create a WebSocket API
            ws_api = api_gateway.create_websocket_api(
                name="my-websocket-api",
                description="My WebSocket API",
                route_selection_expression="$request.body.action",
                tags={"Environment": "prod"}
            )

            # Create routes for the WebSocket API
            api_gateway.create_route(
                api_id=ws_api["ApiId"],
                route_key="$connect",
                target="integration-id"
            )
            api_gateway.create_route(
                api_id=ws_api["ApiId"],
                route_key="$disconnect",
                target="integration-id"
            )
            ```
        """
        config = WebSocketApiConfig(
            name=name,
            route_selection_expression=route_selection_expression,
            api_key_selection_expression=api_key_selection_expression,
            description=description,
            tags=tags,
        )
        return self.api_gateway.create_api(config)

    def create_lambda_integration(
        self,
        api_id: str,
        lambda_arn: str,
        payload_format_version: str = "2.0",
    ) -> IntegrationResponse:
        """Create a Lambda integration.

        Args:
            api_id: API identifier
            lambda_arn: Lambda function ARN
            payload_format_version: Payload format version

        Returns:
            Integration details

        Example:
            ```python
            # Create a Lambda integration
            integration = api_gateway.create_lambda_integration(
                api_id="api-id",
                lambda_arn="arn:aws:lambda:region:account:function:my-function",
                payload_format_version="2.0"
            )

            # Create a route with the Lambda integration
            api_gateway.create_route(
                api_id="api-id",
                route_key="GET /items",
                target=integration["IntegrationId"]
            )
            ```
        """
        config = IntegrationConfig(
            integration_type=IntegrationType.AWS_PROXY,
            integration_uri=lambda_arn,
            payload_format_version=payload_format_version,
        )
        return self.api_gateway.create_integration(api_id, config)

    def create_http_integration(
        self,
        api_id: str,
        endpoint_url: str,
        method: str = "ANY",
    ) -> IntegrationResponse:
        """Create an HTTP integration.

        Args:
            api_id: API identifier
            endpoint_url: HTTP endpoint URL
            method: HTTP method

        Returns:
            Integration details

        Example:
            ```python
            # Create an HTTP integration
            integration = api_gateway.create_http_integration(
                api_id="api-id",
                endpoint_url="https://api.example.com",
                method="POST"
            )

            # Create a route with the HTTP integration
            api_gateway.create_route(
                api_id="api-id",
                route_key="POST /proxy",
                target=integration["IntegrationId"]
            )
            ```
        """
        config = IntegrationConfig(
            integration_type=IntegrationType.HTTP_PROXY,
            integration_uri=endpoint_url,
            integration_method=method,
        )
        return self.api_gateway.create_integration(api_id, config)

    def create_route(
        self,
        api_id: str,
        route_key: str,
        target: str,
        authorization_type: str = "NONE",
        authorizer_id: Optional[str] = None,
    ) -> RouteResponse:
        """Create a route.

        Args:
            api_id: API identifier
            route_key: Route key (e.g., "GET /items")
            target: Integration ID
            authorization_type: Authorization type
            authorizer_id: Authorizer ID

        Returns:
            Route details

        Example:
            ```python
            # Create a simple route
            route = api_gateway.create_route(
                api_id="api-id",
                route_key="GET /items",
                target="integration-id"
            )

            # Create a route with JWT authorization
            route = api_gateway.create_route(
                api_id="api-id",
                route_key="POST /items",
                target="integration-id",
                authorization_type="JWT",
                authorizer_id="authorizer-id"
            )
            ```
        """
        config = RouteConfig(
            route_key=route_key,
            target=target,
            authorization_type=authorization_type,
            authorizer_id=authorizer_id,
        )
        return self.api_gateway.create_route(api_id, config)

    def create_stage(
        self,
        api_id: str,
        stage_name: str,
        auto_deploy: bool = True,
        description: Optional[str] = None,
        stage_variables: Optional[dict[str, str]] = None,
    ) -> StageResponse:
        """Create a stage.

        Args:
            api_id: API identifier
            stage_name: Stage name
            auto_deploy: Whether to automatically deploy changes
            description: Stage description
            stage_variables: Stage variables

        Returns:
            Stage details

        Example:
            ```python
            # Create a simple stage
            stage = api_gateway.create_stage(
                api_id="api-id",
                stage_name="prod"
            )

            # Create a stage with variables
            stage = api_gateway.create_stage(
                api_id="api-id",
                stage_name="dev",
                description="Development stage",
                stage_variables={
                    "environment": "development",
                    "table_name": "dev-table"
                }
            )
            ```
        """
        return self.api_gateway.create_stage(
            api_id=api_id,
            stage_name=stage_name,
            auto_deploy=auto_deploy,
            description=description,
            stage_variables=stage_variables,
        )

    def create_jwt_authorizer(
        self,
        api_id: str,
        name: str,
        issuer: str,
        audiences: list[str],
        identity_source: Optional[list[str]] = None,
    ) -> AuthorizerResponse:
        """Create a JWT authorizer.

        Args:
            api_id: API identifier
            name: Authorizer name
            issuer: JWT token issuer URL
            audiences: List of allowed audiences
            identity_source: Where to extract the token from

        Returns:
            Authorizer details

        Example:
            ```python
            # Create a JWT authorizer for Cognito
            authorizer = api_gateway.create_jwt_authorizer(
                api_id="api-id",
                name="cognito-authorizer",
                issuer="https://cognito-idp.region.amazonaws.com/user-pool-id",
                audiences=["client-id"],
                identity_source=["$request.header.Authorization"]
            )

            # Create a protected route
            api_gateway.create_route(
                api_id="api-id",
                route_key="GET /protected",
                target="integration-id",
                authorization_type="JWT",
                authorizer_id=authorizer["AuthorizerId"]
            )
            ```
        """
        config = JwtConfig(
            issuer=issuer,
            audiences=audiences,
            identity_source=identity_source or [
                "$request.header.Authorization"],
        )
        return self.api_gateway.create_jwt_authorizer(api_id, name, config)

    def create_lambda_authorizer(
        self,
        api_id: str,
        name: str,
        function_arn: str,
        identity_sources: list[str],
        result_ttl: int = 300,
        enable_simple_responses: bool = True,
        payload_format_version: str = "2.0",
    ) -> AuthorizerResponse:
        """Create a Lambda authorizer.

        Args:
            api_id: API identifier
            name: Authorizer name
            function_arn: Lambda function ARN
            identity_sources: Where to extract identity from
            result_ttl: Time to cache authorizer result
            enable_simple_responses: Whether to enable simple IAM responses
            payload_format_version: Authorizer payload version

        Returns:
            Authorizer details

        Example:
            ```python
            # Create a Lambda authorizer
            authorizer = api_gateway.create_lambda_authorizer(
                api_id="api-id",
                name="custom-authorizer",
                function_arn="arn:aws:lambda:region:account:function:authorizer",
                identity_sources=["$request.header.Authorization"],
                result_ttl=300,
                enable_simple_responses=True
            )

            # Create a protected route
            api_gateway.create_route(
                api_id="api-id",
                route_key="GET /protected",
                target="integration-id",
                authorization_type="CUSTOM",
                authorizer_id=authorizer["AuthorizerId"]
            )
            ```
        """
        config = LambdaAuthorizerConfig(
            function_arn=function_arn,
            identity_sources=identity_sources,
            result_ttl=result_ttl,
            enable_simple_responses=enable_simple_responses,
            payload_format_version=payload_format_version,
        )
        return self.api_gateway.create_lambda_authorizer(api_id, name, config)

    def create_vpc_link(
        self,
        name: str,
        subnet_ids: list[str],
        security_group_ids: list[str],
        tags: Optional[dict[str, str]] = None,
    ) -> VpcLinkResponse:
        """Create a VPC link.

        Args:
            name: VPC link name
            subnet_ids: Subnet IDs for the VPC link
            security_group_ids: Security group IDs
            tags: Tags for VPC link

        Returns:
            VPC link details

        Example:
            ```python
            # Create a VPC link
            vpc_link = api_gateway.create_vpc_link(
                name="my-vpc-link",
                subnet_ids=["subnet-1234", "subnet-5678"],
                security_group_ids=["sg-1234"],
                tags={"Environment": "prod"}
            )

            # Create a VPC link integration
            integration = api_gateway.create_vpc_link_integration(
                api_id="api-id",
                vpc_link_id=vpc_link["VpcLinkId"],
                target_uri="http://internal-nlb.region.elb.amazonaws.com",
                method="POST"
            )
            ```
        """
        config = VpcLinkConfig(
            name=name,
            subnet_ids=subnet_ids,
            security_group_ids=security_group_ids,
            tags=tags,
        )
        return self.api_gateway.create_vpc_link(config)

    def create_vpc_link_integration(
        self,
        api_id: str,
        vpc_link_id: str,
        target_uri: str,
        method: str = "ANY",
    ) -> IntegrationResponse:
        """Create a VPC link integration.

        Args:
            api_id: API identifier
            vpc_link_id: VPC link ID
            target_uri: Target URI in VPC
            method: HTTP method

        Returns:
            Integration details

        Example:
            ```python
            # Create a VPC link integration for internal ALB
            integration = api_gateway.create_vpc_link_integration(
                api_id="api-id",
                vpc_link_id="vpc-link-id",
                target_uri="http://internal-alb.region.elb.amazonaws.com",
                method="ANY"
            )

            # Create a route with the VPC link integration
            api_gateway.create_route(
                api_id="api-id",
                route_key="ANY /private",
                target=integration["IntegrationId"]
            )
            ```
        """
        config = IntegrationConfig(
            integration_type=IntegrationType.VPC_LINK,
            integration_uri=target_uri,
            integration_method=method,
            connection_id=vpc_link_id,
        )
        return self.api_gateway.create_integration(api_id, config)

    def send_websocket_message(
        self,
        api_id: str,
        connection_id: str,
        data: Union[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Send a message to a WebSocket connection.

        Args:
            api_id: API identifier
            connection_id: WebSocket connection ID
            data: Message data to send (string or JSON-serializable dict)

        Returns:
            Message sending details

        Example:
            ```python
            # Send a text message
            api_gateway.send_websocket_message(
                api_id="api-id",
                connection_id="connection-id",
                data="Hello, WebSocket!"
            )

            # Send a JSON message
            api_gateway.send_websocket_message(
                api_id="api-id",
                connection_id="connection-id",
                data={
                    "action": "update",
                    "data": {"status": "completed"}
                }
            )
            ```
        """
        config = WebSocketMessageConfig(
            connection_id=connection_id,
            data=data,
        )
        return self.api_gateway.send_websocket_message(api_id, config)

    def get_websocket_connection(
        self, api_id: str, connection_id: str
    ) -> dict[str, Any]:
        """Get information about a WebSocket connection.

        Args:
            api_id: API identifier
            connection_id: Connection identifier

        Returns:
            Connection details

        Example:
            ```python
            # Get connection information
            connection = api_gateway.get_websocket_connection(
                api_id="api-id",
                connection_id="connection-id"
            )
            print(f"Connection created at: {connection['ConnectedAt']}")
            ```
        """
        return self.api_gateway.get_websocket_connection(api_id, connection_id)

    def delete_websocket_connection(
        self, api_id: str, connection_id: str
    ) -> dict[str, Any]:
        """Delete a WebSocket connection.

        Args:
            api_id: API identifier
            connection_id: Connection identifier

        Returns:
            Deletion details

        Example:
            ```python
            # Delete an inactive connection
            api_gateway.delete_websocket_connection(
                api_id="api-id",
                connection_id="connection-id"
            )
            ```
        """
        return self.api_gateway.delete_websocket_connection(api_id, connection_id)

    def init_lambda_integration(
        self,
        api_id: str,
        lambda_arn: str,
        payload_format_version: str = "2.0",
    ) -> None:
        """Initialize Lambda integration with a catch-all proxy route.
        If the integration already exists, it will be skipped.

        Args:
            api_id: API identifier
            lambda_arn: Lambda function ARN
            payload_format_version: Payload format version

        Example:
            ```python
            # Initialize Lambda integration
            api_gateway.init_lambda_integration(
                api_id="api-id",
                lambda_arn="arn:aws:lambda:region:account:function:my-function"
            )
            ```
        """
        try:
            integration = self.create_lambda_integration(
                api_id=api_id,
                lambda_arn=lambda_arn,
                payload_format_version=payload_format_version,
            )
            self.create_route(
                api_id=api_id,
                route_key="ANY /{proxy+}",
                target=f"integrations/{integration['IntegrationId']}"
            )
        except self.api_gateway.client.exceptions.ConflictException:
            pass
        except Exception as e:
            raise Exception(
                f"Failed to initialize Lambda integration: {str(e)}") from e

    def init_http_api_with_lambda(
        self,
        name: str,
        lambda_arn: str,
        account_id: str,
        cors_enabled: bool = False,
        cors_origins: Optional[list[str]] = None,
        description: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        payload_format_version: str = "2.0",
    ) -> CreateApiResponse:
        """Create a new HTTP API and initialize Lambda integration with a catch-all proxy route.
        If the API already exists with the same name, it will return the existing API details.

        Args:
            name: API name
            lambda_arn: Lambda function ARN
            account_id: AWS account ID
            cors_enabled: Whether to enable CORS
            cors_origins: Allowed origins for CORS
            description: API description
            tags: API tags
            payload_format_version: Lambda integration payload format version

        Returns:
            API details

        Example:
            ```python
            # Create an HTTP API with Lambda integration
            api = api_gateway.init_http_api_with_lambda(
                name="my-lambda-api",
                lambda_arn="arn:aws:lambda:region:account:function:my-function",
                account_id="123456789012",
                region="us-east-1",
                cors_enabled=True,
                cors_origins=["https://example.com"],
                description="My Lambda API",
                tags={"Environment": "prod"}
            )
            ```
        """
        try:
            # Create HTTP API
            api = self.create_http_api(
                name=name,
                cors_enabled=cors_enabled,
                cors_origins=cors_origins,
                description=description,
                tags=tags,
            )

            # Add Lambda permission for API Gateway
            from chainsaws.aws.iam.iam import IAMAPI
            iam = IAMAPI()
            source_arn = f"arn:aws:execute-api:{
                self.config.region}:{account_id}:{api['ApiId']}/*"
            iam.add_lambda_permission(
                function_name=lambda_arn,
                statement_id=f"AllowAPIGateway-{name}",
                action="lambda:InvokeFunction",
                principal="apigateway.amazonaws.com",
                source_arn=source_arn,
            )

            # Create Lambda integration
            self.init_lambda_integration(
                api_id=api["ApiId"],
                lambda_arn=lambda_arn,
                payload_format_version=payload_format_version,
            )
            return api
        except self.api_gateway.client.exceptions.ConflictException:
            # If API already exists, find and return it
            apis = self.api_gateway.get_apis()
            for existing_api in apis["Items"]:
                if existing_api["Name"] == name:
                    return existing_api
            raise  # Re-raise if we couldn't find the API
        except Exception as e:
            raise Exception(
                f"Failed to initialize HTTP API with Lambda integration: {str(e)}") from e
