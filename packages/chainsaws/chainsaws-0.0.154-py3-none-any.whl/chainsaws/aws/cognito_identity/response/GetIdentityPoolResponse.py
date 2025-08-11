from typing import TypedDict, NotRequired


class CognitoIdentityProviderDict(TypedDict, total=False):
    ProviderName: str
    ClientId: str
    ServerSideTokenCheck: bool


class GetIdentityPoolResponse(TypedDict, total=False):
    IdentityPoolId: str
    IdentityPoolName: str
    AllowUnauthenticatedIdentities: bool
    CognitoIdentityProviders: NotRequired[list[CognitoIdentityProviderDict]]
    DeveloperProviderName: NotRequired[str]
    SupportedLoginProviders: NotRequired[dict[str, str]]
    OpenIdConnectProviderARNs: NotRequired[list[str]]
    SamlProviderARNs: NotRequired[list[str]]
    IdentityPoolTags: NotRequired[dict[str, str]]


