"""Memcached client implementation for ElastiCache."""

from typing import Any, Dict, Optional
from pymemcache.client.base import Client
from pymemcache.client.retrying import RetryingClient
from pymemcache.exceptions import MemcacheError

from .dataplane_models import CacheConfig, CacheResponse


class MemcachedClient:
    """High-level Memcached client with enhanced features."""

    def __init__(self, config: CacheConfig):
        """Initialize Memcached client with configuration."""
        self.config = config
        base_client = Client(
            server=(config.host, config.port),
            connect_timeout=config.timeout,
            timeout=config.timeout,
            no_delay=True,
            encoding=config.encoding
        )
        self.client = RetryingClient(
            base_client,
            attempts=3,
            retry_delay=0.1,
            retry_for=[MemcacheError]
        )

    def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None,
        noreply: bool = False
    ) -> CacheResponse[bool]:
        """Set a key with an optional TTL."""
        try:
            result = self.client.set(key, value, expire=ttl, noreply=noreply)
            return CacheResponse(success=True, value=bool(result))
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def get(self, key: str) -> CacheResponse[Optional[str]]:
        """Get the value of a key."""
        try:
            value = self.client.get(key)
            return CacheResponse(
                success=True,
                value=value.decode(self.config.encoding) if value else None
            )
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def delete(self, key: str, noreply: bool = False) -> CacheResponse[bool]:
        """Delete a key."""
        try:
            result = self.client.delete(key, noreply=noreply)
            return CacheResponse(success=True, value=bool(result))
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def add(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None,
        noreply: bool = False
    ) -> CacheResponse[bool]:
        """Add a key if it doesn't exist."""
        try:
            result = self.client.add(key, value, expire=ttl, noreply=noreply)
            return CacheResponse(success=True, value=bool(result))
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def replace(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None,
        noreply: bool = False
    ) -> CacheResponse[bool]:
        """Replace an existing key."""
        try:
            result = self.client.replace(
                key, value, expire=ttl, noreply=noreply)
            return CacheResponse(success=True, value=bool(result))
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def append(self, key: str, value: str, noreply: bool = False) -> CacheResponse[bool]:
        """Append data to an existing key."""
        try:
            result = self.client.append(key, value, noreply=noreply)
            return CacheResponse(success=True, value=bool(result))
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def prepend(self, key: str, value: str, noreply: bool = False) -> CacheResponse[bool]:
        """Prepend data to an existing key."""
        try:
            result = self.client.prepend(key, value, noreply=noreply)
            return CacheResponse(success=True, value=bool(result))
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def cas(
        self,
        key: str,
        value: str,
        cas: int,
        ttl: Optional[int] = None,
        noreply: bool = False
    ) -> CacheResponse[bool]:
        """Check and set operation."""
        try:
            result = self.client.cas(
                key, value, cas, expire=ttl, noreply=noreply)
            return CacheResponse(success=True, value=bool(result))
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def gets(self, key: str) -> CacheResponse[tuple[Optional[str], Optional[int]]]:
        """Get value and CAS token for a key."""
        try:
            result = self.client.gets(key)
            if result is None:
                return CacheResponse(success=True, value=(None, None))
            value, cas = result
            return CacheResponse(
                success=True,
                value=(
                    value.decode(self.config.encoding) if value else None,
                    cas
                )
            )
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def touch(self, key: str, ttl: int, noreply: bool = False) -> CacheResponse[bool]:
        """Update the TTL for a key."""
        try:
            result = self.client.touch(key, expire=ttl, noreply=noreply)
            return CacheResponse(success=True, value=bool(result))
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def stats(self) -> CacheResponse[Dict[str, Any]]:
        """Get server statistics."""
        try:
            result = self.client.stats()
            return CacheResponse(success=True, value=result)
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def version(self) -> CacheResponse[str]:
        """Get server version."""
        try:
            result = self.client.version()
            return CacheResponse(
                success=True,
                value=result.decode(self.config.encoding) if result else None
            )
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def flush_all(self, delay: int = 0, noreply: bool = False) -> CacheResponse[bool]:
        """Flush all cache entries."""
        try:
            result = self.client.flush_all(delay=delay, noreply=noreply)
            return CacheResponse(success=True, value=bool(result))
        except MemcacheError as e:
            return CacheResponse(success=False, error=str(e))

    def quit(self) -> None:
        """Close the connection."""
        self.client.quit()
