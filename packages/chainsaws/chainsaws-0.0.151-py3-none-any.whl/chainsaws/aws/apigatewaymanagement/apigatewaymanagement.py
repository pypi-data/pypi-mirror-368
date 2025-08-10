from typing import Optional
from chainsaws.aws.apigatewaymanagement._apigatewaymanagement_internal import APIGatewayManagement
from chainsaws.aws.apigatewaymanagement.apigatewaymanagement_models import APIGatewayManagementAPIConfig
from chainsaws.aws.apigatewaymanagement.response.GetConnectionResponse import GetConnectionResponse
from chainsaws.aws.shared import session

class APIGatewayManagementAPI():
    def __init__(
        self,
        config: Optional[APIGatewayManagementAPIConfig] = None,
    ) -> None:
        self.config = config
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.apigateway_management = APIGatewayManagement(
            boto3_session=self.boto3_session,
            config=self.config,
        )

    def post_to_connection(
        self,
        connection_id: str,
        data: str | bytes,
    ) -> None:
        self.apigateway_management.post_to_connection(
            connection_id=connection_id,
            data=data,
        )

    def get_connection(
        self,
        connection_id: str,
    ) -> GetConnectionResponse:
        return self.apigateway_management.get_connection(
            connection_id=connection_id,
        )
    
    def delete_connection(
        self,
        connection_id: str,
    ) -> None:
        self.apigateway_management.delete_connection(
            connection_id=connection_id,
        )