# AWS Redshift API

A high-level Python API wrapper for AWS Redshift that provides an intuitive interface for database operations and cluster management.

## Key Features

### Data Plane Operations

- **Query Execution**

  - Synchronous/Asynchronous query execution
  - Type-safe results
  - Fluent query builder for all query types
  - Execution plan analysis and query optimization

- **Batch Operations**

  - Efficient bulk inserts/updates
  - Data load/unload via S3
  - Retry logic and error handling
  - Parallel processing support

- **Performance Monitoring**

  - Query execution metrics
  - Resource usage tracking
  - Bottleneck identification
  - Performance analysis reports

- **Security**
  - IAM authentication
  - Temporary credential management
  - Token-based access control
  - Encrypted credential storage

### Control Plane Operations

- **Cluster Management**

  - Create/modify/delete clusters
  - Status monitoring
  - Snapshot management
  - Resize operations

- **Security Management**

  - IAM role management
  - Security group configuration
  - User/group management
  - Permission control

- **Parameter Management**
  - Parameter group management
  - Configuration modifications
  - Default value management
  - Change tracking

## Usage Examples

### Basic Query Execution

```python
from chainsaws.aws.redshift import RedshiftAPI, RedshiftAPIConfig

# Initialize API
config = RedshiftAPIConfig(
    host="your-cluster.region.redshift.amazonaws.com",
    port=5439,
    database="dev",
    aws_access_key_id="your-access-key",
    aws_secret_access_key="your-secret-key"
)
api = RedshiftAPI(config)

# Execute query
result = await api.execute_query(
    "SELECT * FROM users WHERE age > %(min_age)s",
    parameters={"min_age": 25}
)

# Process results
for row in result.result_rows:
    print(row)
```

### Using Query Builder

```python
from chainsaws.aws.redshift import (
    QueryBuilder,
    QueryType,
    JoinType,
    OrderDirection,
    AggregateFunction
)

# SELECT query
query = (QueryBuilder("users")
    .select("users.id", "users.name", "orders.total")
    .join("orders", "users.id = orders.user_id", JoinType.LEFT)
    .where("users.age > {}", 25)
    .group_by("users.id", "users.name")
    .having("SUM(orders.total) > {}", 1000)
    .order_by("users.name", OrderDirection.ASC)
    .limit(10))

# INSERT query
query = (QueryBuilder("users", QueryType.INSERT)
    .values({
        "id": 1,
        "name": "John",
        "email": "john@example.com"
    })
    .on_conflict("id", action="update"))

# UPDATE query
query = (QueryBuilder("users", QueryType.UPDATE)
    .set({
        "status": "inactive",
        "updated_at": "2024-01-01"
    })
    .where("last_login < {}", "2023-12-01"))

# DELETE query
query = (QueryBuilder("users", QueryType.DELETE)
    .where("status = {}", "inactive"))

# Execute query
result = await api.execute_query(*query.build())
```

### Batch Operations

```python
from chainsaws.aws.redshift import BatchConfig, BatchProcessor

# Configure batch processor
config = BatchConfig(
    batch_size=1000,
    parallel_workers=5,
    max_retries=3
)
processor = BatchProcessor(config)

# Bulk insert
result = await processor.batch_insert(
    connection,
    "users",
    ["id", "name", "email"],
    [[1, "User1", "user1@example.com"],
     [2, "User2", "user2@example.com"]]
)
```

### Performance Monitoring

```python
from chainsaws.aws.redshift import QueryMonitor, ResourceMonitor, PerformanceAnalyzer

# Setup monitoring
query_monitor = QueryMonitor()
resource_monitor = ResourceMonitor()
analyzer = PerformanceAnalyzer(query_monitor, resource_monitor)

# Analyze performance
patterns = analyzer.analyze_query_patterns()
bottlenecks = analyzer.identify_bottlenecks()
```

## Installation

```bash
pip install chainsaws
```

## Dependencies

- Python 3.12+
- asyncio
- boto3
- psycopg2-binary

## License

MIT License
