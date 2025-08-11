"""WebSocket connection management for Lambda functions."""

from typing import Optional, Dict, Any, List
import logging

from chainsaws.aws.dynamodb.dynamodb import DynamoDBAPI
from chainsaws.aws.dynamodb.dynamodb_exception import DynamoDBError
from chainsaws.aws.lambda_client.event_handler.handler_models import LambdaResponse
from chainsaws.aws.lambda_client.event_handler.websocket_models import (
    WebSocketConnection,
    WebSocketGroup
)


logger = logging.getLogger(__name__)


class APIGatewayWSConnectionManager:
    """Manages WebSocket connections for API Gateway using DynamoDB."""

    def __init__(
        self,
        table_name: str,
        partition: str = 'websocket_status',
        group_partition: str = 'websocket_group',
        connection_ttl: int = 7200,  # 2 hours
        endpoint_url: Optional[str] = None
    ):
        """Initialize connection manager.
        
        Args:
            table_name: DynamoDB table name for connection management
            partition: Partition name for WebSocket connections
            group_partition: Partition name for WebSocket groups
            connection_ttl: Connection TTL in seconds (default: 2 hours)
            endpoint_url: Optional endpoint URL for DynamoDB
        """
        self.table_name = table_name
        self.partition = partition
        self.group_partition = group_partition
        self.connection_ttl = connection_ttl
        self.dynamodb = DynamoDBAPI(table_name=self.table_name, endpoint_url=endpoint_url)

    async def connect(
        self,
        connection_id: str,
        client_data: Optional[Dict[str, Any]] = None
    ) -> LambdaResponse:
        """Handle new WebSocket connection.
        
        Args:
            connection_id: WebSocket connection ID
            client_data: Optional client metadata
            
        Returns:
            LambdaResponse with connection result
        """
        try:
            # Create and save connection
            connection = WebSocketConnection.create_connection(
                connection_id=connection_id,
                client_data=client_data,
                ttl_seconds=self.connection_ttl
            )

            await self.dynamodb.put_item(
                partition=self.partition,
                item=connection.to_dict(),
                can_overwrite=True
            )

            return LambdaResponse.create(
                {"message": "Connected successfully"},
                status_code=200
            )

        except DynamoDBError as e:
            logger.error(f"Failed to establish connection: {str(e)}")
            return LambdaResponse.create(
                {
                    "message": "Failed to establish connection",
                    "error": str(e)
                },
                status_code=500
            )

    async def disconnect(self, connection_id: str) -> LambdaResponse:
        """Handle WebSocket disconnection.
        
        Args:
            connection_id: WebSocket connection ID
            
        Returns:
            LambdaResponse with disconnection result
        """
        try:
            connection = await self.get_connection(connection_id)
            if not connection:
                return LambdaResponse.create(
                    {"message": "Connection not found"},
                    status_code=404
                )

            # Delete connection
            await self.dynamodb.delete_item(
                partition=self.partition,
                item_id=connection._id
            )

            return LambdaResponse.create(
                {"message": "Disconnected successfully"},
                status_code=200
            )

        except DynamoDBError as e:
            logger.error(f"Failed to handle disconnection: {str(e)}")
            return LambdaResponse.create(
                {
                    "message": "Failed to handle disconnection",
                    "error": str(e)
                },
                status_code=500
            )

    async def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get connection details.
        
        Args:
            connection_id: WebSocket connection ID
            
        Returns:
            Connection details if found, None otherwise
        """
        try:
            result, _ = await self.dynamodb.query_items(
                partition=self.partition,
                pk_field='connection_id',
                pk_value=connection_id,
                limit=1
            )

            if not result:
                return None

            return WebSocketConnection.from_dict(result[0])
        
        except DynamoDBError as e:
            logger.error(f"Failed to get connection: {str(e)}")
            return None

    async def update_last_seen(self, connection_id: str) -> None:
        """Update connection's last seen timestamp.
        
        Args:
            connection_id: WebSocket connection ID
        """
        try:
            connection = await self.get_connection(connection_id)
            if connection:
                connection.update_last_seen()
                await self.dynamodb.update_item(
                    partition=self.partition,
                    item_id=connection._id,
                    item=connection.to_dict(),
                )
        except DynamoDBError as e:
            logger.error(f"Failed to update last seen: {str(e)}")
            # Silently fail as this is not critical

    async def init_table(self) -> None:
        """Initialize DynamoDB table for connection management."""
        await self.dynamodb.init_db_table()

    async def create_group(
        self,
        group_id: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LambdaResponse:
        """Create a new WebSocket group.
        
        Args:
            group_id: Unique group identifier
            name: Group name
            metadata: Optional group metadata
            
        Returns:
            LambdaResponse with creation result
        """
        try:
            group = WebSocketGroup.create_group(
                group_id=group_id,
                name=name,
                metadata=metadata
            )
            
            await self.dynamodb.put_item(
                partition=self.group_partition,
                item=group.to_dict(),
                can_overwrite=False  # 기존 그룹 덮어쓰기 방지
            )

            return LambdaResponse.create(
                {"message": "Group created successfully"},
                status_code=200
            )

        except DynamoDBError as e:
            logger.error(f"Failed to create group: {str(e)}")
            return LambdaResponse.create(
                {
                    "message": "Failed to create group",
                    "error": str(e)
                },
                status_code=500
            )

    async def add_to_group(
        self,
        group_id: str,
        connection_id: str
    ) -> LambdaResponse:
        """Add a connection to a group.
        
        Args:
            group_id: Group identifier
            connection_id: Connection to add
            
        Returns:
            LambdaResponse with result
        """
        try:
            # 1. 그룹 조회
            result, _ = await self.dynamodb.query_items(
                partition=self.group_partition,
                pk_field='group_id',
                pk_value=group_id,
                limit=1
            )
            
            if not result:
                return LambdaResponse.create(
                    {"message": "Group not found"},
                    status_code=404
                )

            group = WebSocketGroup.from_dict(result[0])
            
            # 2. 연결 조회
            connection = await self.get_connection(connection_id)
            if not connection:
                return LambdaResponse.create(
                    {"message": "Connection not found"},
                    status_code=404
                )

            # 3. 그룹에 연결 추가
            if connection_id not in group.connection_ids:
                group.connection_ids.append(connection_id)
                await self.dynamodb.put_item(
                    partition=self.group_partition,
                    item=group.to_dict(),
                    can_overwrite=True
                )

            # 4. 연결에 그룹 추가
            if group_id not in connection.groups:
                connection.groups.append(group_id)
                await self.dynamodb.put_item(
                    partition=self.partition,
                    item=connection.to_dict(),
                    can_overwrite=True
                )

            return LambdaResponse.create(
                {"message": "Added to group successfully"},
                status_code=200
            )

        except DynamoDBError as e:
            logger.error(f"Failed to add to group: {str(e)}")
            return LambdaResponse.create(
                {
                    "message": "Failed to add to group",
                    "error": str(e)
                },
                status_code=500
            )

    async def remove_from_group(
        self,
        group_id: str,
        connection_id: str
    ) -> LambdaResponse:
        """Remove a connection from a group.
        
        Args:
            group_id: Group identifier
            connection_id: Connection to remove
            
        Returns:
            LambdaResponse with result
        """
        try:
            # 1. 그룹 조회
            result, _ = await self.dynamodb.query_items(
                partition=self.group_partition,
                pk_field='group_id',
                pk_value=group_id,
                limit=1
            )
            
            if not result:
                return LambdaResponse.create(
                    {"message": "Group not found"},
                    status_code=404
                )

            group = WebSocketGroup.from_dict(result[0])
            
            # 2. 연결 조회
            connection = await self.get_connection(connection_id)
            if not connection:
                return LambdaResponse.create(
                    {"message": "Connection not found"},
                    status_code=404
                )

            # 3. 그룹에서 연결 제거
            if connection_id in group.connection_ids:
                group.connection_ids.remove(connection_id)
                await self.dynamodb.put_item(
                    partition=self.group_partition,
                    item=group.to_dict(),
                    can_overwrite=True
                )

            # 4. 연결에서 그룹 제거
            if group_id in connection.groups:
                connection.groups.remove(group_id)
                await self.dynamodb.put_item(
                    partition=self.partition,
                    item=connection.to_dict(),
                    can_overwrite=True
                )

            return LambdaResponse.create(
                {"message": "Removed from group successfully"},
                status_code=200
            )

        except DynamoDBError as e:
            logger.error(f"Failed to remove from group: {str(e)}")
            return LambdaResponse.create(
                {
                    "message": "Failed to remove from group",
                    "error": str(e)
                },
                status_code=500
            )

    async def get_group_connections(
        self,
        group_id: str
    ) -> Optional[List[str]]:
        """Get all connection IDs in a group.
        
        Args:
            group_id: Group identifier
            
        Returns:
            List of connection IDs if group exists, None otherwise
        """
        try:
            result, _ = await self.dynamodb.query_items(
                partition=self.group_partition,
                pk_field='group_id',
                pk_value=group_id,
                limit=1
            )
            
            if not result:
                return None

            group = WebSocketGroup.from_dict(result[0])
            return group.connection_ids

        except DynamoDBError as e:
            logger.error(f"Failed to get group connections: {str(e)}")
            return None