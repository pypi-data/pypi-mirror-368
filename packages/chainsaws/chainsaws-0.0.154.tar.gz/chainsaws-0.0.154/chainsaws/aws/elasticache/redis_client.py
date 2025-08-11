"""Redis client implementation for ElastiCache."""

from typing import Any, Dict, Optional, Set, Callable
from redis import Redis, ConnectionPool
from redis.client import Pipeline
from redis.exceptions import RedisError

from .dataplane_models import (
    CacheConfig,
    CacheResponse,
    PubSubMessage,
)


class RedisClient:
    """High-level Redis client with enhanced features."""

    def __init__(self, config: CacheConfig):
        """Initialize Redis client with configuration."""
        self.config = config
        self.pool = ConnectionPool(
            host=config.host,
            port=config.port,
            username=config.username,
            password=config.password,
            db=config.db,
            ssl=config.ssl,
            encoding=config.encoding,
            max_connections=config.max_connections,
            health_check_interval=config.health_check_interval,
            retry_on_timeout=config.retry_on_timeout,
            socket_timeout=config.timeout,
            socket_connect_timeout=config.timeout,
        )
        self.redis = Redis(connection_pool=self.pool)

    def pipeline(self) -> Pipeline:
        """Create a pipeline for batch operations."""
        return self.redis.pipeline()

    # Basic operations
    def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> CacheResponse[bool]:
        """Set key to hold the string value with optional TTL."""
        try:
            result = self.redis.set(key, value, ex=ttl, nx=nx, xx=xx)
            return CacheResponse(success=True, value=bool(result))
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def get(self, key: str) -> CacheResponse[Optional[str]]:
        """Get the value of key."""
        try:
            value = self.redis.get(key)
            return CacheResponse(
                success=True,
                value=value.decode(self.config.encoding) if value else None
            )
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def delete(self, key: str) -> CacheResponse[bool]:
        """Delete a key."""
        try:
            result = self.redis.delete(key)
            return CacheResponse(success=True, value=bool(result))
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def exists(self, key: str) -> CacheResponse[bool]:
        """Check if key exists."""
        try:
            result = self.redis.exists(key)
            return CacheResponse(success=True, value=bool(result))
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def expire(self, key: str, seconds: int) -> CacheResponse[bool]:
        """Set a key's time to live in seconds."""
        try:
            result = self.redis.expire(key, seconds)
            return CacheResponse(success=True, value=bool(result))
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    # List operations
    def lpush(self, key: str, *values: str) -> CacheResponse[int]:
        """Push values to the head of a list."""
        try:
            result = self.redis.lpush(key, *values)
            return CacheResponse(success=True, value=result)
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def rpush(self, key: str, *values: str) -> CacheResponse[int]:
        """Push values to the tail of a list."""
        try:
            result = self.redis.rpush(key, *values)
            return CacheResponse(success=True, value=result)
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def lpop(self, key: str) -> CacheResponse[Optional[str]]:
        """Remove and get the first element in a list."""
        try:
            value = self.redis.lpop(key)
            return CacheResponse(
                success=True,
                value=value.decode(self.config.encoding) if value else None
            )
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def rpop(self, key: str) -> CacheResponse[Optional[str]]:
        """Remove and get the last element in a list."""
        try:
            value = self.redis.rpop(key)
            return CacheResponse(
                success=True,
                value=value.decode(self.config.encoding) if value else None
            )
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    # Set operations
    def sadd(self, key: str, *members: str) -> CacheResponse[int]:
        """Add members to a set."""
        try:
            result = self.redis.sadd(key, *members)
            return CacheResponse(success=True, value=result)
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def srem(self, key: str, *members: str) -> CacheResponse[int]:
        """Remove members from a set."""
        try:
            result = self.redis.srem(key, *members)
            return CacheResponse(success=True, value=result)
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def smembers(self, key: str) -> CacheResponse[Set[str]]:
        """Get all members in a set."""
        try:
            result = self.redis.smembers(key)
            return CacheResponse(
                success=True,
                value={v.decode(self.config.encoding) for v in result}
            )
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    # Hash operations
    def hset(self, key: str, field: str, value: str) -> CacheResponse[bool]:
        """Set the string value of a hash field."""
        try:
            result = self.redis.hset(key, field, value)
            return CacheResponse(success=True, value=bool(result))
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def hget(self, key: str, field: str) -> CacheResponse[Optional[str]]:
        """Get the value of a hash field."""
        try:
            value = self.redis.hget(key, field)
            return CacheResponse(
                success=True,
                value=value.decode(self.config.encoding) if value else None
            )
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def hgetall(self, key: str) -> CacheResponse[Dict[str, str]]:
        """Get all the fields and values in a hash."""
        try:
            result = self.redis.hgetall(key)
            return CacheResponse(
                success=True,
                value={
                    k.decode(self.config.encoding): v.decode(self.config.encoding)
                    for k, v in result.items()
                }
            )
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    # Pub/Sub operations
    def publish(self, channel: str, message: str) -> CacheResponse[int]:
        """Publish a message to a channel."""
        try:
            result = self.redis.publish(channel, message)
            return CacheResponse(success=True, value=result)
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def subscribe(
        self,
        channel: str,
        callback: Callable[[PubSubMessage], None],
        pattern: bool = False
    ) -> None:
        """Subscribe to a channel and process messages with callback."""
        pubsub = self.redis.pubsub()

        def message_handler(message: Dict[str, Any]) -> None:
            if message['type'] in ('message', 'pmessage'):
                msg = PubSubMessage(
                    channel=message['channel'].decode(self.config.encoding),
                    message=message['data'].decode(self.config.encoding),
                    pattern=message.get('pattern', None)
                )
                callback(msg)

        if pattern:
            pubsub.psubscribe(**{channel: message_handler})
        else:
            pubsub.subscribe(**{channel: message_handler})

        pubsub.run_in_thread(sleep_time=0.001)

    def close(self) -> None:
        """Close all connections in the pool."""
        self.pool.disconnect()
