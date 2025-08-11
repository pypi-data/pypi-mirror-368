"""WebSocket connection models for DynamoDB."""

import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from chainsaws.aws.dynamodb.dynamodb_models import DynamoModel


@dataclass(kw_only=True)
class WebSocketConnection(DynamoModel):
    """WebSocket connection model for DynamoDB."""

    # Connection fields
    connection_id: str
    status: str
    connected_at: int
    last_seen: int
    client_data: Optional[Dict[str, Any]] = None
    groups: Optional[List[str]] = None  # 소속된 그룹 ID 목록

    # DynamoDB partition configuration
    _partition: str = "websocket_status"
    _pk: str = "connection_id"
    _sk: str = "_crt"

    @classmethod
    def create_connection(
        cls,
        connection_id: str,
        client_data: Optional[Dict[str, Any]] = None,
        ttl_seconds: int = 7200  # 2 hours
    ) -> "WebSocketConnection":
        """Create a new connection record.

        Args:
            connection_id: WebSocket connection ID
            client_data: Optional client metadata
            ttl_seconds: TTL in seconds (default: 2 hours)

        Returns:
            New WebSocketConnection instance
        """
        current_time = int(time.time())
        return cls(
            connection_id=connection_id,
            status="CONNECTED",
            connected_at=current_time,
            last_seen=current_time,
            client_data=client_data,
            groups=[],  # 초기에는 빈 그룹 목록
            _ttl=current_time + ttl_seconds
        )

    def update_last_seen(self) -> None:
        """Update the last seen timestamp."""
        self.last_seen = int(time.time())


@dataclass(kw_only=True)
class WebSocketGroup(DynamoModel):
    """WebSocket group model for DynamoDB."""

    # Group fields
    group_id: str
    name: str
    created_at: int
    metadata: Optional[Dict[str, Any]]
    connection_ids: List[str] = field(default_factory=list)  # 그룹에 속한 연결 ID 목록

    # DynamoDB partition configuration
    _partition: str = "websocket_group"
    _pk: str = "group_id"
    _sk: str = "_crt"

    @classmethod
    def create_group(
        cls,
        group_id: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "WebSocketGroup":
        """Create a new group.

        Args:
            group_id: Unique group identifier
            name: Group name
            metadata: Optional group metadata

        Returns:
            New WebSocketGroup instance
        """
        return cls(
            group_id=group_id,
            name=name,
            created_at=int(time.time()),
            metadata=metadata,
            connection_ids=[]  # 초기에는 빈 연결 목록
        )
