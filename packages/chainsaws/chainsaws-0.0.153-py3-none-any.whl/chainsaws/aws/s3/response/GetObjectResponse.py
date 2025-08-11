from typing import Optional, Dict
from datetime import datetime
from botocore.response import StreamingBody
from .CommonResponse import (
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    ObjectMetadataResponse,
    ContentResponse,
    ObjectLockResponse,
    ReplicationResponse
)


class GetObjectResponse(
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    ObjectMetadataResponse,
    ContentResponse,
    ObjectLockResponse,
    ReplicationResponse,
    total=False
):
    """Response from S3 GetObject operation."""
    Body: Optional[StreamingBody]
    DeleteMarker: Optional[bool]
    AcceptRanges: Optional[str]
    Expiration: Optional[str]
    Restore: Optional[str]
    LastModified: Optional[datetime]
    ContentLength: Optional[int]
    ETag: Optional[str]
    ChecksumCRC32: Optional[str]
    ChecksumCRC32C: Optional[str]
    ChecksumSHA1: Optional[str]
    ChecksumSHA256: Optional[str]
    MissingMeta: Optional[int]
    VersionId: Optional[str]
    CacheControl: Optional[str]
    ContentDisposition: Optional[str]
    ContentEncoding: Optional[str]
    ContentLanguage: Optional[str]
    ContentRange: Optional[str]
    ContentType: Optional[str]
    Expires: Optional[datetime]
    WebsiteRedirectLocation: Optional[str]
    ServerSideEncryption: Optional[str]
    Metadata: Optional[Dict[str, str]]
    SSECustomerAlgorithm: Optional[str]
    SSECustomerKeyMD5: Optional[str]
    SSEKMSKeyId: Optional[str]
    BucketKeyEnabled: Optional[bool]
    StorageClass: Optional[str]
    RequestCharged: Optional[str]
    ReplicationStatus: Optional[str]
    PartsCount: Optional[int]
    TagCount: Optional[int]
    ObjectLockMode: Optional[str]
    ObjectLockRetainUntilDate: Optional[datetime]
    ObjectLockLegalHoldStatus: Optional[str] 