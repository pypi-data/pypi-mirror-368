from typing import Optional
from .CommonResponse import BaseS3Response, ServerSideEncryptionResponse


class CreateMultipartUploadResponse(
    BaseS3Response,
    ServerSideEncryptionResponse,
    total=False
):
    """Response from S3 CreateMultipartUpload operation."""
    Bucket: Optional[str]
    Key: Optional[str]
    UploadId: str
    ChecksumAlgorithm: Optional[str] 