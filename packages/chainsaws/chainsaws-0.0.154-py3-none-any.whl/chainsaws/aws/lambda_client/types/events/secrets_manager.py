"""Secrets Manager rotation event types for AWS Lambda."""


from typing import Literal, TypedDict


class SecretsManagerRotationEvent(TypedDict):
    """Event sent by Secrets Manager during secret rotation.

    Args:
        Step (str): The current step in the rotation process:
            - createSecret: Create a new version of the secret
            - setSecret: Update the protected resource with the new secret
            - testSecret: Verify the new secret works
            - finishSecret: Mark the new secret version as active
        SecretId (str): The ARN or name of the secret being rotated.
        ClientRequestToken (str): A unique identifier for this rotation request.

    Reference:
        https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets-lambda-function-overview.html
    """
    Step: Literal[
        "createSecret",
        "setSecret",
        "testSecret",
        "finishSecret",
    ]
    SecretId: str
    ClientRequestToken: str
