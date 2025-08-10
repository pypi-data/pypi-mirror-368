import logging
from typing import Any, Optional
import re
from datetime import datetime
from croniter import croniter
from dataclasses import dataclass

from chainsaws.aws.lambda_client import LambdaAPI
from chainsaws.aws.scheduler._scheduler_internal import Scheduler
from chainsaws.aws.scheduler.scheduler_models import (
    SchedulerAPIConfig,
    ScheduleRequest,
    ScheduleResponse,
    ScheduleListResponse,
    ScheduleState,
)
from chainsaws.aws.scheduler.scheduler_exception import (
    ScheduleGroupNotFoundException,
    ScheduleNotFoundException
)
from chainsaws.aws.scheduler.scheduler_utils import (
    generate_schedule_name,
)

from chainsaws.aws.lambda_client.lambda_exception import LambdaException

from chainsaws.aws.shared import session

logger = logging.getLogger(__name__)


class SchedulerAPI:
    """High-level EventBridge Scheduler manager."""

    def __init__(
        self,
        schedule_group: Optional[str] = None,
        config: Optional[SchedulerAPIConfig] = None,
    ) -> None:
        """Initialize scheduler."""
        self.config = config or SchedulerAPIConfig()
        self.schedule_group = schedule_group or "chainsaws-default"

        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )

        self.scheduler = Scheduler(
            self.boto3_session,
            self.config,
        )

        self.lambda_client = LambdaAPI(config=self.config.to_lambda_config())

    def init_scheduler(
        self,
        lambda_function: str,
        schedule_expression: Optional[str] = 'rate(1 minute)',
        description: Optional[str] = None,
        input_data: Optional[dict[str, Any]] = None,
        name_prefix: Optional[str] = None,
    ) -> str:
        """Initialize scheduler for Lambda function.

        Args:
            lambda_function: Name or ARN of Lambda function
            schedule_expression: Optional custom schedule expression
            description: Optional schedule description
            input_data: Optional input data for Lambda
            name_prefix: Optional prefix for schedule name

        Returns:
            str: Created schedule name

        Raises:
            ValueError: If Lambda function doesn't exist or isn't properly configured
            Exception: Other AWS API errors
        """
        try:
            # Get Lambda function details and full ARN
            try:
                lambda_details = self.lambda_client.get_function(
                    function_name=lambda_function)
                lambda_function_arn = lambda_details['FunctionArn']
            except Exception as ex:
                msg = f"Failed to validate Lambda function: {ex!s}"
                raise LambdaException(msg) from ex

            try:
                self.scheduler.get_schedule_group(
                    group_name=self.schedule_group)
                logger.warning(
                    msg=f"Schedule group '{self.schedule_group}' already exists. Skipping creation...")
                pass
            except ScheduleGroupNotFoundException:
                self.scheduler.create_schedule_group(self.schedule_group)

            # Extract function name from ARN for schedule name generation
            function_name = lambda_function_arn.split(":")[-1]
            name = generate_schedule_name(function_name, prefix=name_prefix)

            request = ScheduleRequest(
                name=name,
                group_name=self.schedule_group,
                schedule_expression=schedule_expression,
                lambda_function_arn=lambda_function_arn,
                description=description,
                input_data=input_data,
            )

            try:
                name = self.scheduler.get_schedule(
                    name, group_name=self.schedule_group)
                logger.warning(
                    msg=f"Schedule {name} already exists for Lambda function, skipping generation... : {
                        function_name}",
                )

                return name
            except ScheduleNotFoundException:
                self.scheduler.create_schedule(request)
                logger.info(
                    msg=f"Created schedule: {
                        name} for Lambda function: {function_name}",
                )
            except Exception:
                logger.info(
                    msg=f"Failed to create schedule: {
                        name} for Lambda function: {function_name}",
                )
                raise

        except Exception as ex:
            logger.exception(f"Failed to create schedule: {ex!s}")
            raise

    def delete_schedule(self, name: str) -> None:
        """Delete a schedule.

        Args:
            name: Name of the schedule to delete

        Raises:
            ScheduleNotFoundException: If schedule doesn't exist
            SchedulerException: Other AWS API errors
        """
        try:
            self.scheduler.delete_schedule(name, self.schedule_group)
            logger.info(f"Deleted schedule: {name}")
        except Exception as ex:
            logger.exception(f"Failed to delete schedule: {ex!s}")
            raise

    def disable_schedule(self, name: str) -> None:
        """Disable a schedule.

        Args:
            name: Name of the schedule to disable

        Raises:
            ScheduleNotFoundException: If schedule doesn't exist
            SchedulerException: Other AWS API errors
        """
        try:
            self.scheduler.update_schedule_state(
                name, self.schedule_group, "DISABLED")
            logger.info(f"Disabled schedule: {name}")
        except Exception as ex:
            logger.exception(f"Failed to disable schedule: {ex!s}")
            raise

    def enable_schedule(self, name: str) -> None:
        """Enable a schedule.

        Args:
            name: Name of the schedule to enable

        Raises:
            ScheduleNotFoundException: If schedule doesn't exist
            SchedulerException: Other AWS API errors
        """
        try:
            self.scheduler.update_schedule_state(
                name, self.schedule_group, "ENABLED")
            logger.info(f"Enabled schedule: {name}")
        except Exception as ex:
            logger.exception(f"Failed to enable schedule: {ex!s}")
            raise

    def list_schedules(
        self,
        next_token: Optional[str] = None,
        max_results: int = 100,
    ) -> ScheduleListResponse:
        """List schedules in the group.

        Args:
            next_token: Token for pagination
            max_results: Maximum number of results to return

        Returns:
            ScheduleListResponse: List of schedules and next token

        Raises:
            SchedulerException: AWS API errors
        """
        try:
            response = self.scheduler.list_schedules(
                self.schedule_group,
                next_token=next_token,
                max_results=max_results,
            )

            schedules = []
            for schedule in response.get("Schedules", []):
                schedule_response = {
                    "name": schedule["Name"],
                    "arn": schedule["Arn"],
                    "state": schedule["State"],
                    "group_name": schedule["GroupName"],
                    "schedule_expression": schedule["ScheduleExpression"],
                    "description": schedule.get("Description"),
                    "next_invocation": schedule.get("NextInvocation"),
                    "last_invocation": schedule.get("LastInvocation"),
                    "target_arn": schedule["Target"]["Arn"],
                }
                schedules.append(schedule_response)

            return {
                "schedules": schedules,
                "next_token": response.get("NextToken"),
            }
        except Exception as ex:
            logger.exception(f"Failed to list schedules: {ex!s}")
            raise

    def update_schedule(
        self,
        name: str,
        schedule_expression: Optional[str] = None,
        description: Optional[str] = None,
        input_data: Optional[dict[str, Any]] = None,
        state: Optional[ScheduleState] = None,
    ) -> ScheduleResponse:
        """Update a schedule.

        Args:
            name: Name of the schedule to update
            schedule_expression: New schedule expression
            description: New description
            input_data: New input data
            state: New state

        Returns:
            ScheduleResponse: Updated schedule details

        Raises:
            ScheduleNotFoundException: If schedule doesn't exist
            InvalidScheduleExpressionError: If schedule expression is invalid
            SchedulerException: Other AWS API errors
        """
        try:
            response = self.scheduler.update_schedule(
                name=name,
                group_name=self.schedule_group,
                schedule_expression=schedule_expression,
                description=description,
                input_data=input_data,
                state=state.value if state else None,
            )

            return {
                "name": response["Name"],
                "arn": response["Arn"],
                "state": response["State"],
                "group_name": response["GroupName"],
                "schedule_expression": response["ScheduleExpression"],
                "description": response.get("Description"),
                "next_invocation": response.get("NextInvocation"),
                "last_invocation": response.get("LastInvocation"),
                "target_arn": response["Target"]["Arn"],
            }
        except Exception as ex:
            logger.exception(f"Failed to update schedule: {ex!s}")
            raise


@dataclass
class ScheduleExpression:
    """Schedule expression with validation."""

    expression: str  # Schedule expression string

    def __post_init__(self) -> None:
        """Validate schedule expression after initialization."""
        # at 표현식 검증 (at(yyyy-mm-ddThh:mm:ss))
        at_pattern = r"^at\(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\)$"
        if re.match(at_pattern, self.expression):
            try:
                time_str = self.expression[3:-1]
                datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
                return
            except ValueError as e:
                raise ValueError(f"Invalid at expression format: {e}")

        # rate 표현식 검증
        rate_pattern = r"^rate\((\d+) (minute|minutes|hour|hours|day|days)\)$"
        if re.match(rate_pattern, self.expression):
            return

        # cron 표현식 검증
        if self.expression.startswith("cron(") and self.expression.endswith(")"):
            cron_expr = self.expression[5:-1]
            try:
                croniter(expr_format=cron_expr)
                return
            except ValueError as e:
                raise ValueError(f"Invalid cron expression: {e}")

        raise ValueError(
            "Invalid schedule expression. Must be one of:\n"
            "- at(yyyy-mm-ddThh:mm:ss)\n"
            "- rate(value unit)\n"
            "- cron(* * * * * *)"
        )

    def __str__(self) -> str:
        """Return the schedule expression string."""
        return self.expression
