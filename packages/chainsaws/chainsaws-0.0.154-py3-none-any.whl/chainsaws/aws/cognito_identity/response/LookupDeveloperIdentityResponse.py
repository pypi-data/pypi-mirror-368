from typing import TypedDict, NotRequired


class DeveloperUserIdentifierListDict(TypedDict, total=False):
    DeveloperUserIdentifierList: list[str]


class LookupDeveloperIdentityResponse(TypedDict, total=False):
    IdentityId: str
    DeveloperUserIdentifierList: NotRequired[list[str]]
    NextToken: NotRequired[str]


