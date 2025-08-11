"""S3 Response Type Definitions."""

# Common response types
from .CommonResponse import (
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    ObjectMetadataResponse,
    ContentResponse,
    ObjectLockResponse,
    ReplicationResponse,
)

# Specific response types
from .CreateBucketResponse import CreateBucketResponse
from .CreateMultipartUploadResponse import CreateMultipartUploadResponse
from .DeleteObjectResponse import DeleteObjectResponse
from .PutObjectResponse import PutObjectResponse
from .DeleteObjectsResponse import DeleteObjectsResponse, DeletedObject, DeleteError
from .HeadObjectResponse import HeadObjectResponse
from .GetObjectTaggingResponse import GetObjectTaggingResponse, Tag
from .PutObjectTaggingResponse import PutObjectTaggingResponse
from .CopyObjectResponse import CopyObjectResponse, CopyObjectResult
from .UploadPartResponse import UploadPartResponse
from .CompleteMultipartUploadResponse import CompleteMultipartUploadResponse
from .GetBucketPolicyResponse import GetBucketPolicyResponse
from .GetBucketNotificationResponse import (
    GetBucketNotificationResponse,
    Filter,
    LambdaFunctionConfiguration,
    TopicConfiguration,
    QueueConfiguration,
    EventBridgeConfiguration,
)
from .GetBucketAccelerateConfigurationResponse import GetBucketAccelerateConfigurationResponse
from .GetObjectResponse import GetObjectResponse
from .GetBucketWebsiteResponse import (
    GetBucketWebsiteResponse,
    RedirectAllRequestsTo,
    Condition,
    Redirect,
    RoutingRule,
    IndexDocument,
    ErrorDocument,
)
from .ListObjectsResponse import (
    ListObjectsResponse,
    S3Object,
    S3CommonPrefix,
    S3Owner,
    S3RestoreStatus,
)

__all__ = [
    # Common response types
    "BaseS3Response",
    "ServerSideEncryptionResponse",
    "ChecksumResponse",
    "ObjectMetadataResponse",
    "ContentResponse",
    "ObjectLockResponse",
    "ReplicationResponse",
    # Core response types
    "CreateBucketResponse",
    "CreateMultipartUploadResponse",
    "DeleteObjectResponse",
    "PutObjectResponse",
    "DeleteObjectsResponse",
    "HeadObjectResponse",
    "GetObjectTaggingResponse",
    "PutObjectTaggingResponse",
    "CopyObjectResponse",
    "UploadPartResponse",
    "CompleteMultipartUploadResponse",
    "GetBucketPolicyResponse",
    "GetBucketNotificationResponse",
    "GetBucketAccelerateConfigurationResponse",
    "GetObjectResponse",
    "GetBucketWebsiteResponse",
    "ListObjectsResponse",
    # Helper types
    "DeletedObject",
    "DeleteError",
    "Tag",
    "CopyObjectResult",
    "Filter",
    "LambdaFunctionConfiguration",
    "TopicConfiguration",
    "QueueConfiguration",
    "EventBridgeConfiguration",
    "RedirectAllRequestsTo",
    "Condition",
    "Redirect",
    "RoutingRule",
    "IndexDocument",
    "ErrorDocument",
    "S3Object",
    "S3CommonPrefix",
    "S3Owner",
    "S3RestoreStatus",
]
