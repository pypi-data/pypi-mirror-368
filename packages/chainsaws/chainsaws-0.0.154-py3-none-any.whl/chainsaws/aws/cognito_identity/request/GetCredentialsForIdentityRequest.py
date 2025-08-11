from typing import TypedDict, NotRequired


class GetCredentialsForIdentityRequest(TypedDict, total=False):
    IdentityId: str
    Logins: NotRequired[dict[str, str]]
    CustomRoleArn: NotRequired[str]


