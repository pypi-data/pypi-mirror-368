import time
import uuid
import logging
import threading
import asyncio
from datetime import datetime
from typing import Optional
from contextlib import contextmanager, asynccontextmanager
from threading import Lock

from chainsaws.aws.dynamodb import DynamoDBAPI, DynamoDBAPIConfig
from chainsaws.aws.distributed_lock.lock_models import LockConfig, LockItem, LockStatus
from chainsaws.aws.distributed_lock.lock_exceptions import LockAcquisitionError, LockReleaseError, LockRenewalError

logger = logging.getLogger(__name__)



class DistributedLockAPI:
    PARTITION_NAME = "distributed_lock"
    
    def __init__(self, config: LockConfig):
        """Initialize distributed lock.
        
        Args:
            config: Lock configuration
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not config.table_name:
            raise ValueError("table_name is required")
            
        self.ttl_seconds = config.ttl_seconds
        self.owner_id = config.owner_id or str(uuid.uuid4())
        self.retry_times = config.retry_times
        self.retry_delay = config.retry_delay
        self.heartbeat_interval = config.heartbeat_interval or self.ttl_seconds // 2
        
        if self.ttl_seconds <= self.heartbeat_interval:
            raise ValueError("ttl_seconds must be greater than heartbeat_interval")
        
        # DynamoDB 설정 추가
        dynamodb_config = DynamoDBAPIConfig(
            credentials=config.credentials,
            region=config.region,           
            endpoint_url=config.endpoint_url
        )
        
        self.dynamodb = DynamoDBAPI(
            table_name=config.table_name,
            config=dynamodb_config
        )
        
        # Thread safety
        self._locks_mutex = Lock()
        self._active_locks = {}
        self._renewal_threads = {}
        self._shutdown = threading.Event()


    def init_lock(self) -> None:
        self.dynamodb.init_db_table()
        self.dynamodb.apply_partition_map(
            partition_map={
                self.PARTITION_NAME: {
                    "pk": "lock_id",
                    "sk": "owner_id",
                    "uks": None,
                    "indexes": []
                }   
            }
        )

    def _verify_lock_ownership(self, lock_id: str) -> bool:
        """Verify that we still own the lock.
        
        Args:
            lock_id: Lock identifier to verify
            
        Returns:
            bool: True if we still own the lock
        """
        item = self.dynamodb.get_item(
            item_id=f"{self.PARTITION_NAME}#lock_id#{lock_id}&owner_id#S{self.owner_id}|"
        )
        if not item:
            return False
        return (
            item.get('owner_id') == self.owner_id and
            item.get('expires_at', 0) > time.time()
        )

    def get_lock_status(self, lock_id: str) -> LockStatus:
        """Get current status of a lock.
        
        Args:
            lock_id: Lock identifier to check
            
        Returns:
            LockStatus object containing current lock state
        """
        items, _ = self.dynamodb.query_items(
            partition=self.PARTITION_NAME,
            pk_field="lock_id",
            pk_value=lock_id,
            consistent_read=True
        )
        
        if not items:
            return LockStatus(
                is_locked=False,
                owner_id=None,
                expires_at=None,
                last_renewed_at=None,
                metadata=None
            )
        
        current_time = time.time()
        active_lock = None
        
        for item in items:
            expires_at = item.get('expires_at', 0)
            if expires_at > current_time:
                if not active_lock or expires_at > active_lock.get('expires_at', 0):
                    active_lock = item
        
        if active_lock:
            return LockStatus(
                is_locked=True,
                owner_id=active_lock.get('owner_id'),
                expires_at=active_lock.get('expires_at'),
                last_renewed_at=active_lock.get('last_renewed_at'),
                metadata=active_lock.get('metadata')
            )
        else:
            return LockStatus(
                is_locked=False,
                owner_id=None,
                expires_at=None,
                last_renewed_at=None,
                metadata=None
            )

    def acquire(
        self,
        lock_id: str,
        timeout: Optional[float] = None,
        metadata: Optional[dict] = None
    ) -> bool:
        """Acquire a distributed lock.
        
        Args:
            lock_id: Unique lock identifier
            timeout: Maximum time to wait for lock acquisition
            metadata: Optional metadata to store with the lock
            
        Returns:
            bool: True if lock was acquired
            
        Raises:
            ValueError: If lock_id is empty or timeout is negative
            LockAcquisitionError: If lock acquisition fails
        """
        if not lock_id:
            raise ValueError("lock_id cannot be empty")
        if timeout is not None and timeout < 0:
            raise ValueError("timeout cannot be negative")
            
        with self._locks_mutex:
            if lock_id in self._active_locks:
                if self._verify_lock_ownership(lock_id):
                    return True
                self._cleanup_expired_lock(lock_id)
            
        start_time = time.time()
        attempts = 0
        
        while True:
            try:
                expires_at = int(time.time() + self.ttl_seconds)
                
                item: LockItem = {
                    'lock_id': lock_id,
                    'owner_id': self.owner_id,
                    'expires_at': expires_at,
                    'created_at': datetime.now(),
                    'last_renewed_at': None,
                    'metadata': metadata
                }

                current_status = self.get_lock_status(lock_id)
                if current_status.is_locked and current_status.owner_id != self.owner_id:
                    attempts += 1
                    if timeout and time.time() - start_time >= timeout:
                        raise LockAcquisitionError(lock_id, "Timeout waiting for lock")
                    if attempts >= self.retry_times:
                        raise LockAcquisitionError(lock_id, f"Failed after {attempts} attempts")
                    time.sleep(self.retry_delay)
                    continue
                
                self.dynamodb.put_item(
                    partition=self.PARTITION_NAME,
                    item=item,
                    can_overwrite=True
                )

                with self._locks_mutex:
                    self._active_locks[lock_id] = item
                    self._start_renewal_thread(lock_id)
                
                logger.debug(f"Acquired lock '{lock_id}'")
                return True

            except Exception as e:
                attempts += 1
                if timeout and time.time() - start_time >= timeout:
                    raise LockAcquisitionError(lock_id, "Timeout waiting for lock")
                if attempts >= self.retry_times:
                    raise LockAcquisitionError(lock_id, f"Failed after {attempts} attempts: {str(e)}")
                time.sleep(self.retry_delay)
                continue

    def _cleanup_expired_lock(self, lock_id: str) -> None:
        """Clean up an expired lock.
        
        Args:
            lock_id: Lock identifier to clean up
        """
        with self._locks_mutex:
            if lock_id in self._active_locks:
                self._stop_renewal_thread(lock_id)
                del self._active_locks[lock_id]

    def release(self, lock_id: str) -> None:
        """Release a distributed lock.
        
        Args:
            lock_id: Lock identifier to release
            
        Raises:
            LockReleaseError: If lock release fails
        """
        try:
            if not self._verify_lock_ownership(lock_id):
                logger.warning(f"Cannot release lock '{lock_id}': not owner or expired")
                return

            with self._locks_mutex:
                self._stop_renewal_thread(lock_id)

            self.dynamodb.delete_item(
                item_id=f"{self.PARTITION_NAME}#lock_id#{lock_id}&owner_id#S{self.owner_id}|"
            )
            
            with self._locks_mutex:
                if lock_id in self._active_locks:
                    del self._active_locks[lock_id]
            
            logger.debug(f"Released lock '{lock_id}'")

        except Exception as e:
            raise LockReleaseError(lock_id, str(e))

    def _renew_lock(self, lock_id: str) -> None:
        """Renew a lock's expiration time.
        
        Args:
            lock_id: Lock identifier to renew
            
        Raises:
            LockRenewalError: If renewal fails after retries
        """
        retry_count = 0
        while retry_count < self.retry_times:
            try:
                if not self._verify_lock_ownership(lock_id):
                    raise LockRenewalError(lock_id, "Lost lock ownership")
                    
                expires_at = int(time.time() + self.ttl_seconds)
                
                self.dynamodb.update_item(
                    partition=self.PARTITION_NAME,
                    item_id=f"{self.PARTITION_NAME}#lock_id#{lock_id}&owner_id#S{self.owner_id}|",
                    item={
                        'expires_at': expires_at,
                        'last_renewed_at': datetime.now()
                    }
                )

                logger.debug(f"Renewed lock '{lock_id}'")
                return

            except Exception as e:
                retry_count += 1
                if retry_count >= self.retry_times:
                    logger.warning(f"Failed to renew lock '{lock_id}': {e}")
                    with self._locks_mutex:
                        self._stop_renewal_thread(lock_id)
                    raise LockRenewalError(lock_id, str(e))
                time.sleep(self.retry_delay)

    def _renewal_worker(self, lock_id: str) -> None:
        """Background worker for lock renewal.
        
        Args:
            lock_id: Lock identifier to renew
        """
        while not self._shutdown.is_set():
            try:
                self._renew_lock(lock_id)
                self._shutdown.wait(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Error in renewal worker for lock '{lock_id}': {e}")
                break

    def _start_renewal_thread(self, lock_id: str) -> None:
        """Start a background thread for lock renewal.
        
        Args:
            lock_id: Lock identifier to renew
        """
        # This method should be called within _locks_mutex
        if lock_id not in self._renewal_threads:
            thread = threading.Thread(
                target=self._renewal_worker,
                args=(lock_id,),
                daemon=True
            )
            self._renewal_threads[lock_id] = thread
            thread.start()

    def _stop_renewal_thread(self, lock_id: str) -> None:
        """Stop the renewal thread for a lock.
        
        Args:
            lock_id: Lock identifier
        """
        # This method should be called within _locks_mutex
        if lock_id in self._renewal_threads:
            self._renewal_threads[lock_id].join(timeout=1.0)
            del self._renewal_threads[lock_id]

    @contextmanager
    def lock(
        self,
        lock_id: str,
        timeout: Optional[float] = None,
        metadata: Optional[dict] = None
    ):
        """Context manager for acquiring and releasing a lock.
        
        Args:
            lock_id: Lock identifier
            timeout: Maximum time to wait for lock acquisition
            metadata: Optional metadata to store with the lock
            
        Yields:
            None
            
        Example:
            ```python
            lock_config = LockConfig(
                table_name="my-table",
                ttl_seconds=60,
                retry_times=3
            )
            lock_manager = DistributedLock(lock_config)
            
            try:
                with lock_manager.lock("my-resource"):
                    # Critical section
                    process_resource()
            except LockAcquisitionError:
                # Handle lock acquisition failure
                pass
            ```
        """
        try:
            self.acquire(lock_id, timeout, metadata)
            yield
        finally:
            self.release(lock_id)

    def shutdown(self) -> None:
        """Shutdown the lock manager and release all locks."""
        self._shutdown.set()
        
        with self._locks_mutex:
            active_locks = list(self._active_locks.keys())
            
        for lock_id in active_locks:
            try:
                self.release(lock_id)
            except Exception as e:
                logger.error(f"Error releasing lock '{lock_id}' during shutdown: {e}")

        with self._locks_mutex:
            for thread in self._renewal_threads.values():
                thread.join(timeout=1.0)

            self._active_locks.clear()
            self._renewal_threads.clear()

    def __del__(self):
        """Ensure cleanup on object destruction."""
        try:
            self.shutdown()
        except Exception:
            pass

    async def async_acquire(
        self,
        lock_id: str,
        timeout: Optional[float] = None,
        metadata: Optional[dict] = None
    ) -> bool:
        """Async version of acquire.
        
        Args:
            lock_id: Unique lock identifier
            timeout: Maximum time to wait for lock acquisition
            metadata: Optional metadata to store with the lock
            
        Returns:
            bool: True if lock was acquired
            
        Raises:
            ValueError: If lock_id is empty or timeout is negative
            LockAcquisitionError: If lock acquisition fails
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.acquire(lock_id, timeout, metadata)
        )

    async def async_release(self, lock_id: str) -> None:
        """Async version of release.
        
        Args:
            lock_id: Lock identifier to release
            
        Raises:
            LockReleaseError: If lock release fails
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.release(lock_id)
        )

    @asynccontextmanager
    async def async_lock(
        self,
        lock_id: str,
        timeout: Optional[float] = None,
        metadata: Optional[dict] = None
    ):
        """Async context manager for acquiring and releasing a lock.
        
        Args:
            lock_id: Lock identifier
            timeout: Maximum time to wait for lock acquisition
            metadata: Optional metadata to store with the lock
            
        Yields:
            None
            
        Example:
            ```python
            async with lock_manager.async_lock("my-resource"):
                # Critical section
                await process_resource()
            ```
        """
        try:
            await self.async_acquire(lock_id, timeout, metadata)
            yield
        finally:
            await self.async_release(lock_id) 