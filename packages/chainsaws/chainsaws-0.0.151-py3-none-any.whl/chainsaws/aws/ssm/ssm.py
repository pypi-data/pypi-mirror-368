import logging
from typing import Optional, List, Dict

from chainsaws.aws.shared import session
from chainsaws.aws.ssm._ssm_internal import SSM
from chainsaws.aws.ssm.ssm_models import (
    AutomationExecution,
    AutomationExecutionConfig,
    CommandConfig,
    CommandInvocation,
    Parameter,
    ParameterConfig,
    ParameterDetails,
    SSMAPIConfig,
)

logger = logging.getLogger(__name__)


class SSMAPI:
    """High-level SSM API for AWS Systems Manager operations."""

    def __init__(self, config: Optional[SSMAPIConfig] = None) -> None:
        """Initialize SSM client.

        Args:
            config: Optional SSM configuration

        """
        self.config = config or SSMAPIConfig()
        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None,
        )
        self.ssm = SSM(
            boto3_session=self.boto3_session,
            config=config,
        )

    def put_parameter(self, details: ParameterDetails) -> Parameter:
        """Create or update SSM parameter."""
        config = ParameterConfig(
            name=details['name'],
            value=details['value'],
            type=details['type'],
            description=details.get('description'),
            tier=details['tier'],
            tags=details.get('tags'),
            overwrite=details['overwrite'],
        )
        return self.ssm.put_parameter(config)

    def get_parameter(self, name: str, decrypt: bool = False) -> ParameterDetails:
        """Get SSM parameter value."""
        parameter = self.ssm.get_parameter(name, decrypt)
        return ParameterDetails(
            name=parameter.name,
            value=parameter.value,
            type=parameter.type,
            description=parameter.description,
            tier=parameter.tier,
            tags=parameter.tags,
            overwrite=parameter.overwrite,
        )

    def delete_parameter(self, name: str) -> None:
        """Delete SSM parameter.

        Args:
            name: Parameter name to delete

        """
        self.ssm.delete_parameter(name)

    def send_command(
        self,
        targets: List[Dict[str, List[str]]],
        document_name: str,
        parameters: Optional[Dict[str, List[str]]] = None,
        comment: Optional[str] = None,
        timeout_seconds: int = 3600,
    ) -> str:
        """Send SSM command to targets.

        Args:
            targets: List of target specifications
            document_name: SSM document to execute
            parameters: Optional command parameters
            comment: Optional command comment
            timeout_seconds: Command timeout in seconds

        Returns:
            Command ID for tracking execution

        """
        config = CommandConfig(
            targets=targets,
            document_name=document_name,
            parameters=parameters,
            comment=comment,
            timeout_seconds=timeout_seconds,
        )
        return self.ssm.send_command(config)

    def get_command_invocation(
        self,
        command_id: str,
        instance_id: str,
    ) -> CommandInvocation:
        """Get command execution details.

        Args:
            command_id: Command ID to check
            instance_id: Target instance ID

        Returns:
            Command invocation details including status and output

        """
        return self.ssm.get_command_invocation(command_id, instance_id)

    def start_automation(
        self,
        document_name: str,
        parameters: Optional[Dict[str, List[str]]] = None,
        target_parameter_name: Optional[str] = None,
        targets: Optional[List[Dict[str, List[str]]]] = None,
        max_concurrency: str = "1",
        max_errors: str = "1",
    ) -> str:
        """Start SSM automation execution.

        Args:
            document_name: Automation document name
            parameters: Optional automation parameters
            target_parameter_name: Parameter name for rate control
            targets: Optional automation targets
            max_concurrency: Max concurrent executions
            max_errors: Max allowed errors

        Returns:
            Automation execution ID

        """
        config = AutomationExecutionConfig(
            document_name=document_name,
            parameters=parameters,
            target_parameter_name=target_parameter_name,
            targets=targets,
            max_concurrency=max_concurrency,
            max_errors=max_errors,
        )
        return self.ssm.start_automation(config)

    def get_automation_execution(
        self,
        execution_id: str,
    ) -> AutomationExecution:
        """Get automation execution details.

        Args:
            execution_id: Automation execution ID

        Returns:
            Automation execution details including status and output

        """
        return self.ssm.get_automation_execution(execution_id)
