from typing import TypedDict, Optional


class CreateBucketResponse(TypedDict, total=False):
    """Response from S3 CreateBucket operation."""
    Location: Optional[str] 