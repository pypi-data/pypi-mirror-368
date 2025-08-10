from boto3 import Session
from typing import Optional
from chainsaws.aws.apigatewaymanagement.apigatewaymanagement_models import APIGatewayManagementAPIConfig
from chainsaws.aws.apigatewaymanagement.apigatewaymanagement_exceptions import (
    APIGatewayManagementEndpointURLRequiredException,
    APIGatewayManagementPostToConnectionError,
)
from chainsaws.aws.apigatewaymanagement.response.GetConnectionResponse import (
    GetConnectionResponse
)

class APIGatewayManagement:
    def __init__(
      self,
      boto3_session: Session,
      config: Optional[APIGatewayManagementAPIConfig] = None,
    ) -> None:
        self.config = config
        if not self.config or not self.config.endpoint_url:
            raise APIGatewayManagementEndpointURLRequiredException("endpoint_url is required")
    
        self.apigateway_management_client = boto3_session.client(
            service_name="apigatewaymanagementapi",
            region_name=self.config.region,
            endpoint_url=self.config.endpoint_url,
        )


    def post_to_connection(
        self,
        connection_id: str,
        data: str | bytes,
    ) -> None:
        if not isinstance(data, bytes):
            raise APIGatewayManagementPostToConnectionError("data must be a bytes object")

        self.apigateway_management_client.post_to_connection(
            ConnectionId=connection_id,
            Data=data,
        )


    def get_connection(
        self,
        connection_id: str
    ) -> GetConnectionResponse:
        response = self.apigateway_management_client.get_connection(
            ConnectionId=connection_id,
        )

        return response
    

    def delete_connection(
        self,
        connection_id: str
    ) -> None:
        self.apigateway_management_client.delete_connection(
            ConnectionId=connection_id,
        )