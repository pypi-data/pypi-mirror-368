from typing import TypedDict, Optional, List
from .CommonResponse import BaseS3Response


class DeletedObject(TypedDict, total=False):
    """Represents a successfully deleted object."""
    Key: str
    VersionId: Optional[str]
    DeleteMarker: Optional[bool]
    DeleteMarkerVersionId: Optional[str]


class DeleteError(TypedDict, total=False):
    """Represents an error during object deletion."""
    Key: str
    Code: str
    Message: str
    VersionId: Optional[str]


class DeleteObjectsResponse(BaseS3Response, total=False):
    """Response from S3 DeleteObjects operation."""
    Deleted: Optional[List[DeletedObject]]
    Errors: Optional[List[DeleteError]] 