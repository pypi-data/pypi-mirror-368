# DynamoDB High-Level Client

A high-level DynamoDB client that provides partition management, indexing, and simplified CRUD operations with type safety and comprehensive error handling.

## Features

- 🗄️ **Partition Management**

  - Create and manage logical partitions within a single table
  - Model-based partition configuration
  - Support for multiple indexes per partition

- 🛡️ **Type Safety**

  - Generic type support for all operations
  - Pydantic model integration
  - Automatic type validation and conversion

- 🔍 **Advanced Querying**

  - Type-safe filter expressions
  - Complex condition support (eq, neq, lt, gt, between, etc.)
  - Recursive filtering with AND/OR operations
  - Pagination support

- ⚡ **Batch Operations**

  - Bulk create/update/delete with type safety
  - Automatic batching and error handling
  - Parallel processing support

- 🔄 **Async Support**

  - Full async/await support with AsyncDynamoDBAPI
  - Identical interface to synchronous API
  - Enhanced performance for I/O-bound operations

- Dataclass integration

## Quick Start

### 1. Define Your Models

```python
from chainsaws.aws.dynamodb import DynamoModel, DynamoIndex
from dataclasses import dataclass

@dataclass(kw_only=True)
class User(DynamoModel):
    _partition = "user"
    _partition_key = "user_id"
    _sort_key = "email"
    _indexes = [
        DynamoIndex(pk="email", sk="user_id"),
        DynamoIndex(pk="status", sk="created_at")
    ]

    name: str
    email: str
    status: str
    created_at: int
```

### 2. Initialize Client and Apply Models

```python
from chainsaws.aws.dynamodb import DynamoDBAPI, AsyncDynamoDBAPI

# Synchronous client
db = DynamoDBAPI(table_name="my-table")

# Asynchronous client
async_db = AsyncDynamoDBAPI(table_name="my-table")

# Apply model configurations
db.apply_model_partitions(User)
```

### 3. Type-Safe Operations (Sync)

```python
# Create with type checking
user = User(
    name="John Doe",
    email="john@example.com",
    status="active",
    created_at=1234567890
)
created_user = db.put_item("user", user)  # Returns User instance

# Batch create with type safety
users = [
    User(name="Jane", email="jane@example.com"),
    User(name="Bob", email="bob@example.com")
]
created_users = db.put_items("user", users)  # Returns List[User]

# Type-safe querying
result, next_key = db.query_items(
    partition="user",
    filters=[
        {
            "field": "status",
            "value": "active",
            "condition": "eq"  # IDE autocomplete for conditions
        }
    ]
)
```

### 4. Type-Safe Operations (Async)

```python
# Create with type checking
user = User(
    name="John Doe",
    email="john@example.com",
    status="active",
    created_at=1234567890
)
created_user = await async_db.put_item("user", user)  # Returns User instance

# Batch create with type safety
users = [
    User(name="Jane", email="jane@example.com"),
    User(name="Bob", email="bob@example.com")
]
created_users = await async_db.put_items("user", users)  # Returns List[User]

# Type-safe querying
result, next_key = await async_db.query_items(
    partition="user",
    filters=[
        {
            "field": "status",
            "value": "active",
            "condition": "eq"
        }
    ]
)

# Async iteration over scan results
async for item in async_db.scan_table():
    print(item)
```

## Error Handling

```python
from chainsaws.aws.dynamodb.exceptions import (
    DynamoDBError,
    PartitionNotFoundError,
    BatchOperationError
)

try:
    db.put_items("user", users)  # or await async_db.put_items("user", users)
except BatchOperationError as e:
    print(f"Failed items: {e.failed_items}")
    print(f"Processed items: {e.processed_items}")
except PartitionNotFoundError as e:
    print(f"Partition not found: {e.partition_name}")
except DynamoDBError as e:
    print(f"Operation failed: {str(e)}")
```

## Important Notes

1. **Type Safety**

   - All operations are type-checked at runtime
   - IDE autocompletion support for filter conditions
   - Automatic conversion between models and DynamoDB format

2. **Batch Operations**

   - Automatic handling of DynamoDB batch size limits
   - Parallel processing for better performance
   - Consistent error handling and reporting

3. **Index Management**

   - Automatic index creation and status monitoring
   - Wait for index completion before proceeding
   - Up to 20 GSIs per table (AWS limit)

4. **Async Support**

   - All operations available in both sync and async versions
   - Same interface and features in both APIs
   - Better performance for I/O-bound operations
   - Seamless integration with async/await code

5. **Best Practices**
   - Use model-based configuration for type safety
   - Handle batch operation errors appropriately
   - Monitor index creation status for large operations
   - Choose sync/async API based on your application needs

## Configuration

```python
from chainsaws.aws.dynamodb import DynamoDBAPIConfig
from chainsaws.aws.shared.config import AWSCredentials

config = DynamoDBAPIConfig(
    credentials=AWSCredentials(
        aws_access_key_id="YOUR_ACCESS_KEY",
        aws_secret_access_key="YOUR_SECRET_KEY"
    ),
    region="ap-northeast-2",
    max_pool_connections=100
)

# Sync client
db = DynamoDBAPI(
    table_name="my-table",
    config=config
)

# Async client
async_db = AsyncDynamoDBAPI(
    table_name="my-table",
    config=config
)
```
