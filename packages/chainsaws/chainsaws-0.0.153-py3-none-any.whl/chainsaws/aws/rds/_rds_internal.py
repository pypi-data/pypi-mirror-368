"""Internal implementation of RDS and RDS Data Service operations."""
import logging
from datetime import datetime
from typing import Any, List, Dict, Optional

from boto3 import Session
from botocore.exceptions import ClientError

from chainsaws.aws.rds.rds_models import (
    BackupConfig,
    BackupType,
    BackupWindow,
    BatchExecuteResult,
    BatchExecuteStatementConfig,
    DatabaseInstance,
    DatabaseInstanceConfig,
    DBSnapshot,
    EventSubscriptionConfig,
    LogType,
    MetricConfig,
    ModifyInstanceConfig,
    ParameterGroupConfig,
    PerformanceInsightConfig,
    QueryConfig,
    QueryResult,
    ReadReplicaConfig,
    RestoreConfig,
    SnapshotConfig,
)

logger = logging.getLogger(__name__)


class RDS:
    """Internal RDS operations implementation."""

    def __init__(self, boto3_session: Session, region: str) -> None:
        """Initialize RDS clients."""
        self.rds_client = boto3_session.client("rds", region_name=region)
        self.rds_data_client = boto3_session.client(
            "rds-data", region_name=region)
        self.region = region

    def create_db_instance(
        self,
        config: DatabaseInstanceConfig,
    ) -> DatabaseInstance:
        """Create a new RDS instance."""
        try:
            response = self.rds_client.create_db_instance(
                DBInstanceIdentifier=config.instance_identifier,
                Engine=config.engine.value,
                EngineVersion=config.engine_version,
                DBInstanceClass=config.instance_class.value,
                AllocatedStorage=config.allocated_storage,
                MasterUsername=config.master_username,
                MasterUserPassword=config.master_password,
                VpcSecurityGroupIds=config.vpc_security_group_ids,
                AvailabilityZone=config.availability_zone,
                DBSubnetGroupName=config.db_subnet_group_name,
                Port=config.port,
                DBName=config.db_name,
                BackupRetentionPeriod=config.backup_retention_period,
                Tags=[{"Key": k, "Value": v} for k, v in config.tags.items()],
            )

            return self._convert_to_instance(response["DBInstance"])

        except ClientError as e:
            logger.exception(f"Failed to create DB instance: {e!s}")
            raise

    def modify_instance(self, config: ModifyInstanceConfig) -> DatabaseInstance:
        """Modify RDS instance configuration."""
        try:
            params = {
                "DBInstanceIdentifier": config.instance_identifier,
                "ApplyImmediately": config.apply_immediately,
            }

            # Add optional parameters
            if config.instance_class:
                params["DBInstanceClass"] = config.instance_class.value
            if config.allocated_storage:
                params["AllocatedStorage"] = config.allocated_storage
            if config.master_password:
                params["MasterUserPassword"] = config.master_password
            if config.backup_retention_period is not None:
                params["BackupRetentionPeriod"] = config.backup_retention_period
            if config.preferred_backup_window:
                params["PreferredBackupWindow"] = config.preferred_backup_window
            if config.preferred_maintenance_window:
                params["PreferredMaintenanceWindow"] = config.preferred_maintenance_window
            if config.multi_az is not None:
                params["MultiAZ"] = config.multi_az
            if config.auto_minor_version_upgrade is not None:
                params["AutoMinorVersionUpgrade"] = config.auto_minor_version_upgrade

            response = self.rds_client.modify_db_instance(**params)
            return self._convert_to_instance(response["DBInstance"])
        except ClientError as e:
            logger.exception(f"Failed to modify instance: {e!s}")
            raise

    def delete_db_instance(
        self,
        instance_identifier: str,
        skip_final_snapshot: bool = False,
        final_snapshot_identifier: Optional[str] = None,
    ) -> None:
        """Delete an RDS instance."""
        try:
            params = {
                "DBInstanceIdentifier": instance_identifier,
                "SkipFinalSnapshot": skip_final_snapshot,
            }

            if not skip_final_snapshot:
                if not final_snapshot_identifier:
                    final_snapshot_identifier = f"{
                        instance_identifier}-final-snapshot"
                params["FinalDBSnapshotIdentifier"] = final_snapshot_identifier

            self.rds_client.delete_db_instance(**params)

        except ClientError as e:
            logger.exception(f"Failed to delete DB instance: {e!s}")
            raise

    def get_db_instance(self, instance_identifier: str) -> DatabaseInstance:
        """Get details of an RDS instance."""
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=instance_identifier,
            )
            return self._convert_to_instance(response["DBInstances"][0])

        except ClientError as e:
            logger.exception(f"Failed to get DB instance details: {e!s}")
            raise

    def execute_statement(self, config: QueryConfig) -> QueryResult:
        """Execute SQL statement using Data API."""
        try:
            params = {
                "resourceArn": config.resource_arn,
                "secretArn": config.secret_arn,
                "database": config.database,
                "sql": config.sql,
                "parameters": config.parameters,
            }

            if config.schema:
                params["schema"] = config.schema
            if config.transaction_id:
                params["transactionId"] = config.transaction_id

            response = self.rds_data_client.execute_statement(**params)
            return self._convert_to_query_result(response)

        except ClientError as e:
            logger.exception(f"Failed to execute statement: {e!s}")
            raise

    def batch_execute_statement(
        self,
        config: BatchExecuteStatementConfig,
    ) -> BatchExecuteResult:
        """Execute batch SQL statements using Data API."""
        try:
            params = {
                "resourceArn": config.resource_arn,
                "secretArn": config.secret_arn,
                "database": config.database,
                "sql": config.sql,
                "parameterSets": config.parameter_sets,
            }

            if config.schema:
                params["schema"] = config.schema
            if config.transaction_id:
                params["transactionId"] = config.transaction_id

            response = self.rds_data_client.batch_execute_statement(**params)

            return BatchExecuteResult(
                update_results=response.get("updateResults", []),
                generated_fields=[
                    [field["longValue"] if "longValue" in field else field["stringValue"]
                     for field in record.get("generatedFields", [])]
                    for record in response.get("updateResults", [])
                ],
            )

        except ClientError as e:
            logger.exception(f"Failed to execute batch statement: {e!s}")
            raise

    def begin_transaction(
        self,
        resource_arn: str,
        secret_arn: str,
        database: str,
        schema: Optional[str] = None,
    ) -> str:
        """Begin a new transaction."""
        try:
            params = {
                "resourceArn": resource_arn,
                "secretArn": secret_arn,
                "database": database,
            }
            if schema:
                params["schema"] = schema

            response = self.rds_data_client.begin_transaction(**params)
            return response["transactionId"]

        except ClientError as e:
            logger.exception(f"Failed to begin transaction: {e!s}")
            raise

    def commit_transaction(
        self,
        resource_arn: str,
        secret_arn: str,
        transaction_id: str,
    ) -> None:
        """Commit a transaction."""
        try:
            self.rds_data_client.commit_transaction(
                resourceArn=resource_arn,
                secretArn=secret_arn,
                transactionId=transaction_id,
            )
        except ClientError as e:
            logger.exception(f"Failed to commit transaction: {e!s}")
            raise

    def rollback_transaction(
        self,
        resource_arn: str,
        secret_arn: str,
        transaction_id: str,
    ) -> None:
        """Rollback a transaction."""
        try:
            self.rds_data_client.rollback_transaction(
                resourceArn=resource_arn,
                secretArn=secret_arn,
                transactionId=transaction_id,
            )
        except ClientError as e:
            logger.exception(f"Failed to rollback transaction: {e!s}")
            raise

    def _convert_to_instance(self, raw_instance: dict) -> DatabaseInstance:
        """Convert raw instance data to DatabaseInstance model."""
        return DatabaseInstance(
            instance_identifier=raw_instance["DBInstanceIdentifier"],
            engine=raw_instance["Engine"],
            status=raw_instance["DBInstanceStatus"],
            endpoint=raw_instance.get("Endpoint", {}).get("Address"),
            port=raw_instance.get("Endpoint", {}).get("Port", 3306),
            allocated_storage=raw_instance["AllocatedStorage"],
            instance_class=raw_instance["DBInstanceClass"],
            creation_time=raw_instance["InstanceCreateTime"],
            publicly_accessible=raw_instance["PubliclyAccessible"],
            vpc_id=raw_instance.get("DBSubnetGroup", {}).get("VpcId"),
            availability_zone=raw_instance["AvailabilityZone"],
            tags={t["Key"]: t["Value"]
                  for t in raw_instance.get("TagList", [])},
        )

    def _convert_to_query_result(
        self,
        raw_result: Dict[str, Any],
    ) -> QueryResult:
        """Convert raw query result to QueryResult model."""
        columns = [col["label"]
                   for col in raw_result.get("columnMetadata", [])]
        rows = []

        for record in raw_result.get("records", []):
            row = {}
            for i, value in enumerate(record):
                # Get the first non-None value from the field
                field_value = next(
                    (v for v in value.values() if v is not None),
                    None,
                )
                row[columns[i]] = field_value
            rows.append(row)

        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=raw_result.get("numberOfRecordsUpdated", len(rows)),
            generated_fields=raw_result.get("generatedFields", []),
        )

    def create_snapshot(self, config: SnapshotConfig) -> DBSnapshot:
        """Create a DB snapshot."""
        try:
            response = self.rds_client.create_db_snapshot(
                DBSnapshotIdentifier=config.snapshot_identifier,
                DBInstanceIdentifier=config.instance_identifier,
                Tags=[{"Key": k, "Value": v} for k, v in config.tags.items()],
            )
            return self._convert_to_snapshot(response["DBSnapshot"])
        except ClientError as e:
            logger.exception(f"Failed to create snapshot: {e!s}")
            raise

    def restore_from_snapshot(
        self,
        snapshot_identifier: str,
        target_instance_identifier: str,
        instance_class: Optional[str] = None,
    ) -> DatabaseInstance:
        """Restore a DB instance from snapshot."""
        try:
            params = {
                "DBSnapshotIdentifier": snapshot_identifier,
                "DBInstanceIdentifier": target_instance_identifier,
            }
            if instance_class:
                params["DBInstanceClass"] = instance_class

            response = self.rds_client.restore_db_instance_from_db_snapshot(
                **params,
            )
            return self._convert_to_instance(response["DBInstance"])
        except ClientError as e:
            logger.exception(f"Failed to restore from snapshot: {e!s}")
            raise

    def create_parameter_group(
        self,
        config: ParameterGroupConfig,
    ) -> Dict[str, Any]:
        """Create a DB parameter group."""
        try:
            response = self.rds_client.create_db_parameter_group(
                DBParameterGroupName=config.group_name,
                DBParameterGroupFamily=config.family,
                Description=config.description,
                Tags=[{"Key": k, "Value": v} for k, v in config.tags.items()],
            )

            if config.parameters:
                self.rds_client.modify_db_parameter_group(
                    DBParameterGroupName=config.group_name,
                    Parameters=[
                        {
                            "ParameterName": name,
                            "ParameterValue": value,
                            "ApplyMethod": "pending-reboot",
                        }
                        for name, value in config.parameters.items()
                    ],
                )

            return response["DBParameterGroup"]
        except ClientError as e:
            logger.exception(f"Failed to create parameter group: {e!s}")
            raise

    def get_instance_metrics(
        self,
        config: MetricConfig,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get CloudWatch metrics for an RDS instance."""
        try:
            cloudwatch = self.boto3_session.client("cloudwatch")
            response = cloudwatch.get_metric_statistics(
                Namespace="AWS/RDS",
                MetricName=config.metric_name,
                Dimensions=[
                    {
                        "Name": "DBInstanceIdentifier",
                        "Value": config.instance_identifier,
                    },
                ],
                StartTime=config.start_time,
                EndTime=config.end_time,
                Period=config.period,
                Statistics=config.statistics,
            )
            return response["Datapoints"]
        except ClientError as e:
            logger.exception(f"Failed to get metrics: {e!s}")
            raise

    def create_read_replica(
        self,
        config: ReadReplicaConfig,
    ) -> DatabaseInstance:
        """Create a read replica."""
        try:
            params = {
                "DBInstanceIdentifier": config.replica_identifier,
                "SourceDBInstanceIdentifier": config.source_instance_identifier,
                "Tags": [{"Key": k, "Value": v} for k, v in config.tags.items()],
            }

            if config.availability_zone:
                params["AvailabilityZone"] = config.availability_zone
            if config.instance_class:
                params["DBInstanceClass"] = config.instance_class.value
            if config.port:
                params["Port"] = config.port

            response = self.rds_client.create_db_instance_read_replica(
                **params)
            return self._convert_to_instance(response["DBInstance"])
        except ClientError as e:
            logger.exception(f"Failed to create read replica: {e!s}")
            raise

    def _convert_to_snapshot(self, raw_snapshot: dict) -> DBSnapshot:
        """Convert raw snapshot data to DBSnapshot model."""
        return DBSnapshot(
            snapshot_identifier=raw_snapshot["DBSnapshotIdentifier"],
            instance_identifier=raw_snapshot["DBInstanceIdentifier"],
            creation_time=raw_snapshot["SnapshotCreateTime"],
            status=raw_snapshot["Status"],
            engine=raw_snapshot["Engine"],
            allocated_storage=raw_snapshot["AllocatedStorage"],
            availability_zone=raw_snapshot["AvailabilityZone"],
            tags={t["Key"]: t["Value"]
                  for t in raw_snapshot.get("TagList", [])},
        )

    def get_performance_insights(
        self,
        config: PerformanceInsightConfig,
    ) -> Dict[str, Any]:
        """Get Performance Insights metrics."""
        try:
            params = {
                "DBInstanceIdentifier": config.instance_identifier,
                "StartTime": config.start_time,
                "EndTime": config.end_time,
                "MetricQueries": config.metric_queries,
            }
            if config.max_results:
                params["MaxResults"] = config.max_results

            return self.rds_client.get_performance_insights_metrics(
                **params)
        except ClientError as e:
            logger.exception(f"Failed to get performance insights: {e!s}")
            raise

    def get_logs(
        self,
        instance_identifier: str,
        log_type: LogType,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_lines: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get database logs."""
        try:
            params = {
                "DBInstanceIdentifier": instance_identifier,
                "LogFileName": f"error/{log_type.value}.log",
            }
            if max_lines:
                params["NumberOfLines"] = max_lines

            response = self.rds_client.download_db_log_file_portion(**params)
            return self._parse_log_contents(response["LogFileData"])
        except ClientError as e:
            logger.exception(f"Failed to get logs: {e!s}")
            raise

    def create_event_subscription(
        self,
        config: EventSubscriptionConfig,
    ) -> Dict[str, Any]:
        """Create RDS event subscription."""
        try:
            params = {
                "SubscriptionName": config.subscription_name,
                "SnsTopicArn": config.sns_topic_arn,
                "SourceType": config.source_type,
                "EventCategories": [cat.value for cat in config.event_categories],
                "SourceIds": config.source_ids,
                "Enabled": config.enabled,
                "Tags": [{"Key": k, "Value": v} for k, v in config.tags.items()],
            }

            response = self.rds_client.create_event_subscription(**params)
            return response["EventSubscription"]
        except ClientError as e:
            logger.exception(f"Failed to create event subscription: {e!s}")
            raise

    def _parse_log_contents(self, log_data: str) -> List[Dict[str, Any]]:
        """Parse log contents into structured format."""
        # Implement log parsing logic based on log type
        # This is a simplified example
        logs = []
        for line in log_data.split("\n"):
            if line.strip():
                logs.append({
                    "timestamp": self._extract_timestamp(line),
                    "message": line.strip(),
                })
        return logs

    def _extract_timestamp(self, log_line: str) -> Optional[datetime]:
        """Extract timestamp from log line."""
        # Implement timestamp extraction logic
        # This is a placeholder
        return datetime.now()

    def create_backup(self, config: BackupConfig) -> Dict[str, Any]:
        """Create a manual backup/snapshot."""
        try:
            params = {
                "DBInstanceIdentifier": config.instance_identifier,
                "DBSnapshotIdentifier": config.backup_identifier,
                "Tags": [{"Key": k, "Value": v} for k, v in config.tags.items()],
            }

            response = self.rds_client.create_db_snapshot(**params)
            return response["DBSnapshot"]
        except ClientError as e:
            logger.exception(f"Failed to create backup: {e!s}")
            raise

    def restore_from_backup(self, config: RestoreConfig) -> DatabaseInstance:
        """Restore database from backup."""
        try:
            params = {
                "DBSnapshotIdentifier": config.source_identifier,
                "DBInstanceIdentifier": config.target_identifier,
                "MultiAZ": config.multi_az,
                "Tags": [{"Key": k, "Value": v} for k, v in config.tags.items()],
            }

            if config.instance_class:
                params["DBInstanceClass"] = config.instance_class.value
            if config.availability_zone:
                params["AvailabilityZone"] = config.availability_zone
            if config.port:
                params["Port"] = config.port
            if config.vpc_security_group_ids:
                params["VpcSecurityGroupIds"] = config.vpc_security_group_ids

            response = self.rds_client.restore_db_instance_from_db_snapshot(
                **params,
            )
            return self._convert_to_instance(response["DBInstance"])
        except ClientError as e:
            logger.exception(f"Failed to restore from backup: {e!s}")
            raise

    def restore_to_point_in_time(
        self,
        config: RestoreConfig,
    ) -> DatabaseInstance:
        """Restore database to a point in time."""
        try:
            params = {
                "SourceDBInstanceIdentifier": config.source_identifier,
                "TargetDBInstanceIdentifier": config.target_identifier,
                "RestoreTime": config.point_in_time,
                "MultiAZ": config.multi_az,
                "Tags": [{"Key": k, "Value": v} for k, v in config.tags.items()],
            }

            if config.instance_class:
                params["DBInstanceClass"] = config.instance_class.value
            if config.availability_zone:
                params["AvailabilityZone"] = config.availability_zone
            if config.port:
                params["Port"] = config.port
            if config.vpc_security_group_ids:
                params["VpcSecurityGroupIds"] = config.vpc_security_group_ids

            response = self.rds_client.restore_db_instance_to_point_in_time(
                **params,
            )
            return self._convert_to_instance(response["DBInstance"])
        except ClientError as e:
            logger.exception(
                f"Failed to restore to point in time: {e!s}")
            raise

    def configure_backup_window(
        self,
        config: BackupWindow,
    ) -> DatabaseInstance:
        """Configure backup window and retention period."""
        try:
            response = self.rds_client.modify_db_instance(
                DBInstanceIdentifier=config.instance_identifier,
                PreferredBackupWindow=config.preferred_window,
                BackupRetentionPeriod=config.retention_period,
                ApplyImmediately=True,
            )
            return self._convert_to_instance(response["DBInstance"])
        except ClientError as e:
            logger.exception(f"Failed to configure backup window: {e!s}")
            raise

    def list_backups(
        self,
        instance_identifier: Optional[str] = None,
        backup_type: Optional[BackupType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """List available backups/snapshots."""
        try:
            params = {}
            if instance_identifier:
                params["DBInstanceIdentifier"] = instance_identifier
            if backup_type == BackupType.AUTOMATED:
                params["SnapshotType"] = "automated"
            elif backup_type == BackupType.MANUAL:
                params["SnapshotType"] = "manual"
            if start_time:
                params["StartTime"] = start_time
            if end_time:
                params["EndTime"] = end_time

            response = self.rds_client.describe_db_snapshots(**params)
            return response["DBSnapshots"]
        except ClientError as e:
            logger.exception(f"Failed to list backups: {e!s}")
            raise
