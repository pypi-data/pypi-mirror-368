from typing import Optional
from .CommonResponse import BaseS3Response, ObjectMetadataResponse


class DeleteObjectResponse(
    BaseS3Response,
    ObjectMetadataResponse,
    total=False
):
    """Response from S3 DeleteObject operation."""
    DeleteMarker: Optional[bool]
    VersionId: Optional[str]
    RequestCharged: Optional[str] 