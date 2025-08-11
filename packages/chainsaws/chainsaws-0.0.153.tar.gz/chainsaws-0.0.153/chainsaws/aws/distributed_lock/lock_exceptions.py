"""Exceptions for distributed locking mechanism."""

class LockError(Exception):
    """Base exception for lock-related errors."""
    pass

class LockAcquisitionError(LockError):
    """Raised when lock acquisition fails."""
    def __init__(self, lock_id: str, reason: str):
        self.lock_id = lock_id
        self.reason = reason
        super().__init__(f"Failed to acquire lock '{lock_id}': {reason}")

class LockReleaseError(LockError):
    """Raised when lock release fails."""
    def __init__(self, lock_id: str, reason: str):
        self.lock_id = lock_id
        self.reason = reason
        super().__init__(f"Failed to release lock '{lock_id}': {reason}")

class LockRenewalError(LockError):
    """Raised when lock renewal fails."""
    def __init__(self, lock_id: str, reason: str):
        self.lock_id = lock_id
        self.reason = reason
        super().__init__(f"Failed to renew lock '{lock_id}': {reason}") 