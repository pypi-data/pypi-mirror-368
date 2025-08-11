from typing import TypedDict, NotRequired


class GetIdRequest(TypedDict, total=False):
    AccountId: NotRequired[str]
    IdentityPoolId: str
    Logins: NotRequired[dict[str, str]]
    PrincipalTags: NotRequired[dict[str, str]]


