"""AWS Config event types for AWS Lambda."""


from typing import TypedDict


class ConfigEvent(TypedDict):
    """Event sent by AWS Config to evaluate resources.

    Args:
        invokingEvent (str): A JSON string containing details about the AWS Config rule evaluation.
        ruleParameters (str): A JSON string of the rule parameters from your AWS Config rule.
        resultToken (str): A token that AWS Config uses to ensure evaluation results are unique.
        eventLeftScope (bool): Indicates whether the AWS resource to be evaluated exists.
        executionRoleArn (str): The ARN of the IAM role that AWS Config used to invoke the Lambda function.
        configRuleArn (str): The ARN of the AWS Config rule.
        configRuleName (str): The name of the AWS Config rule.
        configRuleId (str): The ID of the AWS Config rule.
        accountId (str): The ID of the AWS account that owns the rule.
        version (str): The version of the event.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/services-config.html
    """
    invokingEvent: str
    ruleParameters: str
    resultToken: str
    eventLeftScope: bool
    executionRoleArn: str
    configRuleArn: str
    configRuleName: str
    configRuleId: str
    accountId: str
    version: str
