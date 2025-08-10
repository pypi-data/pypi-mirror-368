import logging
from datetime import datetime
from typing import Optional

from boto3.session import Session

from chainsaws.aws.ssm.ssm_models import (
    AutomationExecution,
    AutomationExecutionConfig,
    CommandConfig,
    CommandInvocation,
    InventoryConfig,
    MaintenanceTask,
    MaintenanceWindow,
    MaintenanceWindowConfig,
    Parameter,
    ParameterConfig,
    PatchBaselineConfig,
    PatchSummary,
    SessionConfig,
    SessionDetails,
    SSMAPIConfig,
    StateAssociation,
    StateConfig,
)

logger = logging.getLogger(__name__)


class SSM:
    """Internal SSM operations."""

    def __init__(
        self,
        boto3_session: Session,
        config: Optional[SSMAPIConfig] = None,
    ) -> None:
        self.config = config or SSMAPIConfig()
        self.client = boto3_session.client("ssm")

    def put_parameter(self, config: ParameterConfig) -> Parameter:
        """Put SSM parameter."""
        try:
            self.client.put_parameter(
                Name=config.name,
                Value=config.value,
                Type=config.type,
                Description=config.description,
                Tier=config.tier,
                Overwrite=config.overwrite,
                Tags=[{"Key": k, "Value": v}
                      for k, v in (config.tags or {}).items()],
            )

            # Get parameter details after putting
            param = self.client.get_parameter(
                Name=config.name,
                WithDecryption=True,
            )["Parameter"]

            return Parameter(
                name=param["Name"],
                type=param["Type"],
                value=param["Value"],
                version=param["Version"],
                last_modified_date=param["LastModifiedDate"],
                arn=param["ARN"],
                data_type=param["DataType"],
            )
        except Exception as e:
            logger.exception(f"Failed to put parameter: {e!s}")
            raise

    def get_parameter(self, name: str, decrypt: bool = True) -> Parameter:
        """Get SSM parameter."""
        try:
            param = self.client.get_parameter(
                Name=name,
                WithDecryption=decrypt,
            )["Parameter"]

            return Parameter(
                name=param["Name"],
                type=param["Type"],
                value=param["Value"],
                version=param["Version"],
                last_modified_date=param["LastModifiedDate"],
                arn=param["ARN"],
                data_type=param["DataType"],
            )
        except Exception as e:
            logger.exception(f"Failed to get parameter: {e!s}")
            raise

    def delete_parameter(self, name: str) -> None:
        """Delete SSM parameter."""
        try:
            self.client.delete_parameter(Name=name)
        except Exception as e:
            logger.exception(f"Failed to delete parameter: {e!s}")
            raise

    def send_command(self, config: CommandConfig) -> str:
        """Send SSM command."""
        try:
            response = self.client.send_command(
                Targets=config.targets,
                DocumentName=config.document_name,
                Parameters=config.parameters,
                Comment=config.comment,
                TimeoutSeconds=config.timeout_seconds,
            )
            return response["Command"]["CommandId"]
        except Exception as e:
            logger.exception(f"Failed to send command: {e!s}")
            raise

    def get_command_invocation(
        self,
        command_id: str,
        instance_id: str,
    ) -> CommandInvocation:
        """Get command invocation details."""
        try:
            result = self.client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id,
            )
            return CommandInvocation(
                command_id=result["CommandId"],
                instance_id=result["InstanceId"],
                status=result["Status"],
                status_details=result["StatusDetails"],
                standard_output_content=result.get("StandardOutputContent"),
                standard_error_content=result.get("StandardErrorContent"),
            )
        except Exception as e:
            logger.exception(f"Failed to get command invocation: {e!s}")
            raise

    def start_automation(
        self,
        config: AutomationExecutionConfig,
    ) -> str:
        """Start automation execution."""
        try:
            response = self.client.start_automation_execution(
                DocumentName=config.document_name,
                Parameters=config.parameters,
                TargetParameterName=config.target_parameter_name,
                Targets=config.targets,
                MaxConcurrency=config.max_concurrency,
                MaxErrors=config.max_errors,
            )
            return response["AutomationExecutionId"]
        except Exception as e:
            logger.exception(f"Failed to start automation: {e!s}")
            raise

    def get_automation_execution(
        self,
        execution_id: str,
    ) -> AutomationExecution:
        """Get automation execution details."""
        try:
            result = self.client.get_automation_execution(
                AutomationExecutionId=execution_id,
            )["AutomationExecution"]

            return AutomationExecution(
                automation_execution_id=result["AutomationExecutionId"],
                document_name=result["DocumentName"],
                status=result["Status"],
                start_time=result["StartTime"],
                end_time=result.get("EndTime"),
                outputs=result.get("Outputs"),
                failure_message=result.get("FailureMessage"),
            )
        except Exception as e:
            logger.exception(f"Failed to get automation execution: {e!s}")
            raise

    def start_session(self, config: SessionConfig) -> SessionDetails:
        """Start a Session Manager session."""
        try:
            response = self.client.start_session(
                Target=config.target,
                DocumentName=config.document_name,
                Parameters=config.parameters,
                Reason=config.reason,
            )

            return SessionDetails(
                session_id=response["SessionId"],
                target=response["Target"],
                status=response["Status"],
                reason=config.reason,
                start_date=datetime.now(),
            )
        except Exception as e:
            logger.exception(f"Failed to start session: {e!s}")
            raise

    def terminate_session(self, session_id: str) -> None:
        """Terminate a Session Manager session."""
        try:
            self.client.terminate_session(SessionId=session_id)
        except Exception as e:
            logger.exception(f"Failed to terminate session: {e!s}")
            raise

    def get_session_status(self, session_id: str) -> SessionDetails:
        """Get Session Manager session status."""
        try:
            response = self.client.describe_sessions(
                SessionId=session_id,
            )["Sessions"][0]

            return SessionDetails(
                session_id=response["SessionId"],
                target=response["Target"],
                status=response["Status"],
                reason=response.get("Reason"),
                start_date=response["StartDate"],
                end_date=response.get("EndDate"),
            )
        except Exception as e:
            logger.exception(f"Failed to get session status: {e!s}")
            raise

    def create_patch_baseline(self, config: PatchBaselineConfig) -> str:
        """Create a patch baseline."""
        try:
            response = self.client.create_patch_baseline(
                Name=config.name,
                OperatingSystem=config.operating_system,
                ApprovalRules=config.approval_rules,
                Description=config.description,
                Tags=[{"Key": k, "Value": v}
                      for k, v in (config.tags or {}).items()],
            )
            return response["BaselineId"]
        except Exception as e:
            logger.exception(f"Failed to create patch baseline: {e!s}")
            raise

    def get_patch_baseline(self, baseline_id: str) -> dict:
        """Get patch baseline details."""
        try:
            return self.client.get_patch_baseline(
                BaselineId=baseline_id,
            )
        except Exception as e:
            logger.exception(f"Failed to get patch baseline: {e!s}")
            raise

    def register_patch_baseline_for_patch_group(
        self,
        baseline_id: str,
        patch_group: str,
    ) -> None:
        """Register patch baseline for patch group."""
        try:
            self.client.register_patch_baseline_for_patch_group(
                BaselineId=baseline_id,
                PatchGroup=patch_group,
            )
        except Exception as e:
            logger.exception(f"Failed to register patch baseline: {e!s}")
            raise

    def get_patch_summary(self, instance_id: str) -> PatchSummary:
        """Get patch summary for an instance."""
        try:
            response = self.client.describe_instance_patches(
                InstanceId=instance_id,
            )

            summary = {
                "critical_missing": 0,
                "security_missing": 0,
                "installed_count": 0,
                "installed_rejected": 0,
            }

            for patch in response["Patches"]:
                if patch["State"] == "Missing":
                    if patch["Severity"] == "Critical":
                        summary["critical_missing"] += 1
                    elif patch["Severity"] == "Security":
                        summary["security_missing"] += 1
                elif patch["State"] == "Installed":
                    summary["installed_count"] += 1
                elif patch["State"] == "InstalledRejected":
                    summary["installed_rejected"] += 1

            return PatchSummary(
                instance_id=instance_id,
                patch_group=response.get("PatchGroup", ""),
                baseline_id=response.get("BaselineId", ""),
                status=response.get("OverallStatus", "Unknown"),
                operation_type="Scan",
                **summary,
            )
        except Exception as e:
            logger.exception(f"Failed to get patch summary: {e!s}")
            raise

    def create_association(self, config: StateConfig) -> StateAssociation:
        """Create State Manager association."""
        try:
            response = self.client.create_association(
                Name=config.name,
                DocumentName=config.document_name,
                Targets=config.targets,
                Parameters=config.parameters,
                ScheduleExpression=config.schedule_expression,
                AutomationTargetParameterName=config.automation_target_parameter_name,
            )

            return StateAssociation(
                association_id=response["AssociationId"],
                name=config.name,
                status=response["Overview"]["Status"],
                overview=response["Overview"],
            )
        except Exception as e:
            logger.exception(f"Failed to create association: {e!s}")
            raise

    def delete_association(self, association_id: str) -> None:
        """Delete State Manager association."""
        try:
            self.client.delete_association(AssociationId=association_id)
        except Exception as e:
            logger.exception(f"Failed to delete association: {e!s}")
            raise

    def get_association(self, association_id: str) -> StateAssociation:
        """Get State Manager association details."""
        try:
            response = self.client.describe_association(
                AssociationId=association_id,
            )

            return StateAssociation(
                association_id=association_id,
                name=response["Name"],
                status=response["Overview"]["Status"],
                last_execution_date=response.get("LastExecutionDate"),
                overview=response["Overview"],
            )
        except Exception as e:
            logger.exception(f"Failed to get association: {e!s}")
            raise

    def collect_inventory(self, config: InventoryConfig) -> None:
        """Collect inventory data."""
        try:
            self.client.put_inventory(
                InstanceId=config.instance_id,
                TypeName=config.type_name,
                SchemaVersion=config.schema_version,
                CaptureTime=config.capture_time,
                Content=[config.content],
            )
        except Exception as e:
            logger.exception(f"Failed to collect inventory: {e!s}")
            raise

    def get_inventory(
        self,
        instance_id: str,
        type_name: str,
    ) -> list[dict]:
        """Get inventory data."""
        try:
            response = self.client.get_inventory(
                Filters=[
                    {
                        "Key": "AWS:InstanceInformation.InstanceId",
                        "Values": [instance_id],
                        "Type": "Equal",
                    },
                    {
                        "Key": "TypeName",
                        "Values": [type_name],
                        "Type": "Equal",
                    },
                ],
            )
            return response["Entities"]
        except Exception as e:
            logger.exception(f"Failed to get inventory: {e!s}")
            raise

    def create_maintenance_window(
        self,
        config: MaintenanceWindowConfig,
    ) -> MaintenanceWindow:
        """Create maintenance window."""
        try:
            response = self.client.create_maintenance_window(
                Name=config.name,
                Schedule=config.schedule,
                Duration=config.duration,
                Cutoff=config.cutoff,
                AllowUnassociatedTargets=config.allow_unregistered_targets,
                Tags=[{"Key": k, "Value": v}
                      for k, v in (config.tags or {}).items()],
            )

            return MaintenanceWindow(
                window_id=response["WindowId"],
                name=config.name,
                status="Creating",
                enabled=True,
                schedule=config.schedule,
                duration=config.duration,
                cutoff=config.cutoff,
            )
        except Exception as e:
            logger.exception(f"Failed to create maintenance window: {e!s}")
            raise

    def register_maintenance_window_task(
        self,
        window_id: str,
        task_type: str,
        targets: list[dict],
        task_arn: str,
        service_role_arn: str,
        priority: int = 1,
        max_concurrency: str = "1",
        max_errors: str = "1",
    ) -> MaintenanceTask:
        """Register task with maintenance window."""
        try:
            response = self.client.register_task_with_maintenance_window(
                WindowId=window_id,
                TaskType=task_type,
                Targets=targets,
                TaskArn=task_arn,
                ServiceRoleArn=service_role_arn,
                Priority=priority,
                MaxConcurrency=max_concurrency,
                MaxErrors=max_errors,
            )

            return MaintenanceTask(
                window_id=window_id,
                task_id=response["WindowTaskId"],
                task_type=task_type,
                targets=targets,
                task_arn=task_arn,
                service_role_arn=service_role_arn,
                status="Registered",
                priority=priority,
                max_concurrency=max_concurrency,
                max_errors=max_errors,
            )
        except Exception as e:
            logger.exception(
                f"Failed to register maintenance window task: {e!s}")
            raise

    def get_patch_status(self, instance_id: str) -> PatchSummary:
        """Get patching status for an instance.

        Args:
            instance_id: EC2 instance ID

        Returns:
            PatchSummary containing patch compliance information

        Example:
            ```python
            status = ssm.get_patch_status("i-1234567890abcdef0")
            print(f"Missing critical patches: {status.critical_missing}")
            print(f"Installed patches: {status.installed_count}")
            ```

        """
        return self.ssm.get_patch_summary(instance_id)

    def create_state_association(
        self,
        name: str,
        document_name: str,
        targets: list[dict[str, list[str]]],
        schedule: str,
        parameters: dict[str, list[str]] | None = None,
    ) -> StateAssociation:
        """Create a State Manager association for automated configuration.

        Args:
            name: Association name
            document_name: SSM document to use
            targets: List of targets (instances/tags)
            schedule: Schedule expression (cron/rate)
            parameters: Optional document parameters

        Returns:
            StateAssociation containing association details

        Example:
            ```python
            association = ssm.create_state_association(
                name="InstallCloudWatchAgent",
                document_name="AWS-ConfigureAWSPackage",
                targets=[{
                    "Key": "tag:Environment",
                    "Values": ["Production"]
                }],
                schedule="rate(1 day)",
                parameters={
                    "Action": ["Install"],
                    "Name": ["AmazonCloudWatchAgent"]
                }
            )
            ```

        """
        config = StateConfig(
            name=name,
            document_name=document_name,
            targets=targets,
            schedule_expression=schedule,
            parameters=parameters,
        )
        return self.ssm.create_association(config)

    def add_maintenance_task(
        self,
        window_id: str,
        task_type: str,
        targets: list[dict],
        task_arn: str,
        service_role_arn: str,
        priority: int = 1,
        max_concurrent: str = "1",
        max_errors: str = "1",
    ) -> MaintenanceTask:
        """Add a task to a maintenance window.

        Args:
            window_id: Maintenance window ID
            task_type: Task type (AUTOMATION, LAMBDA, RUN_COMMAND, etc.)
            targets: Task targets
            task_arn: Task ARN (document/function ARN)
            service_role_arn: IAM role ARN for task execution
            priority: Task priority (lower numbers run first)
            max_concurrent: Max concurrent executions
            max_errors: Max allowed errors

        Returns:
            MaintenanceTask containing task details

        Example:
            ```python
            task = ssm.add_maintenance_task(
                window_id="mw-1234567890abcdef0",
                task_type="RUN_COMMAND",
                targets=[{
                    "Key": "WindowTargetIds",
                    "Values": ["target-1234567890abcdef0"]
                }],
                task_arn="AWS-RunPatchBaseline",
                service_role_arn="arn:aws:iam::123456789012:role/MaintenanceWindowRole",
                priority=1,
                max_concurrent="50%",
                max_errors="25%"
            )
            ```

        """
        return self.ssm.register_maintenance_window_task(
            window_id=window_id,
            task_type=task_type,
            targets=targets,
            task_arn=task_arn,
            service_role_arn=service_role_arn,
            priority=priority,
            max_concurrency=max_concurrent,
            max_errors=max_errors,
        )
