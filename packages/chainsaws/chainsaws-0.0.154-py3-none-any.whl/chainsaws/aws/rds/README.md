# AWS RDS Module

High-level interface for AWS RDS (Relational Database Service) and RDS Data API operations. This module provides a simplified and type-safe way to manage RDS instances and interact with databases using the Data API.

## Features

### Instance Management

- Create and delete RDS instances
- Modify instance configurations (scaling, storage, etc.)
- Instance status monitoring
- Multi-AZ deployment support
- Parameter group management
- Security group management

### Database Operations

- Execute SQL queries using Data API
- Transaction management
- Batch operations support
- Performance Insights integration
- Log retrieval and analysis

### Backup & Recovery

- Automated and manual snapshots
- Point-in-time recovery
- Cross-region backup copying
- Backup window configuration
- Retention period management

### Monitoring & Events

- Performance metrics collection
- Event subscription management
- CloudWatch integration
- Log streaming and analysis

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.aws.rds import RDSAPI, DatabaseInstanceConfig, DatabaseEngine, InstanceClass

# Initialize RDS API
rds = RDSAPI()

# Create a new RDS instance
instance = rds.create_instance(
    DatabaseInstanceConfig(
        instance_identifier="my-db",
        engine=DatabaseEngine.POSTGRESQL,
        instance_class=InstanceClass.SMALL,
        master_username="admin",
        master_password="secret123",
        vpc_security_group_ids=["sg-1234567890"]
    )
)

# Execute a query using Data API
result = rds.execute_query(
    resource_arn="arn:aws:rds:region:account:cluster:my-cluster",
    secret_arn="arn:aws:secretsmanager:region:account:secret:my-secret",
    database="mydb",
    sql="SELECT * FROM users WHERE age > :age",
    parameters=[{'name': 'age', 'value': {'longValue': 18}}]
)

# Create a backup
backup = rds.create_backup(
    instance_identifier="my-db",
    backup_identifier="my-db-backup-20240101",
    tags={"Environment": "Production"}
)
```

## Detailed Usage

### Instance Management

```python
# Create an instance
instance = rds.create_instance(config)

# Modify instance
modified = rds.modify_instance(
    instance_identifier="my-db",
    instance_class=InstanceClass.LARGE,
    allocated_storage=100,
    apply_immediately=True
)

# Delete instance
rds.delete_instance(
    "my-db",
    skip_final_snapshot=False,
    final_snapshot_identifier="my-db-final"
)
```

### Database Operations

```python
# Transaction management using context manager
with rds.transaction(config) as transaction_id:
    result = rds.execute_query(
        resource_arn=config.resource_arn,
        secret_arn=config.secret_arn,
        database="mydb",
        sql="INSERT INTO users (name) VALUES (:name)",
        parameters=[{'name': 'name', 'value': {'stringValue': 'John'}}],
        transaction_id=transaction_id
    )

# Batch operations
result = rds.batch_execute(
    resource_arn="arn:aws:rds:region:account:cluster:my-cluster",
    secret_arn="arn:aws:secretsmanager:region:account:secret:my-secret",
    database="mydb",
    sql="INSERT INTO users (name, age) VALUES (:name, :age)",
    parameter_sets=[
        [
            {'name': 'name', 'value': {'stringValue': 'John'}},
            {'name': 'age', 'value': {'longValue': 30}}
        ],
        [
            {'name': 'name', 'value': {'stringValue': 'Jane'}},
            {'name': 'age', 'value': {'longValue': 25}}
        ]
    ]
)
```

### Backup & Recovery

```python
# Create backup
backup = rds.create_backup(
    instance_identifier="my-db",
    backup_identifier="my-db-backup-20240101",
    tags={"Environment": "Production"}
)

# Restore from backup
restored = rds.restore_from_backup(
    snapshot_identifier="my-db-backup-20240101",
    target_instance_identifier="my-db-restored",
    instance_class=InstanceClass.MEDIUM
)

# Configure backup window
rds.configure_backup_window(
    instance_identifier="my-db",
    preferred_window="03:00-04:00",  # UTC
    retention_period=14
)
```

### Monitoring & Events

```python
# Create event subscription
subscription = rds.create_event_subscription(
    name="my-db-events",
    sns_topic_arn="arn:aws:sns:region:account:topic",
    categories=[
        EventCategory.FAILURE,
        EventCategory.MAINTENANCE
    ],
    source_type="db-instance",
    source_ids=["my-db"]
)

# Get performance insights
metrics = rds.get_performance_insights(
    instance_identifier="my-db",
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now(),
    metric_queries=[{
        'Metric': 'db.load.avg',
        'GroupBy': {'Group': 'db.wait_event'}
    }]
)
```

## API Reference

### Instance Management

#### create_instance

Create a new RDS instance.

```python
def create_instance(
    self,
    config: DatabaseInstanceConfig
) -> DatabaseInstance:
```

Parameters:

- `config`: Instance configuration including:
  - `instance_identifier`: Unique instance identifier
  - `engine`: Database engine (e.g., POSTGRESQL, MYSQL)
  - `instance_class`: Instance type (e.g., T3_MICRO, M5_LARGE)
  - `master_username`: Admin username
  - `master_password`: Admin password
  - `vpc_security_group_ids`: List of security group IDs
  - `allocated_storage`: Storage size in GB (default: 20)
  - Other optional parameters (availability_zone, subnet_group, etc.)

#### modify_instance

Modify an existing RDS instance.

```python
def modify_instance(
    self,
    instance_identifier: str,
    instance_class: Optional[InstanceClass] = None,
    allocated_storage: Optional[int] = None,
    apply_immediately: bool = False,
    **kwargs
) -> DatabaseInstance:
```

### Database Operations

#### execute_query

Execute a single SQL query using Data API.

```python
def execute_query(
    self,
    resource_arn: str,
    secret_arn: str,
    database: str,
    sql: str,
    parameters: Optional[List[Dict[str, Any]]] = None,
    schema: Optional[str] = None,
    transaction_id: Optional[str] = None
) -> QueryResult:
```

#### batch_execute

Execute SQL statements in batch mode.

```python
def batch_execute(
    self,
    resource_arn: str,
    secret_arn: str,
    database: str,
    sql: str,
    parameter_sets: List[List[Dict[str, Any]]],
    schema: Optional[str] = None,
    transaction_id: Optional[str] = None
) -> BatchExecuteResult:
```

#### transaction

Transaction context manager.

```python
@contextlib.contextmanager
def transaction(
    self,
    config: TransactionConfig
) -> Generator[str, None, None]:
```

### Backup & Recovery

#### create_backup

Create a manual backup/snapshot.

```python
def create_backup(
    self,
    instance_identifier: str,
    backup_identifier: str,
    tags: Optional[Dict[str, str]] = None,
    backup_type: BackupType = BackupType.MANUAL
) -> Dict[str, Any]:
```

#### restore_from_backup

Restore a database from backup.

```python
def restore_from_backup(
    self,
    source_identifier: str,
    target_identifier: str,
    instance_class: Optional[InstanceClass] = None,
    **kwargs
) -> DatabaseInstance:
```

#### restore_to_point_in_time

Restore a database to a specific point in time.

```python
def restore_to_point_in_time(
    self,
    source_identifier: str,
    target_identifier: str,
    point_in_time: datetime,
    **kwargs
) -> DatabaseInstance:
```

### Monitoring & Events

#### get_performance_insights

Get Performance Insights metrics.

```python
def get_performance_insights(
    self,
    instance_identifier: str,
    start_time: datetime,
    end_time: datetime,
    metric_queries: List[Dict[str, Any]],
    max_results: Optional[int] = None
) -> Dict[str, Any]:
```

#### create_event_subscription

Create an event subscription.

```python
def create_event_subscription(
    self,
    name: str,
    sns_topic_arn: str,
    categories: List[EventCategory],
    source_type: Optional[str] = None,
    source_ids: Optional[List[str]] = None,
    tags: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
```

### Data Models

#### DatabaseEngine (Enum)

Supported database engines:

```python
class DatabaseEngine(str, Enum):
    AURORA_MYSQL = "aurora-mysql"
    AURORA_POSTGRESQL = "aurora-postgresql"
    MYSQL = "mysql"
    POSTGRESQL = "postgres"
    MARIADB = "mariadb"
    ORACLE_SE = "oracle-se"
    ORACLE_SE1 = "oracle-se1"
    ORACLE_SE2 = "oracle-se2"
    ORACLE_EE = "oracle-ee"
    SQLSERVER_SE = "sqlserver-se"
    SQLSERVER_EX = "sqlserver-ex"
    SQLSERVER_WEB = "sqlserver-web"
    SQLSERVER_EE = "sqlserver-ee"
```

#### InstanceClass (Enum)

Available instance types:

```python
class InstanceClass(str, Enum):
    # Burstable Performance Instances
    T3_MICRO = "db.t3.micro"
    T3_SMALL = "db.t3.small"
    # ... more instance types ...

    # General Purpose Instances
    M5_LARGE = "db.m5.large"
    M5_XLARGE = "db.m5.xlarge"
    # ... more instance types ...

    # Memory Optimized Instances
    R5_LARGE = "db.r5.large"
    R5_XLARGE = "db.r5.xlarge"
    # ... more instance types ...
```

### Common Use Cases

#### Creating a New Database

```python
# Create instance configuration
config = DatabaseInstanceConfig(
    instance_identifier="my-db",
    engine=DatabaseEngine.POSTGRESQL,
    instance_class=InstanceClass.T3_MEDIUM,
    master_username="admin",
    master_password="secret123",
    vpc_security_group_ids=["sg-1234567890"],
    allocated_storage=50,
    tags={"Environment": "Production"}
)

# Create instance
instance = rds.create_instance(config)
```

#### Executing Queries with Transactions

```python
# Transaction configuration
config = TransactionConfig(
    resource_arn="arn:aws:rds:region:account:cluster:my-cluster",
    secret_arn="arn:aws:secretsmanager:region:account:secret:my-secret",
    database="mydb",
    schema="public"
)

# Execute queries in transaction
with rds.transaction(config) as transaction_id:
    # Insert data
    rds.execute_query(
        resource_arn=config.resource_arn,
        secret_arn=config.secret_arn,
        database=config.database,
        sql="INSERT INTO users (name, email) VALUES (:name, :email)",
        parameters=[
            {
                'name': 'name',
                'value': {'stringValue': 'John Doe'}
            },
            {
                'name': 'email',
                'value': {'stringValue': 'john@example.com'}
            }
        ],
        transaction_id=transaction_id
    )

    # Update data
    rds.execute_query(
        resource_arn=config.resource_arn,
        secret_arn=config.secret_arn,
        database=config.database,
        sql="UPDATE users SET status = :status WHERE email = :email",
        parameters=[
            {
                'name': 'status',
                'value': {'stringValue': 'active'}
            },
            {
                'name': 'email',
                'value': {'stringValue': 'john@example.com'}
            }
        ],
        transaction_id=transaction_id
    )
```

#### Automated Backup Management

```python
# Configure backup window
rds.configure_backup_window(
    instance_identifier="my-db",
    preferred_window="03:00-04:00",  # UTC
    retention_period=14
)

# Create manual backup
backup = rds.create_backup(
    instance_identifier="my-db",
    backup_identifier=f"my-db-backup-{datetime.now().strftime('%Y%m%d')}",
    tags={"Type": "Manual", "Environment": "Production"}
)

# List recent backups
backups = rds.list_backups(
    instance_identifier="my-db",
    backup_type=BackupType.AUTOMATED,
    start_time=datetime.utcnow() - timedelta(days=7)
)
```

### Error Handling

The module uses custom exceptions for different error cases:

```python
try:
    instance = rds.create_instance(config)
except RDSError as e:
    logger.error(f"Failed to create instance: {str(e)}")
    # Handle error appropriately
```

### Best Practices

1. Always use proper error handling
2. Use transactions for data consistency
3. Configure appropriate backup retention periods
4. Monitor instance performance
5. Use proper instance sizing
6. Implement proper security groups
7. Use parameter groups for database configuration
8. Enable automated backups
9. Use tags for resource management
10. Monitor costs and optimize resources

## Configuration

The module can be configured using `RDSAPIConfig`:

```python
from chainsaws.aws.rds import RDSAPI, RDSAPIConfig

rds = RDSAPI(
    config=RDSAPIConfig(
        region="ap-northeast-2",
        max_retries=5
    )
)
```

## Supported Database Engines

- Aurora MySQL
- Aurora PostgreSQL
- MySQL
- PostgreSQL
- MariaDB
- Oracle (SE, SE1, SE2, EE)
- SQL Server (SE, EX, WEB, EE)

## Error Handling

All operations include proper error handling and logging. Errors are propagated as exceptions with meaningful error messages.

## Type Safety

The module uses dataclasses for configuration and data validation, ensuring type safety and proper parameter validation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
