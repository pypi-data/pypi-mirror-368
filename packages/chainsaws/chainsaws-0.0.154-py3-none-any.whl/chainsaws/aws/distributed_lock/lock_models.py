from typing import TypedDict, Optional
from datetime import datetime
from dataclasses import dataclass
from chainsaws.aws.dynamodb.dynamodb_models import DynamoDBAPIConfig

@dataclass
class LockStatus:
    """Status of a distributed lock."""
    is_locked: bool
    owner_id: Optional[str]
    expires_at: Optional[int]
    last_renewed_at: Optional[datetime]
    metadata: Optional[dict]

@dataclass
class LockConfig(DynamoDBAPIConfig):
    """Configuration for distributed lock."""
    table_name: str = "distributed-locks"
    ttl_seconds: int = 60 
    owner_id: Optional[str] = None
    retry_times: int = 3
    retry_delay: float = 1.0
    heartbeat_interval: Optional[int] = None

class LockItem(TypedDict):
    """Lock item structure in DynamoDB."""
    lock_id: str
    owner_id: str
    expires_at: int
    created_at: datetime
    last_renewed_at: Optional[datetime]
    metadata: Optional[dict]