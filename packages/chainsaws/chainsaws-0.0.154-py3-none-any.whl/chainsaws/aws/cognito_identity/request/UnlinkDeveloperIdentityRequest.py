from typing import TypedDict


class UnlinkDeveloperIdentityRequest(TypedDict):
    IdentityId: str
    DeveloperProviderName: str
    DeveloperUserIdentifier: str
    IdentityPoolId: str


