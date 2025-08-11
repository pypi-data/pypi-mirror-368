"""Cognito Identity Pool high-level client."""

from chainsaws.aws.cognito_identity.cognito_identity import CognitoIdentityAPI
from chainsaws.aws.cognito_identity.cognito_identity_models import (
    CognitoIdentityAPIConfig,
    CreateIdentityPoolConfig,
    CreateIdentityPoolResult,
    SetIdentityPoolRolesConfig,
    SetIdentityPoolRolesResult,
    GetIdentityPoolResult,
)

__all__ = [
    "CognitoIdentityAPI",
    "CognitoIdentityAPIConfig",
    "CreateIdentityPoolConfig",
    "CreateIdentityPoolResult",
    "SetIdentityPoolRolesConfig",
    "SetIdentityPoolRolesResult",
    "GetIdentityPoolResult",
]


