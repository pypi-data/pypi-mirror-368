from typing import Optional
from datetime import datetime
from .CommonResponse import (
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    ObjectMetadataResponse
)


class CopyObjectResult(ChecksumResponse, total=False):
    """Result details from copy operation."""
    ETag: Optional[str]
    LastModified: Optional[datetime]


class CopyObjectResponse(
    BaseS3Response,
    ServerSideEncryptionResponse,
    ObjectMetadataResponse,
    total=False
):
    """Response from S3 CopyObject operation."""
    CopyObjectResult: Optional[CopyObjectResult]
    CopySourceVersionId: Optional[str]
    Expiration: Optional[str]
    VersionId: Optional[str]
    ServerSideEncryption: Optional[str]
    SSECustomerAlgorithm: Optional[str]
    SSECustomerKeyMD5: Optional[str]
    SSEKMSKeyId: Optional[str]
    SSEKMSEncryptionContext: Optional[str]
    BucketKeyEnabled: Optional[bool]
    RequestCharged: Optional[str] 