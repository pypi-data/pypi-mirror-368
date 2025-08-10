from typing import Optional
from .CommonResponse import (
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse
)


class UploadPartResponse(
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    total=False
):
    """Response from S3 UploadPart operation."""
    ETag: Optional[str]
    ServerSideEncryption: Optional[str]
    ChecksumCRC32: Optional[str]
    ChecksumCRC32C: Optional[str]
    ChecksumSHA1: Optional[str]
    ChecksumSHA256: Optional[str]
    SSECustomerAlgorithm: Optional[str]
    SSECustomerKeyMD5: Optional[str]
    SSEKMSKeyId: Optional[str]
    BucketKeyEnabled: Optional[bool]
    RequestCharged: Optional[str] 