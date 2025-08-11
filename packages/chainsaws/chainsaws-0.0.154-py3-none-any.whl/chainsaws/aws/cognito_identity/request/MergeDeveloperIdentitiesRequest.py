from typing import TypedDict


class MergeDeveloperIdentitiesRequest(TypedDict):
    SourceUserIdentifier: str
    DestinationUserIdentifier: str
    DeveloperProviderName: str
    IdentityPoolId: str


