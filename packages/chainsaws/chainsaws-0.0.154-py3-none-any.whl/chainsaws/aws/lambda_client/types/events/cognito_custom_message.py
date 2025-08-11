"""Cognito User Pool Custom Message trigger event types for AWS Lambda."""


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
    """Request information for the custom message.

    Args:
        userAttributes (Dict[str, Any]): User attributes from the user pool.
        codeParameter (str): The placeholder for the authorization code.
        usernameParameter (str): The placeholder for the username.
        clientMetadata (Dict[str, Any]): Custom metadata from the client.
    """
    userAttributes: Dict[str, Any]
    codeParameter: str
    usernameParameter: str
    clientMetadata: Dict[str, Any]


class Response(TypedDict):
    """Response containing the custom messages.

    Args:
        smsMessage (str): The custom SMS message.
        emailMessage (str): The custom email message.
        emailSubject (str): The custom email subject.
    """
    smsMessage: str
    emailMessage: str
    emailSubject: str


class CognitoCustomMessageCommon(TypedDict):
    """Common fields for all Cognito Custom Message events.

    Args:
        version (str): The version number of the trigger.
        region (str): The AWS region.
        userPoolId (str): The user pool ID.
        userName (str): The username of the user.
        callerContext (CallerContext): Information about the caller.
        request (Request): The request containing the message parameters.
        response (Response): The response containing the custom messages.

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


class CognitoCustomMessageSignUpEvent(CognitoCustomMessageCommon):
    """Event for customizing sign-up verification messages.

    Args:
        triggerSource (Literal["CustomMessage_SignUp"]): Must be "CustomMessage_SignUp".
    """
    triggerSource: Literal["CustomMessage_SignUp"]


class CognitoCustomMessageAdminCreateUserEvent(CognitoCustomMessageCommon):
    """Event for customizing admin user creation messages.

    Args:
        triggerSource (Literal["CustomMessage_AdminCreateUser"]): Must be "CustomMessage_AdminCreateUser".
    """
    triggerSource: Literal["CustomMessage_AdminCreateUser"]


class CognitoCustomMessageResendCodeEvent(CognitoCustomMessageCommon):
    """Event for customizing code resend messages.

    Args:
        triggerSource (Literal["CustomMessage_ResendCode"]): Must be "CustomMessage_ResendCode".
    """
    triggerSource: Literal["CustomMessage_ResendCode"]


class CognitoCustomMessageForgotPasswordEvent(CognitoCustomMessageCommon):
    """Event for customizing forgot password messages.

    Args:
        triggerSource (Literal["CustomMessage_ForgotPassword"]): Must be "CustomMessage_ForgotPassword".
    """
    triggerSource: Literal["CustomMessage_ForgotPassword"]


class CognitoCustomMessageUpdateUserAttributeEvent(CognitoCustomMessageCommon):
    """Event for customizing attribute update verification messages.

    Args:
        triggerSource (Literal["CustomMessage_UpdateUserAttribute"]): Must be "CustomMessage_UpdateUserAttribute".
    """
    triggerSource: Literal["CustomMessage_UpdateUserAttribute"]


class CognitoCustomMessageVerifyUserAttributeEvent(CognitoCustomMessageCommon):
    """Event for customizing attribute verification messages.

    Args:
        triggerSource (Literal["CustomMessage_VerifyUserAttribute"]): Must be "CustomMessage_VerifyUserAttribute".
    """
    triggerSource: Literal["CustomMessage_VerifyUserAttribute"]


class CognitoCustomMessageAuthenticationEvent(CognitoCustomMessageCommon):
    """Event for customizing authentication messages.

    Args:
        triggerSource (Literal["CustomMessage_Authentication"]): Must be "CustomMessage_Authentication".
    """
    triggerSource: Literal["CustomMessage_Authentication"]


# Type alias for all possible event types
CognitoCustomMessageEvent = Union[
    CognitoCustomMessageSignUpEvent,
    CognitoCustomMessageAdminCreateUserEvent,
    CognitoCustomMessageResendCodeEvent,
    CognitoCustomMessageForgotPasswordEvent,
    CognitoCustomMessageUpdateUserAttributeEvent,
    CognitoCustomMessageVerifyUserAttributeEvent,
    CognitoCustomMessageAuthenticationEvent,
]
