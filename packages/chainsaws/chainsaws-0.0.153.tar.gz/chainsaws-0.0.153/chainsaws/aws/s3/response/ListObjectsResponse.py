from typing import List, Literal
from typing_extensions import NotRequired, TypedDict
from datetime import datetime


class S3Owner(TypedDict):
    """S3 object owner information."""

    DisplayName: str
    ID: str


class S3RestoreStatus(TypedDict):
    """S3 object restore status."""

    IsRestoreInProgress: bool
    RestoreExpiryDate: datetime


class S3CommonPrefix(TypedDict):
    """S3 common prefix information."""

    Prefix: str


class S3Object(TypedDict):
    """Metadata about an individual S3 object."""

    # Required fields - always present in list_objects_v2 response
    Key: str
    LastModified: datetime
    ETag: str
    Size: int
    
    # Optional fields - may or may not be present
    ChecksumAlgorithm: NotRequired[List[Literal["CRC32", "CRC32C", "SHA1", "SHA256"]]]
    StorageClass: NotRequired[Literal[
        "STANDARD",
        "REDUCED_REDUNDANCY",
        "GLACIER",
        "STANDARD_IA",
        "ONEZONE_IA",
        "INTELLIGENT_TIERING",
        "DEEP_ARCHIVE",
        "OUTPOSTS",
        "GLACIER_IR",
        "SNOW",
        "EXPRESS_ONEZONE",
    ]]
    Owner: NotRequired[S3Owner]
    RestoreStatus: NotRequired[S3RestoreStatus]


class ListObjectsResponse(TypedDict):
    """Response structure for S3 list_objects_v2."""

    # Required fields - always present in list_objects_v2 response
    IsTruncated: bool
    Name: str
    KeyCount: int
    MaxKeys: int
    
    # Optional fields - may or may not be present
    Contents: NotRequired[List[S3Object]]
    Prefix: NotRequired[str]
    Delimiter: NotRequired[str]
    CommonPrefixes: NotRequired[List[S3CommonPrefix]]
    EncodingType: NotRequired[Literal["url"]]
    ContinuationToken: NotRequired[str]
    NextContinuationToken: NotRequired[str]
    StartAfter: NotRequired[str]
    RequestCharged: NotRequired[Literal["requester"]]
