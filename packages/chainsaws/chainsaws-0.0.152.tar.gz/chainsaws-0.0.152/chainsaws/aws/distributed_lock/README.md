# DynamoDB Distributed Lock

A robust distributed locking mechanism using AWS DynamoDB with automatic lock renewal, timeout handling, and thread-safe operations.

## Features

- 🔒 **Mutual Exclusion**

  - Guarantees only one process can hold a lock at a time
  - Thread-safe operations within the same process
  - Automatic conflict resolution

- ⏰ **Automatic Lock Renewal**

  - Background heartbeat mechanism to maintain locks
  - Configurable TTL and renewal intervals
  - Graceful handling of renewal failures

- 🛡️ **Fault Tolerance**

  - Process crash recovery through TTL expiration
  - Network partition handling with retry mechanisms
  - Deadlock prevention with timeout controls

- 🔄 **Async/Sync Support**

  - Full async/await support with `async_lock`
  - Synchronous operations for simple use cases
  - Context manager support for both modes

- 📊 **Lock Monitoring**

  - Real-time lock status checking
  - Owner identification and metadata storage
  - Expiration time tracking

- ⚡ **High Performance**
  - DynamoDB-backed for low latency
  - Optimized queries with consistent reads
  - Minimal overhead for lock operations

## Quick Start

### 1. Initialize the Lock Manager

```python
from chainsaws.aws.distributed_lock import DistributedLockAPI, LockConfig

# Basic configuration with minimal setup
config = LockConfig(
    table_name="my-locks-table"  # Only table name is required
)
lock_manager = DistributedLockAPI(config)

# Custom configuration with all options
config = LockConfig(
    table_name="my-locks-table",
    ttl_seconds=60,          # Lock expires after 60 seconds (default: 60)
    retry_times=3,           # Retry 3 times on failure (default: 3)
    retry_delay=1.0,         # Wait 1 second between retries (default: 1.0)
    heartbeat_interval=20,   # Renew lock every 20 seconds (default: ttl_seconds // 2)
    owner_id="unique-process-id"  # Custom owner ID (default: auto-generated UUID)
)
lock_manager = DistributedLockAPI(config)

# Initialize the lock table (call once per application)
lock_manager.init_lock()
```

### 2. Using Context Manager (Recommended)

```python
# Synchronous context manager
with lock_manager.lock("critical_resource", timeout=30.0):
    # Your critical section here
    process_important_data()
    # Lock is automatically released when exiting

# Asynchronous context manager
async with lock_manager.async_lock("async_resource", timeout=30.0):
    # Your async critical section here
    await process_important_data_async()
    # Lock is automatically released when exiting
```

### 3. Manual Lock Management

```python
# Manual acquire and release
try:
    success = lock_manager.acquire("my_resource", timeout=30.0)
    if success:
        print("Lock acquired successfully!")
        # Do your work here
        process_data()
    else:
        print("Failed to acquire lock")
finally:
    lock_manager.release("my_resource")

# Check lock status
status = lock_manager.get_lock_status("my_resource")
if status.is_locked:
    print(f"Lock held by: {status.owner_id}")
    print(f"Expires at: {status.expires_at}")
```

## Basic Usage Examples

### Simple Resource Protection

```python
from chainsaws.aws.distributed_lock import DistributedLockAPI, LockConfig

# Setup - minimal configuration
config = LockConfig(table_name="app-locks")
lock_manager = DistributedLockAPI(config)
lock_manager.init_lock()  # Initialize table (call once)

def process_shared_resource():
    """Process a shared resource safely across multiple processes."""
    resource_id = "shared_database_migration"

    try:
        with lock_manager.lock(resource_id, timeout=60.0):
            print("Starting database migration...")
            # Only one process will execute this at a time
            run_database_migration()
            print("Migration completed!")
    except LockAcquisitionError as e:
        print(f"Could not acquire lock: {e}")
        # Handle the case where another process is already working
```

### Async Operations

```python
import asyncio
from chainsaws.aws.distributed_lock import DistributedLockAPI, LockConfig

async def async_data_processing():
    """Async data processing with distributed lock."""
    config = LockConfig(table_name="async-locks")
    lock_manager = DistributedLockAPI(config)
    lock_manager.init_lock()  # Initialize table

    async with lock_manager.async_lock("data_sync", timeout=45.0):
        print("Starting async data sync...")
        await sync_data_from_external_api()
        await update_local_database()
        print("Data sync completed!")

# Run async function
asyncio.run(async_data_processing())
```

### Lock with Metadata

```python
def process_with_metadata():
    """Store metadata with the lock for debugging."""
    metadata = {
        "process_id": os.getpid(),
        "hostname": socket.gethostname(),
        "operation": "data_export",
        "started_at": datetime.now().isoformat()
    }

    with lock_manager.lock("data_export", timeout=300.0, metadata=metadata):
        print("Exporting data...")
        export_large_dataset()
        print("Export completed!")

# Check what process is holding the lock
status = lock_manager.get_lock_status("data_export")
if status.is_locked:
    print(f"Export in progress by: {status.metadata}")
```

## Error Handling

```python
from chainsaws.aws.distributed_lock import (
    DistributedLockAPI,
    LockConfig,
    LockAcquisitionError,
    LockReleaseError,
    LockRenewalError
)

def robust_lock_usage():
    """Comprehensive error handling for lock operations."""
    config = LockConfig(table_name="robust-locks")
    lock_manager = DistributedLockAPI(config)
    lock_manager.init_lock()  # Initialize table

    try:
        # Try to acquire lock with timeout
        success = lock_manager.acquire("critical_task", timeout=30.0)
        if not success:
            print("Lock acquisition timed out")
            return

        try:
            # Your critical work here
            perform_critical_operation()

        finally:
            # Always attempt to release
            lock_manager.release("critical_task")

    except LockAcquisitionError as e:
        print(f"Failed to acquire lock: {e}")
        # Handle acquisition failure (another process has the lock)

    except LockReleaseError as e:
        print(f"Failed to release lock: {e}")
        # Lock will expire automatically based on TTL

    except LockRenewalError as e:
        print(f"Lock renewal failed: {e}")
        # Lock may have been lost, stop critical operations

    except Exception as e:
        print(f"Unexpected error: {e}")
        # Always cleanup on unexpected errors
        try:
            lock_manager.release("critical_task")
        except:
            pass  # Best effort cleanup
```

## Advanced Configuration

### Custom AWS Configuration

```python
from chainsaws.aws.distributed_lock import DistributedLockAPI, LockConfig
from chainsaws.aws.shared.config import AWSCredentials

# Custom AWS credentials and settings
config = LockConfig(
    table_name="production-locks",
    ttl_seconds=300,           # 5 minutes
    retry_times=5,             # More retries for production
    retry_delay=2.0,           # Longer delay between retries
    heartbeat_interval=60,     # Renew every minute
    credentials=AWSCredentials(
        aws_access_key_id="YOUR_ACCESS_KEY",
        aws_secret_access_key="YOUR_SECRET_KEY"
    ),
    region="ap-northeast-2",   # Seoul region
    endpoint_url=None          # Use real DynamoDB (not local)
)

lock_manager = DistributedLockAPI(config)
```

### High-Availability Setup

```python
def create_ha_lock_manager():
    """Create a high-availability lock manager."""
    config = LockConfig(
        table_name="ha-distributed-locks",
        ttl_seconds=180,        # 3 minutes for HA
        retry_times=10,         # Many retries for network issues
        retry_delay=0.5,        # Quick retries
        heartbeat_interval=30,  # Frequent renewals
        region="us-west-2"      # Primary region
    )

    return DistributedLockAPI(config)

# Usage for critical systems
ha_lock = create_ha_lock_manager()

def critical_system_operation():
    """Critical operation with high availability."""
    with ha_lock.lock("system_maintenance", timeout=120.0):
        print("Performing system maintenance...")
        # Critical maintenance tasks
        update_system_configuration()
        restart_services()
        validate_system_health()
```

## Lock Status Monitoring

```python
def monitor_lock_status():
    """Monitor and report lock status."""
    resource_id = "background_processor"

    # Check current lock status
    status = lock_manager.get_lock_status(resource_id)

    if status.is_locked:
        print(f"🔒 Lock Status Report:")
        print(f"   Resource: {resource_id}")
        print(f"   Owner: {status.owner_id}")
        print(f"   Expires: {datetime.fromtimestamp(status.expires_at)}")
        print(f"   Last Renewed: {status.last_renewed_at}")

        if status.metadata:
            print(f"   Metadata: {status.metadata}")
    else:
        print(f"🔓 Resource '{resource_id}' is available")

# Continuous monitoring
import time

def watch_lock(resource_id, interval=10):
    """Watch a lock status continuously."""
    while True:
        status = lock_manager.get_lock_status(resource_id)

        if status.is_locked:
            remaining = status.expires_at - time.time()
            print(f"Lock held by {status.owner_id}, expires in {remaining:.1f}s")
        else:
            print(f"Lock available for {resource_id}")

        time.sleep(interval)
```

## Best Practices

### 1. **Lock Naming Convention**

```python
# Use descriptive, hierarchical lock names
def good_lock_names():
    # ✅ Good: Clear hierarchy and purpose
    with lock_manager.lock("database:migration:user_table"):
        migrate_user_table()

    with lock_manager.lock("cache:rebuild:product_catalog"):
        rebuild_product_cache()

    with lock_manager.lock("scheduled_job:daily_report"):
        generate_daily_report()

# ❌ Avoid: Generic or unclear names
def bad_lock_names():
    with lock_manager.lock("lock1"):  # Too generic
        pass

    with lock_manager.lock("temp"):   # Unclear purpose
        pass
```

### 2. **Timeout Configuration**

```python
def configure_timeouts_properly():
    """Configure timeouts based on operation duration."""

    # Short operations: aggressive timeout
    with lock_manager.lock("quick_cache_update", timeout=10.0):
        update_cache()  # Should complete in seconds

    # Medium operations: reasonable timeout
    with lock_manager.lock("data_processing", timeout=300.0):  # 5 minutes
        process_data_batch()

    # Long operations: generous timeout
    with lock_manager.lock("full_backup", timeout=3600.0):  # 1 hour
        create_full_backup()
```

### 3. **Error Recovery Patterns**

```python
def implement_retry_pattern():
    """Implement proper retry patterns."""
    max_attempts = 3
    base_delay = 2.0

    for attempt in range(max_attempts):
        try:
            with lock_manager.lock("retry_operation", timeout=30.0):
                perform_operation()
                break  # Success, exit retry loop

        except LockAcquisitionError:
            if attempt == max_attempts - 1:
                print("Failed to acquire lock after all attempts")
                raise

            # Exponential backoff
            delay = base_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
            time.sleep(delay)
```

### 4. **Graceful Shutdown**

```python
import signal
import sys

class GracefulLockManager:
    """Lock manager with graceful shutdown."""

    def __init__(self, config):
        self.lock_manager = DistributedLockAPI(config)
        self.active_locks = set()

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print("Received shutdown signal, cleaning up locks...")
        self.shutdown()
        sys.exit(0)

    def acquire_lock(self, resource_id, **kwargs):
        """Track acquired locks for cleanup."""
        success = self.lock_manager.acquire(resource_id, **kwargs)
        if success:
            self.active_locks.add(resource_id)
        return success

    def release_lock(self, resource_id):
        """Release and untrack locks."""
        self.lock_manager.release(resource_id)
        self.active_locks.discard(resource_id)

    def shutdown(self):
        """Clean shutdown of all locks."""
        for resource_id in list(self.active_locks):
            try:
                self.release_lock(resource_id)
                print(f"Released lock: {resource_id}")
            except Exception as e:
                print(f"Error releasing {resource_id}: {e}")

        self.lock_manager.shutdown()
```

## Configuration Reference

```python
from chainsaws.aws.distributed_lock import LockConfig

# Complete configuration example with all options
config = LockConfig(
    # Required
    table_name="my-locks",              # DynamoDB table name (default: "distributed-locks")

    # Lock behavior (all have defaults)
    ttl_seconds=60,                     # Lock expiration time (default: 60)
    retry_times=3,                      # Number of acquisition retries (default: 3)
    retry_delay=1.0,                    # Delay between retries in seconds (default: 1.0)
    heartbeat_interval=20,              # Lock renewal interval in seconds (default: ttl_seconds // 2)

    # AWS configuration (inherited from DynamoDBAPIConfig)
    credentials=None,                   # AWS credentials (default: None - use default chain)
    region="ap-northeast-2",           # AWS region (default: "ap-northeast-2")
    endpoint_url=None,                 # DynamoDB endpoint (default: None - use AWS)
    max_pool_connections=100,          # Connection pool size (default: 100)

    # Process identification
    owner_id=None                      # Unique owner ID (default: None - auto-generated UUID)
)

# Minimal configuration - only table name required
config_minimal = LockConfig(table_name="my-locks")
```

## Troubleshooting

### Common Issues

1. **Lock Not Being Released**

   ```python
   # Always use try/finally or context managers
   try:
       lock_manager.acquire("resource")
       # Your code here
   finally:
       lock_manager.release("resource")  # Always cleanup
   ```

2. **Frequent Lock Renewal Failures**

   ```python
   # Increase TTL and reduce heartbeat interval
   config = LockConfig(
       ttl_seconds=300,      # Longer TTL
       heartbeat_interval=60  # More frequent renewals
   )
   ```

3. **DynamoDB Table Not Found**
   ```python
   # The lock manager automatically creates the table
   # Ensure your AWS credentials have DynamoDB permissions:
   # - dynamodb:CreateTable
   # - dynamodb:PutItem
   # - dynamodb:GetItem
   # - dynamodb:UpdateItem
   # - dynamodb:DeleteItem
   # - dynamodb:Query
   ```

### Performance Considerations

- **TTL vs Performance**: Shorter TTL = faster recovery but more DynamoDB calls
- **Heartbeat Interval**: Should be 1/2 to 1/3 of TTL for safety
- **Retry Strategy**: Balance between responsiveness and DynamoDB costs
- **Regional Latency**: Use the closest AWS region for better performance

## Important Notes

1. **Lock Expiration**: Locks automatically expire based on TTL to prevent deadlocks
2. **Thread Safety**: Safe to use within multi-threaded applications
3. **Process Isolation**: Each process gets a unique owner ID for lock identification
4. **Network Partitions**: Locks may be lost during network issues, always handle gracefully
5. **DynamoDB Costs**: Each lock operation results in DynamoDB read/write operations

## Migration and Deployment

When deploying distributed locks in production:

1. **Test Thoroughly**: Test lock behavior under network failures
2. **Monitor Metrics**: Track lock acquisition times and renewal failures
3. **Set Alerts**: Alert on excessive lock acquisition failures
4. **Capacity Planning**: Ensure DynamoDB table has adequate capacity
5. **Backup Strategy**: Consider backup/restore procedures for lock table
