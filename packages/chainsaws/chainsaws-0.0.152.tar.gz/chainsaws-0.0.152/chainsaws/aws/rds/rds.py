"""High-level interface for AWS RDS and RDS Data Service operations."""


import contextlib
import logging
from collections.abc import Generator
from datetime import datetime
from typing import Any

from chainsaws.aws.rds._rds_internal import RDS
from chainsaws.aws.rds.rds_models import (
    BackupConfig,
    BackupType,
    BackupWindow,
    BatchExecuteResult,
    BatchExecuteStatementConfig,
    DatabaseInstance,
    DatabaseInstanceConfig,
    DBSnapshot,
    EventCategory,
    EventSubscriptionConfig,
    InstanceClass,
    LogType,
    MetricConfig,
    ModifyInstanceConfig,
    ParameterGroupConfig,
    PerformanceInsightConfig,
    QueryConfig,
    QueryResult,
    RDSAPIConfig,
    ReadReplicaConfig,
    RestoreConfig,
    SnapshotConfig,
    TransactionConfig,
)
from chainsaws.aws.shared import session

logger = logging.getLogger(__name__)


class RDSAPI:
    """High-level RDS and RDS Data Service API."""

    def __init__(
        self,
        config: RDSAPIConfig | None = None,
    ) -> None:
        """Initialize RDS API.

        Args:
            config: Optional API configuration

        Example:
            ```python
            rds = RDSAPI(
                config=RDSAPIConfig(
                    region="ap-northeast-2",
                    max_retries=5
                )
            )
            ```

        """
        self.config = config or RDSAPIConfig()

        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None,
        )

        self.rds = RDS(
            self.boto3_session,
            self.config.default_region,
        )

    def create_instance(
        self,
        config: DatabaseInstanceConfig,
    ) -> DatabaseInstance:
        """Create a new RDS instance.

        Args:
            config: Instance configuration

        Returns:
            Created instance details

        Example:
            ```python
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
            print(f"Created instance: {instance.endpoint}")
            ```

        """
        return self.rds.create_db_instance(config)

    def modify_instance(
        self,
        instance_identifier: str,
        instance_class: InstanceClass | None = None,
        allocated_storage: int | None = None,
        apply_immediately: bool = False,
        **kwargs,
    ) -> DatabaseInstance:
        """Modify RDS instance configuration.

        Args:
            instance_identifier: Instance to modify
            instance_class: New instance class
            allocated_storage: New storage size in GB
            apply_immediately: Apply changes immediately
            **kwargs: Additional modification parameters

        Returns:
            Modified instance details

        Example:
            ```python
            instance = rds.modify_instance(
                instance_identifier="my-db",
                instance_class=InstanceClass.LARGE,
                allocated_storage=100,
                apply_immediately=True,
                backup_retention_period=7
            )
            ```

        """
        config = ModifyInstanceConfig(
            instance_identifier=instance_identifier,
            instance_class=instance_class,
            allocated_storage=allocated_storage,
            apply_immediately=apply_immediately,
            **kwargs,
        )
        return self.rds.modify_instance(config)

    def delete_instance(
        self,
        instance_identifier: str,
        skip_final_snapshot: bool = False,
        final_snapshot_identifier: str | None = None,
    ) -> None:
        """Delete an RDS instance.

        Args:
            instance_identifier: Instance to delete
            skip_final_snapshot: Skip final snapshot if True
            final_snapshot_identifier: Name for final snapshot

        Example:
            ```python
            rds.delete_instance(
                "my-db",
                skip_final_snapshot=False,
                final_snapshot_identifier="my-db-final"
            )
            ```

        """
        self.rds.delete_db_instance(
            instance_identifier,
            skip_final_snapshot,
            final_snapshot_identifier,
        )

    def get_instance(self, instance_identifier: str) -> DatabaseInstance:
        """Get details of an RDS instance.

        Args:
            instance_identifier: Instance to describe

        Returns:
            Instance details

        Example:
            ```python
            instance = rds.get_instance("my-db")
            print(f"Status: {instance.status}")
            ```

        """
        return self.rds.get_db_instance(instance_identifier)

    def execute_query(
        self,
        resource_arn: str,
        secret_arn: str,
        database: str,
        sql: str,
        parameters: list[dict[str, Any]] | None = None,
        schema: str | None = None,
        transaction_id: str | None = None,
    ) -> QueryResult:
        """Execute a SQL query using RDS Data API.

        Args:
            resource_arn: RDS cluster/instance ARN
            secret_arn: Secrets Manager ARN containing credentials
            database: Target database name
            sql: SQL query to execute
            parameters: Optional query parameters
            schema: Optional schema name
            transaction_id: Optional transaction ID

        Returns:
            Query execution result

        Example:
            ```python
            result = rds.execute_query(
                resource_arn="arn:aws:rds:region:account:cluster:my-cluster",
                secret_arn="arn:aws:secretsmanager:region:account:secret:my-secret",
                database="mydb",
                sql="SELECT * FROM users WHERE age > :age",
                parameters=[{'name': 'age', 'value': {'longValue': 18}}]
            )
            for row in result.rows:
                print(row)
            ```

        """
        config = QueryConfig(
            resource_arn=resource_arn,
            secret_arn=secret_arn,
            database=database,
            sql=sql,
            parameters=parameters or [],
            schema=schema,
            transaction_id=transaction_id,
        )
        return self.rds.execute_statement(config)

    @contextlib.contextmanager
    def transaction(
        self,
        config: TransactionConfig,
    ) -> Generator[str, None, None]:
        """Start a new transaction using context manager.

        Args:
            config: Transaction configuration including resource ARN, secret ARN,
                   database name, schema, and isolation level

        Yields:
            Transaction ID

        Example:
            ```python
            config = TransactionConfig(
                resource_arn="arn:aws:rds:region:account:cluster:my-cluster",
                secret_arn="arn:aws:secretsmanager:region:account:secret:my-secret",
                database="mydb",
                schema="public",
                isolation_level="REPEATABLE_READ"
            )

            with rds.transaction(config) as transaction_id:
                rds.execute_query(
                    resource_arn=config.resource_arn,
                    secret_arn=config.secret_arn,
                    database=config.database,
                    sql="INSERT INTO users (name) VALUES (:name)",
                    parameters=[{'name': 'name', 'value': {'stringValue': 'John'}}],
                    transaction_id=transaction_id
                )
            ```

        """
        transaction_id = self.rds.begin_transaction(
            config.resource_arn,
            config.secret_arn,
            config.database,
            config.schema,
        )
        try:
            yield transaction_id
            self.rds.commit_transaction(
                config.resource_arn,
                config.secret_arn,
                transaction_id,
            )
        except Exception as e:
            logger.exception(f"Transaction failed, rolling back: {e!s}")
            self.rds.rollback_transaction(
                config.resource_arn,
                config.secret_arn,
                transaction_id,
            )
            raise

    def begin_transaction(
        self,
        config: TransactionConfig,
    ) -> str:
        """Begin a new transaction manually.

        Args:
            config: Transaction configuration including resource ARN, secret ARN,
                   database name, schema, and isolation level

        Returns:
            Transaction ID

        Example:
            ```python
            config = TransactionConfig(
                resource_arn="arn:aws:rds:region:account:cluster:my-cluster",
                secret_arn="arn:aws:secretsmanager:region:account:secret:my-secret",
                database="mydb",
                schema="public",
                isolation_level="SERIALIZABLE"
            )

            transaction_id = rds.begin_transaction(config)
            try:
                # Execute queries with transaction_id
                rds.commit_transaction(
                    config.resource_arn,
                    config.secret_arn,
                    transaction_id
                )
            except Exception:
                rds.rollback_transaction(
                    config.resource_arn,
                    config.secret_arn,
                    transaction_id
                )
            ```

        """
        return self.rds.begin_transaction(
            config.resource_arn,
            config.secret_arn,
            config.database,
            config.schema,
        )

    def commit_transaction(
        self,
        resource_arn: str,
        secret_arn: str,
        transaction_id: str,
    ) -> None:
        """Commit a transaction.

        Args:
            resource_arn: RDS cluster/instance ARN
            secret_arn: Secrets Manager ARN containing credentials
            transaction_id: Transaction to commit

        """
        self.rds.commit_transaction(resource_arn, secret_arn, transaction_id)

    def rollback_transaction(
        self,
        resource_arn: str,
        secret_arn: str,
        transaction_id: str,
    ) -> None:
        """Rollback a transaction.

        Args:
            resource_arn: RDS cluster/instance ARN
            secret_arn: Secrets Manager ARN containing credentials
            transaction_id: Transaction to rollback

        """
        self.rds.rollback_transaction(resource_arn, secret_arn, transaction_id)

    def create_snapshot(
        self,
        instance_identifier: str,
        snapshot_identifier: str,
        tags: dict[str, str] | None = None,
    ) -> DBSnapshot:
        """Create a snapshot of an RDS instance.

        Args:
            instance_identifier: Source instance identifier
            snapshot_identifier: Name for the new snapshot
            tags: Optional tags for the snapshot

        Returns:
            Created snapshot details

        Example:
            ```python
            snapshot = rds.create_snapshot(
                instance_identifier="my-db",
                snapshot_identifier="my-db-backup-20240101",
                tags={"Environment": "Production"}
            )
            print(f"Snapshot status: {snapshot.status}")
            ```

        """
        config = SnapshotConfig(
            snapshot_identifier=snapshot_identifier,
            instance_identifier=instance_identifier,
            tags=tags or {},
        )
        return self.rds.create_snapshot(config)

    def restore_from_snapshot(
        self,
        snapshot_identifier: str,
        target_instance_identifier: str,
        instance_class: InstanceClass | None = None,
    ) -> DatabaseInstance:
        """Restore a new RDS instance from a snapshot.

        Args:
            snapshot_identifier: Source snapshot identifier
            target_instance_identifier: Name for the new instance
            instance_class: Optional instance class for the new instance

        Returns:
            Created instance details

        Example:
            ```python
            instance = rds.restore_from_snapshot(
                snapshot_identifier="my-db-backup-20240101",
                target_instance_identifier="my-db-restored",
                instance_class=InstanceClass.MEDIUM
            )
            print(f"Restored instance endpoint: {instance.endpoint}")
            ```

        """
        return self.rds.restore_from_snapshot(
            snapshot_identifier,
            target_instance_identifier,
            instance_class.value if instance_class else None,
        )

    def create_parameter_group(
        self,
        name: str,
        family: str,
        description: str,
        parameters: dict[str, str] | None = None,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create a new DB parameter group.

        Args:
            name: Parameter group name
            family: Parameter group family (e.g., 'postgres13')
            description: Parameter group description
            parameters: Optional parameter settings
            tags: Optional tags

        Returns:
            Created parameter group details

        Example:
            ```python
            param_group = rds.create_parameter_group(
                name="my-postgres-params",
                family="postgres13",
                description="Custom PostgreSQL parameters",
                parameters={
                    "max_connections": "200",
                    "shared_buffers": "4GB"
                }
            )
            ```

        """
        config = ParameterGroupConfig(
            group_name=name,
            family=family,
            description=description,
            parameters=parameters or {},
            tags=tags or {},
        )
        return self.rds.create_parameter_group(config)

    def get_instance_metrics(
        self,
        instance_identifier: str,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        period: int = 60,
        statistics: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get CloudWatch metrics for an RDS instance.

        Args:
            instance_identifier: Instance to monitor
            metric_name: Metric to retrieve (e.g., 'CPUUtilization')
            start_time: Start time for metrics
            end_time: End time for metrics
            period: Period in seconds (default: 60)
            statistics: Statistics to retrieve (default: ['Average'])

        Returns:
            List of metric datapoints

        Example:
            ```python
            from datetime import datetime, timedelta

            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)

            metrics = rds.get_instance_metrics(
                instance_identifier="my-db",
                metric_name="CPUUtilization",
                start_time=start_time,
                end_time=end_time,
                period=300,  # 5-minute intervals
                statistics=["Average", "Maximum"]
            )
            for point in metrics:
                print(f"Time: {point['Timestamp']}, CPU: {point['Average']}%")
            ```

        """
        config = MetricConfig(
            instance_identifier=instance_identifier,
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            period=period,
            statistics=statistics or ["Average"],
        )
        return self.rds.get_instance_metrics(config)

    def create_read_replica(
        self,
        source_instance_identifier: str,
        replica_identifier: str,
        availability_zone: str | None = None,
        instance_class: InstanceClass | None = None,
        port: int | None = None,
        tags: dict[str, str] | None = None,
    ) -> DatabaseInstance:
        """Create a read replica of an RDS instance.

        Args:
            source_instance_identifier: Source instance identifier
            replica_identifier: Name for the new replica
            availability_zone: Optional AZ for the replica
            instance_class: Optional instance class for the replica
            port: Optional port for the replica
            tags: Optional tags for the replica

        Returns:
            Created replica instance details

        Example:
            ```python
            replica = rds.create_read_replica(
                source_instance_identifier="my-db",
                replica_identifier="my-db-replica",
                instance_class=InstanceClass.SMALL,
                tags={"Role": "ReadReplica"}
            )
            print(f"Replica endpoint: {replica.endpoint}")
            ```

        """
        config = ReadReplicaConfig(
            source_instance_identifier=source_instance_identifier,
            replica_identifier=replica_identifier,
            availability_zone=availability_zone,
            instance_class=instance_class,
            port=port,
            tags=tags or {},
        )
        return self.rds.create_read_replica(config)

    def batch_execute(
        self,
        resource_arn: str,
        secret_arn: str,
        database: str,
        sql: str,
        parameter_sets: list[list[dict[str, Any]]],
        schema: str | None = None,
        transaction_id: str | None = None,
    ) -> BatchExecuteResult:
        """Execute a SQL statement in batch mode.

        Args:
            resource_arn: RDS cluster/instance ARN
            secret_arn: Secrets Manager ARN containing credentials
            database: Target database name
            sql: SQL statement to execute
            parameter_sets: List of parameter sets for batch execution
            schema: Optional schema name
            transaction_id: Optional transaction ID

        Returns:
            Batch execution results

        Example:
            ```python
            # Insert multiple users
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
            print(f"Generated IDs: {result.generated_fields}")
            ```

        """
        config = BatchExecuteStatementConfig(
            resource_arn=resource_arn,
            secret_arn=secret_arn,
            database=database,
            sql=sql,
            parameter_sets=parameter_sets,
            schema=schema,
            transaction_id=transaction_id,
        )
        return self.rds.batch_execute_statement(config)

    def bulk_insert(
        self,
        resource_arn: str,
        secret_arn: str,
        database: str,
        table: str,
        records: list[dict[str, Any]],
        schema: str | None = None,
        transaction_id: str | None = None,
    ) -> BatchExecuteResult:
        """Helper method for bulk inserting records into a table.

        Args:
            resource_arn: RDS cluster/instance ARN
            secret_arn: Secrets Manager ARN containing credentials
            database: Target database name
            table: Target table name
            records: List of records to insert
            schema: Optional schema name
            transaction_id: Optional transaction ID

        Returns:
            Batch execution results

        Example:
            ```python
            result = rds.bulk_insert(
                resource_arn="arn:aws:rds:region:account:cluster:my-cluster",
                secret_arn="arn:aws:secretsmanager:region:account:secret:my-secret",
                database="mydb",
                table="users",
                records=[
                    {"name": "John", "age": 30},
                    {"name": "Jane", "age": 25}
                ]
            )
            ```

        """
        if not records:
            return BatchExecuteResult()

        columns = list(records[0].keys())
        placeholders = [f":{col}" for col in columns]

        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({
            ', '.join(placeholders)})"

        parameter_sets = []
        for record in records:
            params = []
            for col in columns:
                value = record[col]
                param = {"name": col, "value": {}}

                # Determine value type
                if isinstance(value, int):
                    param["value"]["longValue"] = value
                elif isinstance(value, float):
                    param["value"]["doubleValue"] = value
                elif isinstance(value, bool):
                    param["value"]["booleanValue"] = value
                elif value is None:
                    param["value"]["isNull"] = True
                else:
                    param["value"]["stringValue"] = str(value)

                params.append(param)
            parameter_sets.append(params)

        return self.batch_execute(
            resource_arn=resource_arn,
            secret_arn=secret_arn,
            database=database,
            sql=sql,
            parameter_sets=parameter_sets,
            schema=schema,
            transaction_id=transaction_id,
        )

    def bulk_update(
        self,
        resource_arn: str,
        secret_arn: str,
        database: str,
        table: str,
        records: list[dict[str, Any]],
        key_columns: list[str],
        schema: str | None = None,
        transaction_id: str | None = None,
    ) -> BatchExecuteResult:
        """Helper method for bulk updating records in a table.

        Args:
            resource_arn: RDS cluster/instance ARN
            secret_arn: Secrets Manager ARN containing credentials
            database: Target database name
            table: Target table name
            records: List of records to update
            key_columns: List of column names that form the key
            schema: Optional schema name
            transaction_id: Optional transaction ID

        Returns:
            Batch execution results

        Example:
            ```python
            result = rds.bulk_update(
                resource_arn="arn:aws:rds:region:account:cluster:my-cluster",
                secret_arn="arn:aws:secretsmanager:region:account:secret:my-secret",
                database="mydb",
                table="users",
                records=[
                    {"id": 1, "name": "John Updated", "age": 31},
                    {"id": 2, "name": "Jane Updated", "age": 26}
                ],
                key_columns=["id"]
            )
            ```

        """
        if not records:
            return BatchExecuteResult()

        update_columns = [
            col for col in records[0] if col not in key_columns]

        set_clause = ", ".join([f"{col} = :{col}" for col in update_columns])
        where_clause = " AND ".join([f"{col} = :{col}" for col in key_columns])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        parameter_sets = []
        for record in records:
            params = []
            for col in update_columns + key_columns:
                value = record[col]
                param = {"name": col, "value": {}}

                # Determine value type
                if isinstance(value, int):
                    param["value"]["longValue"] = value
                elif isinstance(value, float):
                    param["value"]["doubleValue"] = value
                elif isinstance(value, bool):
                    param["value"]["booleanValue"] = value
                elif value is None:
                    param["value"]["isNull"] = True
                else:
                    param["value"]["stringValue"] = str(value)

                params.append(param)
            parameter_sets.append(params)

        return self.batch_execute(
            resource_arn=resource_arn,
            secret_arn=secret_arn,
            database=database,
            sql=sql,
            parameter_sets=parameter_sets,
            schema=schema,
            transaction_id=transaction_id,
        )

    def get_performance_insights(
        self,
        instance_identifier: str,
        start_time: datetime,
        end_time: datetime,
        metric_queries: list[dict[str, Any]],
        max_results: int | None = None,
    ) -> dict[str, Any]:
        """Get Performance Insights metrics.

        Args:
            instance_identifier: Target instance
            start_time: Start time for metrics
            end_time: End time for metrics
            metric_queries: Performance metric queries
            max_results: Maximum number of results

        Returns:
            Performance metrics data

        Example:
            ```python
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

        """
        config = PerformanceInsightConfig(
            instance_identifier=instance_identifier,
            start_time=start_time,
            end_time=end_time,
            metric_queries=metric_queries,
            max_results=max_results,
        )
        return self.rds.get_performance_insights(config)

    def get_logs(
        self,
        instance_identifier: str,
        log_type: LogType,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        max_lines: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get database logs.

        Args:
            instance_identifier: Target instance
            log_type: Type of logs to retrieve
            start_time: Optional start time filter
            end_time: Optional end time filter
            max_lines: Maximum number of log lines

        Returns:
            List of log entries

        Example:
            ```python
            logs = rds.get_logs(
                instance_identifier="my-db",
                log_type=LogType.ERROR,
                max_lines=1000
            )
            for log in logs:
                print(f"{log['timestamp']}: {log['message']}")
            ```

        """
        return self.rds.get_logs(
            instance_identifier,
            log_type,
            start_time,
            end_time,
            max_lines,
        )

    def create_event_subscription(
        self,
        name: str,
        sns_topic_arn: str,
        categories: list[EventCategory],
        source_type: str | None = None,
        source_ids: list[str] | None = None,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create an event subscription.

        Args:
            name: Subscription name
            sns_topic_arn: SNS topic ARN
            categories: Event categories to subscribe to
            source_type: Optional source type
            source_ids: Optional source identifiers
            tags: Optional tags

        Returns:
            Created subscription details

        Example:
            ```python
            subscription = rds.create_event_subscription(
                name="my-db-events",
                sns_topic_arn="arn:aws:sns:region:account:topic",
                categories=[
                    EventCategory.FAILURE,
                    EventCategory.MAINTENANCE
                ],
                source_type="db-instance",
                source_ids=["my-db"],
                tags={"Environment": "Production"}
            )
            ```

        """
        config = EventSubscriptionConfig(
            subscription_name=name,
            sns_topic_arn=sns_topic_arn,
            source_type=source_type,
            event_categories=set(categories),
            source_ids=source_ids or [],
            tags=tags or {},
        )
        return self.rds.create_event_subscription(config)

    def create_backup(
        self,
        instance_identifier: str,
        backup_identifier: str,
        tags: dict[str, str] | None = None,
        backup_type: BackupType = BackupType.MANUAL,
    ) -> dict[str, Any]:
        """Create a database backup/snapshot.

        Args:
            instance_identifier: Source instance identifier
            backup_identifier: Name for the backup
            tags: Optional tags for the backup
            backup_type: Type of backup to create

        Returns:
            Created backup details

        Example:
            ```python
            backup = rds.create_backup(
                instance_identifier="my-db",
                backup_identifier="my-db-backup-20240101",
                tags={"Environment": "Production"},
                backup_type=BackupType.MANUAL
            )
            ```

        """
        config = BackupConfig(
            instance_identifier=instance_identifier,
            backup_identifier=backup_identifier,
            tags=tags or {},
            backup_type=backup_type,
        )
        return self.rds.create_backup(config)

    def restore_from_backup(
        self,
        source_identifier: str,
        target_identifier: str,
        instance_class: InstanceClass | None = None,
        **kwargs,
    ) -> DatabaseInstance:
        """Restore a database from backup.

        Args:
            source_identifier: Source backup identifier
            target_identifier: Name for the restored instance
            instance_class: Optional instance class for restored instance
            **kwargs: Additional restore configuration

        Returns:
            Restored instance details

        Example:
            ```python
            instance = rds.restore_from_backup(
                source_identifier="my-db-backup-20240101",
                target_identifier="my-db-restored",
                instance_class=InstanceClass.MEDIUM,
                multi_az=True,
                tags={"Environment": "Production"}
            )
            ```

        """
        config = RestoreConfig(
            source_identifier=source_identifier,
            target_identifier=target_identifier,
            instance_class=instance_class,
            **kwargs,
        )
        return self.rds.restore_from_backup(config)

    def restore_to_point_in_time(
        self,
        source_identifier: str,
        target_identifier: str,
        point_in_time: datetime,
        **kwargs,
    ) -> DatabaseInstance:
        """Restore a database to a specific point in time.

        Args:
            source_identifier: Source instance identifier
            target_identifier: Name for the restored instance
            point_in_time: Timestamp to restore to
            **kwargs: Additional restore configuration

        Returns:
            Restored instance details

        Example:
            ```python
            from datetime import datetime, timedelta

            # Restore to 1 hour ago
            restore_time = datetime.utcnow() - timedelta(hours=1)

            instance = rds.restore_to_point_in_time(
                source_identifier="my-db",
                target_identifier="my-db-restored",
                point_in_time=restore_time,
                instance_class=InstanceClass.MEDIUM
            )
            ```

        """
        config = RestoreConfig(
            source_identifier=source_identifier,
            target_identifier=target_identifier,
            point_in_time=point_in_time,
            **kwargs,
        )
        return self.rds.restore_to_point_in_time(config)

    def configure_backup_window(
        self,
        instance_identifier: str,
        preferred_window: str,
        retention_period: int = 7,
    ) -> DatabaseInstance:
        """Configure backup window and retention period.

        Args:
            instance_identifier: Target instance
            preferred_window: Preferred backup window (UTC)
            retention_period: Backup retention period in days

        Returns:
            Updated instance details

        Example:
            ```python
            instance = rds.configure_backup_window(
                instance_identifier="my-db",
                preferred_window="03:00-04:00",  # UTC
                retention_period=14
            )
            ```

        """
        config = BackupWindow(
            instance_identifier=instance_identifier,
            preferred_window=preferred_window,
            retention_period=retention_period,
        )
        return self.rds.configure_backup_window(config)

    def list_backups(
        self,
        instance_identifier: str | None = None,
        backup_type: BackupType | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """List available backups/snapshots.

        Args:
            instance_identifier: Optional instance filter
            backup_type: Optional backup type filter
            start_time: Optional start time filter
            end_time: Optional end time filter

        Returns:
            List of backup details

        Example:
            ```python
            # List all manual backups for an instance
            backups = rds.list_backups(
                instance_identifier="my-db",
                backup_type=BackupType.MANUAL
            )

            # List recent automated backups
            recent_backups = rds.list_backups(
                backup_type=BackupType.AUTOMATED,
                start_time=datetime.utcnow() - timedelta(days=7)
            )
            ```

        """
        return self.rds.list_backups(
            instance_identifier,
            backup_type,
            start_time,
            end_time,
        )
