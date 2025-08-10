"""ValKey client implementation for ElastiCache."""

from redis.exceptions import RedisError

from .dataplane_models import CacheConfig, CacheResponse
from .redis_client import RedisClient


class ValKeyClient(RedisClient):
    """High-level ValKey client with enhanced features."""

    def __init__(self, config: CacheConfig):
        """Initialize ValKey client with configuration."""
        super().__init__(config)

    def enhanced_io(self, key: str, value: str) -> CacheResponse[bool]:
        """ValKey enhanced I/O operation.

        Args:
            key: The key to store
            value: The value to store

        Returns:
            CacheResponse indicating success/failure
        """
        try:
            result = self.redis.execute_command("ENHANCED_IO", key, value)
            return CacheResponse(success=True, value=bool(result))
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def tls_offload(self, enabled: bool) -> CacheResponse[bool]:
        """Configure TLS offloading.

        Args:
            enabled: Whether to enable TLS offloading

        Returns:
            CacheResponse indicating success/failure
        """
        try:
            result = self.redis.execute_command(
                "TLS_OFFLOAD", "ON" if enabled else "OFF")
            return CacheResponse(success=True, value=bool(result))
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def io_multiplexing(self, enabled: bool) -> CacheResponse[bool]:
        """Configure I/O multiplexing.

        Args:
            enabled: Whether to enable I/O multiplexing

        Returns:
            CacheResponse indicating success/failure
        """
        try:
            result = self.redis.execute_command(
                "IO_MULTIPLEX", "ON" if enabled else "OFF")
            return CacheResponse(success=True, value=bool(result))
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def set_compression(self, algorithm: str, level: int) -> CacheResponse[bool]:
        """Configure data compression.

        Args:
            algorithm: Compression algorithm to use (e.g., "lz4", "zstd")
            level: Compression level (1-9)

        Returns:
            CacheResponse indicating success/failure
        """
        try:
            result = self.redis.execute_command(
                "SET_COMPRESSION", algorithm, level)
            return CacheResponse(success=True, value=bool(result))
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))

    def get_compression_info(self, key: str) -> CacheResponse[dict]:
        """Get compression information for a key.

        Args:
            key: The key to check

        Returns:
            CacheResponse containing compression information
        """
        try:
            result = self.redis.execute_command("GET_COMPRESSION_INFO", key)
            return CacheResponse(success=True, value=result)
        except RedisError as e:
            return CacheResponse(success=False, error=str(e))
