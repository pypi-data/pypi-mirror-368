from typing import TypedDict, NotRequired


class LookupDeveloperIdentityRequest(TypedDict, total=False):
    IdentityPoolId: str
    IdentityId: NotRequired[str]
    DeveloperUserIdentifier: NotRequired[str]
    MaxResults: NotRequired[int]
    NextToken: NotRequired[str]


