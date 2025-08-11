from typing import Optional
from .CommonResponse import (
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    ObjectMetadataResponse
)


class CompleteMultipartUploadResponse(
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    ObjectMetadataResponse,
    total=False
):
    """Response from S3 CompleteMultipartUpload operation."""
    Location: Optional[str]
    Bucket: Optional[str]
    Key: Optional[str]
    Expiration: Optional[str]
    ETag: Optional[str]
    ChecksumCRC32: Optional[str]
    ChecksumCRC32C: Optional[str]
    ChecksumSHA1: Optional[str]
    ChecksumSHA256: Optional[str]
    ServerSideEncryption: Optional[str]
    VersionId: Optional[str]
    SSEKMSKeyId: Optional[str]
    BucketKeyEnabled: Optional[bool]
    RequestCharged: Optional[str] 