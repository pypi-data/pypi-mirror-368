from typing import Optional, Dict
from datetime import datetime
from .CommonResponse import (
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    ObjectMetadataResponse,
    ContentResponse,
    ObjectLockResponse,
    ReplicationResponse
)


class HeadObjectResponse(
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    ObjectMetadataResponse,
    ContentResponse,
    ObjectLockResponse,
    ReplicationResponse,
    total=False
):
    """Response from S3 HeadObject operation."""
    DeleteMarker: Optional[bool]
    AcceptRanges: Optional[str]
    Restore: Optional[str]
    MissingMeta: Optional[int]
    Expires: Optional[datetime]
    WebsiteRedirectLocation: Optional[str]
    Metadata: Optional[Dict[str, str]]
    StorageClass: Optional[str]
    PartsCount: Optional[int]
    TagCount: Optional[int]
    Expiration: Optional[str]
    LastModified: Optional[datetime]
    ContentLength: Optional[int]
    ChecksumCRC32: Optional[str]
    ChecksumCRC32C: Optional[str]
    ChecksumSHA1: Optional[str]
    ChecksumSHA256: Optional[str]
    ETag: Optional[str]
    CacheControl: Optional[str]
    ContentDisposition: Optional[str]
    ContentEncoding: Optional[str]
    ContentLanguage: Optional[str]
    ContentType: Optional[str]
    RequestCharged: Optional[str]
    ReplicationStatus: Optional[str]
    ObjectLockMode: Optional[str]
    ObjectLockRetainUntilDate: Optional[datetime]
    ObjectLockLegalHoldStatus: Optional[str]
    ServerSideEncryption: Optional[str]
    SSECustomerAlgorithm: Optional[str]
    SSECustomerKeyMD5: Optional[str]
    SSEKMSKeyId: Optional[str]
    BucketKeyEnabled: Optional[bool] 