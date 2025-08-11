from dataclasses import dataclass
from typing import TypedDict, NotRequired

from chainsaws.aws.shared.config import APIConfig


@dataclass
class CognitoIdentityAPIConfig(APIConfig):
    """Config for Cognito Identity API."""
    pass


class CognitoIdentityProviderDict(TypedDict, total=False):
    ProviderName: str  # e.g., 'cognito-idp.<region>.amazonaws.com/<user-pool-id>'
    ClientId: str
    ServerSideTokenCheck: bool


class CreateIdentityPoolConfig(TypedDict, total=False):
    IdentityPoolName: str
    AllowUnauthenticatedIdentities: bool
    CognitoIdentityProviders: list[CognitoIdentityProviderDict]
    DeveloperProviderName: str
    SupportedLoginProviders: dict[str, str]
    OpenIdConnectProviderARNs: list[str]
    SamlProviderARNs: list[str]
    IdentityPoolTags: dict[str, str]


class CreateIdentityPoolResult(TypedDict, total=False):
    IdentityPoolId: str
    IdentityPoolName: str
    AllowUnauthenticatedIdentities: bool
    CognitoIdentityProviders: NotRequired[list[CognitoIdentityProviderDict]]
    DeveloperProviderName: NotRequired[str]
    SupportedLoginProviders: NotRequired[dict[str, str]]
    OpenIdConnectProviderARNs: NotRequired[list[str]]
    SamlProviderARNs: NotRequired[list[str]]
    IdentityPoolTags: NotRequired[dict[str, str]]


class SetIdentityPoolRolesConfig(TypedDict, total=False):
    IdentityPoolId: str
    Roles: dict[str, str]  # { 'authenticated': roleArn, 'unauthenticated': roleArn }
    RoleMappings: NotRequired[dict]


class SetIdentityPoolRolesResult(TypedDict, total=False):
    Success: bool


class GetIdentityPoolResult(TypedDict, total=False):
    IdentityPoolId: str
    IdentityPoolName: str
    AllowUnauthenticatedIdentities: bool
    CognitoIdentityProviders: NotRequired[list[CognitoIdentityProviderDict]]
    DeveloperProviderName: NotRequired[str]
    SupportedLoginProviders: NotRequired[dict[str, str]]
    OpenIdConnectProviderARNs: NotRequired[list[str]]
    SamlProviderARNs: NotRequired[list[str]]
    IdentityPoolTags: NotRequired[dict[str, str]]


