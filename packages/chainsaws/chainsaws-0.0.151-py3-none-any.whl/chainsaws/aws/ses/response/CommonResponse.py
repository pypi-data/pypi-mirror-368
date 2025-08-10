from typing import Dict, TypedDict


class ResponseMetadata(TypedDict, total=False):
    """Metadata about an AWS response."""

    RequestId: str
    HostId: str
    HTTPStatusCode: int
    HTTPHeaders: Dict[str, str]
    RetryAttempts: int
