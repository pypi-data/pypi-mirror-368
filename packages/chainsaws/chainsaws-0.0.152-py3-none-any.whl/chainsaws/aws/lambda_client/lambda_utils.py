from typing import Optional, Dict
from chainsaws.aws.lambda_client.lambda_models import LambdaHandler, TriggerType


def validate_lambda_configuration(
    memory_size: Optional[int] = None,
    timeout: Optional[int] = None,
    environment_variables: Optional[Dict[str, str]] = None,
    handler: Optional[LambdaHandler] = None,
) -> None:
    if memory_size is not None:
        if memory_size < 128 or memory_size > 10240:
            msg = "memory_size must be between 128 and 10240 MB"
            raise ValueError(msg)
        if memory_size % 128 != 0:
            msg = "memory_size must be a multiple of 128 MB. This is intended according to pricing policy of lambda"
            raise ValueError(
                msg)

    if timeout is not None and (timeout < 1 or timeout > 900):
        msg = "timeout must be between 1 and 900 seconds"
        raise ValueError(msg)

    # Validate environment variables
    if environment_variables is not None:
        if not all(isinstance(k, str) and isinstance(v, str)
                   for k, v in environment_variables.items()):
            msg = "All environment variables must be strings"
            raise ValueError(msg)
        # Check total size of environment variables (4KB limit)
        env_size = sum(len(k) + len(v)
                       for k, v in environment_variables.items())
        if env_size > 4096:
            msg = "Total size of environment variables exceeds 4KB limit"
            raise ValueError(
                msg)

    # Validate handler
    if handler is not None:
        if "." not in handler:
            msg = "handler must be in format 'file.function'"
            raise ValueError(msg)
        module, func = handler.rsplit(".", 1)
        if not module or not func:
            msg = "handler must have both module and function names"
            raise ValueError(
                msg)
        if not all(c.isalnum() or c in "_-" for c in module + func):
            msg = "handler can only contain alphanumeric characters, hyphens, and underscores"
            raise ValueError(
                msg)


def validate_source_arn(trigger_type: TriggerType, source_arn: str) -> None:
    """Validate source ARN format based on trigger type."""
    arn_prefixes = {
        TriggerType.API_GATEWAY: ("arn:aws:execute-api:", "arn:aws:apigateway:"),
        TriggerType.S3: ("arn:aws:s3:",),
        TriggerType.EVENTBRIDGE: ("arn:aws:events:",),
        TriggerType.SNS: ("arn:aws:sns:",),
        TriggerType.SQS: ("arn:aws:sqs:",),
        TriggerType.DYNAMODB: ("arn:aws:dynamodb:",),
    }

    valid_prefixes = arn_prefixes.get(trigger_type, ())
    if not any(source_arn.startswith(prefix) for prefix in valid_prefixes):
        prefix_list = "' or '".join(valid_prefixes)
        msg = (
            f"Invalid {trigger_type.value} ARN format. "
            f"Expected to start with: '{prefix_list}'"
        )
        raise ValueError(
            msg,
        )


def get_trigger_config(trigger_type: TriggerType) -> Dict[str, str]:
    """Get service-specific configuration for trigger type."""
    configs = {
        TriggerType.API_GATEWAY: {
            "action": "lambda:InvokeFunction",
            "principal": "apigateway.amazonaws.com",
        },
        TriggerType.S3: {
            "action": "lambda:InvokeFunction",
            "principal": "s3.amazonaws.com",
        },
        TriggerType.EVENTBRIDGE: {
            "action": "lambda:InvokeFunction",
            "principal": "events.amazonaws.com",
        },
        TriggerType.SNS: {
            "action": "lambda:InvokeFunction",
            "principal": "sns.amazonaws.com",
        },
        TriggerType.SQS: {
            "action": "lambda:InvokeFunction",
            "principal": "sqs.amazonaws.com",
        },
        TriggerType.DYNAMODB: {
            "action": "lambda:InvokeFunction",
            "principal": "dynamodb.amazonaws.com",
        },
    }

    return configs.get(trigger_type, {})
