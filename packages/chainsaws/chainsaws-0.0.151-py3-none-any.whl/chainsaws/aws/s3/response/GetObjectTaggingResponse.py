from typing import TypedDict, List
from .CommonResponse import ObjectMetadataResponse


class Tag(TypedDict):
    """S3 object tag."""
    Key: str
    Value: str


class GetObjectTaggingResponse(ObjectMetadataResponse, total=False):
    """Response from S3 GetObjectTagging operation."""
    TagSet: List[Tag] 