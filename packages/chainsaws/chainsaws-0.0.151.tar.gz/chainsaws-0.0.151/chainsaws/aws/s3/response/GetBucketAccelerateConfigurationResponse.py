from typing import Optional
from .CommonResponse import BaseS3Response


class GetBucketAccelerateConfigurationResponse(BaseS3Response, total=False):
    """Response from S3 GetBucketAccelerateConfiguration operation."""
    Status: Optional[str]
    RequestCharged: Optional[str] 