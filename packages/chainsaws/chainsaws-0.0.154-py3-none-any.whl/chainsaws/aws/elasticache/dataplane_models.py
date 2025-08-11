"""Models for ElastiCache data plane operations."""

from dataclasses import dataclass
from typing import Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')


@dataclass
class CacheConfig:
    """Configuration for cache client."""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    db: int = 0
    ssl: bool = True
    timeout: float = 1.0
    encoding: str = 'utf-8'
    max_connections: int = 10
    retry_on_timeout: bool = True
    health_check_interval: int = 30


@dataclass
class CacheResponse(Generic[T]):
    """Generic response for cache operations."""
    success: bool
    value: Optional[T] = None
    error: Optional[str] = None


@dataclass
class ScanResult:
    """Result of scan operation."""
    cursor: int
    keys: List[str]


@dataclass
class PubSubMessage:
    """Message from pub/sub channel."""
    channel: str
    message: str
    pattern: Optional[str] = None


@dataclass
class StreamEntry:
    """Entry in a Redis stream."""
    id: str
    fields: Dict[str, str]


@dataclass
class StreamRange:
    """Range specification for stream operations."""
    start: str = '-'
    end: str = '+'
    count: Optional[int] = None


@dataclass
class GeoLocation:
    """Geographic location data."""
    longitude: float
    latitude: float
    name: str
    distance: Optional[float] = None


@dataclass
class ZSetMember:
    """Sorted set member with score."""
    member: str
    score: float
