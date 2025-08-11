"""Cognito User Pool Post Confirmation trigger event types for AWS Lambda."""

from typing import Any, Dict, Literal, TypedDict, Union


class CallerContext(TypedDict):
    """Information about the caller.

    Args:
        awsSdkVersion (str): The AWS SDK version used by the caller.
        clientId (str): The client ID of the user pool app client.
    """
    awsSdkVersion: str
    clientId: str


class Request(TypedDict, total=False):
    """Request information for the post confirmation trigger.

    Args:
        userAttributes (Dict[str, Any]): User attributes from the user pool.
        clientMetadata (Dict[str, Any]): Custom metadata from the client.
    """
    userAttributes: Dict[str, Any]
    clientMetadata: Dict[str, Any]


class Response(TypedDict):
    """Response object for the post confirmation trigger.

    This is currently empty as post-confirmation triggers don't modify the response.
    """
    pass


class CognitoPostConfirmationCommon(TypedDict):
    """Common fields for all Cognito Post Confirmation events.

    Args:
        version (str): The version number of the trigger.
        region (str): The AWS region.
        userPoolId (str): The user pool ID.
        userName (str): The username of the user.
        callerContext (CallerContext): Information about the caller.
        request (Request): The request containing user attributes.
        response (Response): The response object (empty for post-confirmation).

    Reference:
        https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-working-with-aws-lambda-triggers.html
    """
    version: str
    region: str
    userPoolId: str
    userName: str
    callerContext: CallerContext
    request: Request
    response: Response


class CognitoPostConfirmationForgotPasswordEvent(CognitoPostConfirmationCommon):
    """Event triggered after a successful forgot password confirmation.

    Args:
        triggerSource (Literal["PostConfirmation_ConfirmForgotPassword"]): 
            Must be "PostConfirmation_ConfirmForgotPassword".

    Reference:
        https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-post-confirmation.html
    """
    triggerSource: Literal["PostConfirmation_ConfirmForgotPassword"]


class CognitoPostConfirmationSignUpEvent(CognitoPostConfirmationCommon):
    """Event triggered after a successful sign-up confirmation.

    Args:
        triggerSource (Literal["PostConfirmation_ConfirmSignUp"]): 
            Must be "PostConfirmation_ConfirmSignUp".

    Reference:
        https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-post-confirmation.html
    """
    triggerSource: Literal["PostConfirmation_ConfirmSignUp"]


# Type alias for all possible event types
CognitoPostConfirmationEvent = Union[
    CognitoPostConfirmationForgotPasswordEvent,
    CognitoPostConfirmationSignUpEvent,
]
