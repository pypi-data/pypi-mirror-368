from typing import TypedDict


class CredentialsDict(TypedDict):
    AccessKeyId: str
    SecretKey: str
    SessionToken: str
    Expiration: float  # unix timestamp


class GetCredentialsForIdentityResponse(TypedDict):
    IdentityId: str
    Credentials: CredentialsDict


