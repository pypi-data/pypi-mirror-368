from typing import TypedDict, Optional
from datetime import datetime


class BaseS3Response(TypedDict, total=False):
    """Base response fields common to many S3 operations."""
    RequestCharged: Optional[str]


class ServerSideEncryptionResponse(TypedDict, total=False):
    """Server-side encryption related fields."""
    ServerSideEncryption: Optional[str]
    SSECustomerAlgorithm: Optional[str]
    SSECustomerKeyMD5: Optional[str]
    SSEKMSKeyId: Optional[str]
    SSEKMSEncryptionContext: Optional[str]
    BucketKeyEnabled: Optional[bool]


class ChecksumResponse(TypedDict, total=False):
    """Checksum related fields."""
    ChecksumCRC32: Optional[str]
    ChecksumCRC32C: Optional[str]
    ChecksumSHA1: Optional[str]
    ChecksumSHA256: Optional[str]


class ObjectMetadataResponse(TypedDict, total=False):
    """Object metadata fields."""
    ETag: Optional[str]
    LastModified: Optional[datetime]
    VersionId: Optional[str]
    Expiration: Optional[str]


class ContentResponse(TypedDict, total=False):
    """Content-related fields."""
    ContentLength: Optional[int]
    ContentType: Optional[str]
    ContentDisposition: Optional[str]
    ContentEncoding: Optional[str]
    ContentLanguage: Optional[str]
    ContentRange: Optional[str]
    CacheControl: Optional[str]


class ObjectLockResponse(TypedDict, total=False):
    """Object lock related fields."""
    ObjectLockMode: Optional[str]
    ObjectLockRetainUntilDate: Optional[datetime]
    ObjectLockLegalHoldStatus: Optional[str]


class ReplicationResponse(TypedDict, total=False):
    """Replication related fields."""
    ReplicationStatus: Optional[str] 