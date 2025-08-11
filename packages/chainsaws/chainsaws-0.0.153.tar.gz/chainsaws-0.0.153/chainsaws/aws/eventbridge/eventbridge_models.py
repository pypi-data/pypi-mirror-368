"""EventBridge API models."""

from dataclasses import dataclass
import json
from typing import Any, Dict, List, Optional, Literal

from chainsaws.aws.shared.config import APIConfig


EventSource = Literal[
    "aws.s3", "aws.ec2", "aws.lambda", "aws.rds", "aws.sqs", "aws.sns",
    "aws.dynamodb", "aws.cloudwatch", "aws.codebuild", "aws.codepipeline",
    "custom"
]


@dataclass
class EventPattern:
    """EventBridge event pattern helper."""

    source: Optional[List[EventSource]] = None
    detail_type: Optional[List[str]] = None
    detail: Optional[Dict[str, Any]] = None
    resources: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to EventBridge pattern dict."""
        pattern = {}
        if self.source:
            pattern["source"] = self.source
        if self.detail_type:
            pattern["detail-type"] = self.detail_type
        if self.detail:
            pattern["detail"] = self.detail
        if self.resources:
            pattern["resources"] = self.resources
        return pattern


class EventBridgeAPIConfig(APIConfig):
    """EventBridge API configuration."""
    pass


@dataclass
class InputTransformer:
    """EventBridge input transformer configuration."""

    input_paths: Dict[str, str]
    input_template: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to EventBridge input transformer dict."""
        return {
            "InputPathsMap": self.input_paths,
            "InputTemplate": self.input_template
        }


@dataclass
class DeadLetterConfig:
    """EventBridge dead letter queue configuration."""

    arn: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to EventBridge DLQ dict."""
        return {"Arn": self.arn}


@dataclass
class RetryPolicy:
    """Target retry policy configuration."""

    maximum_retry_attempts: int = 3
    maximum_event_age_in_seconds: int = 86400  # 24 hours

    def to_dict(self) -> Dict[str, int]:
        """Convert to EventBridge retry policy dict."""
        return {
            "MaximumRetryAttempts": self.maximum_retry_attempts,
            "MaximumEventAgeInSeconds": self.maximum_event_age_in_seconds
        }


@dataclass
class Target:
    """EventBridge target configuration."""

    id: str
    arn: str
    input: Optional[str] = None
    input_path: Optional[str] = None
    input_transformer: Optional[InputTransformer] = None
    role_arn: Optional[str] = None
    dead_letter_config: Optional[DeadLetterConfig] = None
    retry_policy: Optional[RetryPolicy] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to EventBridge target dict."""
        target_dict = {
            "Id": self.id,
            "Arn": self.arn
        }
        if self.input:
            target_dict["Input"] = self.input
        if self.input_path:
            target_dict["InputPath"] = self.input_path
        if self.input_transformer:
            target_dict["InputTransformer"] = self.input_transformer.to_dict()
        if self.role_arn:
            target_dict["RoleArn"] = self.role_arn
        if self.dead_letter_config:
            target_dict["DeadLetterConfig"] = self.dead_letter_config.to_dict()
        if self.retry_policy:
            target_dict["RetryPolicy"] = self.retry_policy.to_dict()
        return target_dict


class TargetBuilder:
    """Builder class for creating EventBridge targets."""

    def __init__(self, region: str, account_id: str):
        """Initialize TargetBuilder.

        Args:
            region: AWS region
            account_id: AWS account ID
        """
        self.region = region
        self.account_id = account_id
        self._reset()

    def _reset(self) -> None:
        """Reset builder state."""
        self._target_id: str = ""
        self._arn: str = ""
        self._input: Optional[str] = None
        self._input_path: Optional[str] = None
        self._input_transformer: Optional[InputTransformer] = None
        self._role_arn: Optional[str] = None
        self._dead_letter_config: Optional[DeadLetterConfig] = None
        self._retry_policy: Optional[RetryPolicy] = None
        self._ecs_parameters: Optional[Dict[str, Any]] = None

    def with_input(self, input_data: Dict[str, Any]) -> "TargetBuilder":
        """Set static input data.

        Args:
            input_data: Static input data for the target

        Returns:
            Builder instance for method chaining
        """
        self._input = json.dumps(input_data)
        return self

    def with_input_path(self, path: str) -> "TargetBuilder":
        """Set input path for event transformation.

        Args:
            path: JSONPath expression

        Returns:
            Builder instance for method chaining
        """
        self._input_path = path
        return self

    def with_input_transformer(self, transformer: InputTransformer) -> "TargetBuilder":
        """Set input transformer for event transformation.

        Args:
            transformer: Input transformer configuration

        Returns:
            Builder instance for method chaining
        """
        self._input_transformer = transformer
        return self

    def with_role(self, role_arn: str) -> "TargetBuilder":
        """Set IAM role for target execution.

        Args:
            role_arn: IAM role ARN

        Returns:
            Builder instance for method chaining
        """
        self._role_arn = role_arn
        return self

    def with_dead_letter_queue(self, dlq_arn: str) -> "TargetBuilder":
        """Set dead letter queue for failed events.

        Args:
            dlq_arn: Dead letter queue ARN

        Returns:
            Builder instance for method chaining
        """
        self._dead_letter_config = DeadLetterConfig(dlq_arn)
        return self

    def with_retry_policy(self, retry_policy: RetryPolicy) -> "TargetBuilder":
        """Set retry policy for failed invocations.

        Args:
            retry_policy: Retry policy configuration

        Returns:
            Builder instance for method chaining
        """
        self._retry_policy = retry_policy
        return self

    def build(self) -> Target:
        """Build the target with current configuration.

        Returns:
            Configured Target instance
        """
        target = Target(
            id=self._target_id,
            arn=self._arn,
            input=self._input,
            input_path=self._input_path,
            input_transformer=self._input_transformer,
            role_arn=self._role_arn,
            dead_letter_config=self._dead_letter_config,
            retry_policy=self._retry_policy,
        )
        self._reset()
        return target

    def lambda_function(self, function_name: str) -> "TargetBuilder":
        """Configure Lambda function target.

        Args:
            function_name: Name or ARN of the Lambda function

        Returns:
            Builder instance for method chaining

        Examples:
            >>> builder = TargetBuilder("us-east-1", "123456789012")
            >>> target = (builder.lambda_function("process-upload")
            ...     .with_input({"operation": "resize"})
            ...     .with_retry_policy(RetryPolicy(maximum_retry_attempts=5))
            ...     .with_dead_letter_queue("arn:aws:sqs:us-east-1:123456789012:dlq")
            ...     .build())
        """
        self._target_id = f"lambda-{function_name.split(':')[-1]}"
        self._arn = (
            function_name if function_name.startswith("arn:")
            else f"arn:aws:lambda:{self.region}:{self.account_id}:function:{function_name}"
        )
        return self

    def sqs_queue(self, queue_name: str, message_group_id: Optional[str] = None) -> "TargetBuilder":
        """Configure SQS queue target.

        Args:
            queue_name: Name or ARN of the SQS queue
            message_group_id: Optional message group ID for FIFO queues

        Returns:
            Builder instance for method chaining

        Examples:
            >>> builder = TargetBuilder("us-east-1", "123456789012")
            >>> target = (builder.sqs_queue("my-queue.fifo", "group1")
            ...     .with_input_transformer(InputTransformer(
            ...         input_paths={"userId": "$.detail.user.id"},
            ...         input_template='{"user": <userId>}'
            ...     ))
            ...     .build())
        """
        self._target_id = f"sqs-{queue_name.split(':')[-1]}"
        self._arn = (
            queue_name if queue_name.startswith("arn:")
            else f"arn:aws:sqs:{self.region}:{self.account_id}:{queue_name}"
        )
        return self

    def sns_topic(self, topic_name: str) -> "TargetBuilder":
        """Configure SNS topic target.

        Args:
            topic_name: Name or ARN of the SNS topic

        Returns:
            Builder instance for method chaining

        Examples:
            >>> builder = TargetBuilder("us-east-1", "123456789012")
            >>> target = (builder.sns_topic("alerts")
            ...     .with_input({"alert": "High CPU usage"})
            ...     .with_dead_letter_queue("arn:aws:sqs:us-east-1:123456789012:dlq")
            ...     .build())
        """
        self._target_id = f"sns-{topic_name.split(':')[-1]}"
        self._arn = (
            topic_name if topic_name.startswith("arn:")
            else f"arn:aws:sns:{self.region}:{self.account_id}:{topic_name}"
        )
        return self

    def step_functions(self, state_machine_name: str) -> "TargetBuilder":
        """Configure Step Functions state machine target.

        Args:
            state_machine_name: Name or ARN of the state machine

        Returns:
            Builder instance for method chaining

        Examples:
            >>> builder = TargetBuilder("us-east-1", "123456789012")
            >>> target = (builder.step_functions("order-processing")
            ...     .with_input({"source": "eventbridge"})
            ...     .with_role("arn:aws:iam::123456789012:role/eventbridge-sfn-role")
            ...     .build())
        """
        self._target_id = f"sfn-{state_machine_name.split(':')[-1]}"
        self._arn = (
            state_machine_name if state_machine_name.startswith("arn:")
            else f"arn:aws:states:{self.region}:{self.account_id}:stateMachine:{state_machine_name}"
        )
        return self

    def kinesis_stream(self, stream_name: str, partition_key_path: str) -> "TargetBuilder":
        """Configure Kinesis stream target.

        Args:
            stream_name: Name or ARN of the Kinesis stream
            partition_key_path: JSONPath for the partition key

        Returns:
            Builder instance for method chaining

        Examples:
            >>> builder = TargetBuilder("us-east-1", "123456789012")
            >>> target = (builder.kinesis_stream("data-stream", "$.detail.userId")
            ...     .with_role("arn:aws:iam::123456789012:role/eventbridge-kinesis-role")
            ...     .build())
        """
        self._target_id = f"kinesis-{stream_name.split(':')[-1]}"
        self._arn = (
            stream_name if stream_name.startswith("arn:")
            else f"arn:aws:kinesis:{self.region}:{self.account_id}:stream/{stream_name}"
        )
        return self

    def ecs_task(
        self,
        cluster: str,
        task_definition: str,
        launch_type: Literal["EC2", "FARGATE"] = "FARGATE",
        network_config: Optional[Dict[str, Any]] = None,
    ) -> "TargetBuilder":
        """Configure ECS task target.

        Args:
            cluster: ECS cluster name or ARN
            task_definition: Task definition name or ARN
            launch_type: ECS launch type (EC2 or FARGATE)
            network_config: Optional network configuration for FARGATE

        Returns:
            Builder instance for method chaining

        Examples:
            >>> builder = TargetBuilder("us-east-1", "123456789012")
            >>> target = (builder.ecs_task(
            ...     "my-cluster",
            ...     "task-def:1",
            ...     network_config={
            ...         "awsvpcConfiguration": {
            ...             "subnets": ["subnet-1234"],
            ...             "securityGroups": ["sg-1234"]
            ...         }
            ...     })
            ...     .with_role("arn:aws:iam::123456789012:role/eventbridge-ecs-role")
            ...     .build())
        """
        self._target_id = f"ecs-{task_definition.split('/')[-1].split(':')[0]}"
        self._arn = (
            cluster if cluster.startswith("arn:")
            else f"arn:aws:ecs:{self.region}:{self.account_id}:cluster/{cluster}"
        )

        task_def_arn = (
            task_definition if task_definition.startswith("arn:")
            else f"arn:aws:ecs:{self.region}:{self.account_id}:task-definition/{task_definition}"
        )

        self._ecs_parameters = {
            "TaskDefinitionArn": task_def_arn,
            "TaskCount": 1,
            "LaunchType": launch_type,
        }
        if network_config:
            self._ecs_parameters["NetworkConfiguration"] = network_config

        return self


@dataclass
class PutEventsRequestEntry:
    """EventBridge PutEvents request entry."""

    detail: Dict[str, Any]
    detail_type: str
    source: EventSource
    event_bus_name: Optional[str] = None
    resources: Optional[List[str]] = None
    time: Optional[str] = None


@dataclass
class PutEventsResponse:
    """EventBridge PutEvents response."""

    entries: List[Dict[str, Any]]
    failed_entry_count: int


@dataclass
class CreateRuleResponse:
    """EventBridge CreateRule response."""

    rule_arn: str
    name: str


@dataclass
class PutTargetsResponse:
    """EventBridge PutTargets response."""

    failed_entry_count: int
    failed_entries: List[Dict[str, Any]]


@dataclass
class EventBusResponse:
    """EventBridge event bus response."""

    name: str
    arn: str
    policy: Optional[str] = None
