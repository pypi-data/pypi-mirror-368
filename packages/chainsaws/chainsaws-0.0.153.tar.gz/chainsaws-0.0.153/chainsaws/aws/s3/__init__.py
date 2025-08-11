"""AWS S3 Client Wrapper

This module provides a high-level interface for AWS S3 operations with enhanced features:
- Simplified file upload and download operations
- Directory operations (upload, download, sync)
- Batch operations with parallel processing
- Progress tracking and retry mechanisms
- Type-safe interfaces with comprehensive type hints

✨ New! Simple and intuitive methods for everyday tasks:
- s3.put() / s3.get() - Simple upload/download
- s3.exists() / s3.delete() / s3.copy() - File operations
- s3.list() - List objects with filters
- s3.url() / s3.upload_url() - Generate presigned URLs
- s3.query_json() / s3.query_csv() - Easy S3 Select queries
- s3.put_many() / s3.get_many() - Batch operations
"""

from chainsaws.aws.s3.s3 import S3API
from chainsaws.aws.s3.s3_models import (
    BucketACL,
    BucketConfig,
    BulkUploadItem,
    BulkUploadResult,
    ContentType,
    CopyObjectResult,
    FileUploadConfig,
    FileUploadResult,
    ObjectListConfig,
    PresignedUrlConfig,
    S3APIConfig,
    S3SelectCSVConfig,
    S3SelectFormat,
    S3SelectJSONType,
    SelectObjectConfig,
    UploadConfig,
    DownloadConfig,
    BatchOperationConfig,
    DownloadResult,
    BulkDownloadResult,
    ObjectTags,
    DirectoryUploadResult,
    DirectorySyncResult,
    get_content_type_from_extension,
    create_s3_api_config,
    create_upload_config,
    create_download_config,
    create_batch_operation_config,
    create_object_list_config,
)
from chainsaws.aws.s3.response import S3Object
from chainsaws.aws.s3.s3_exception import (
    InvalidObjectKeyError,
    S3BucketPolicyUpdateError,
    S3BucketPolicyGetError,
    S3LambdaPermissionAddError,
    S3LambdaNotificationAddError,
    S3LambdaNotificationRemoveError,
    S3MultipartUploadError,
    S3StreamingError,
)

__all__ = [
    "S3API",
    # Models
    "BucketACL",
    "BucketConfig",
    "BulkUploadItem",
    "BulkUploadResult",
    "ContentType",
    "CopyObjectResult",
    "FileUploadConfig",
    "FileUploadResult",
    "ObjectListConfig",
    "PresignedUrlConfig",
    "S3APIConfig",
    "S3Object",
    "S3SelectCSVConfig",
    "S3SelectFormat",
    "S3SelectJSONType",
    "SelectObjectConfig",
    "UploadConfig",
    "DownloadConfig",
    "BatchOperationConfig",
    "DownloadResult",
    "BulkDownloadResult",
    "ObjectTags",
    "DirectoryUploadResult",
    "DirectorySyncResult",
    # Helper functions
    "get_content_type_from_extension",
    "create_s3_api_config",
    "create_upload_config",
    "create_download_config",
    "create_batch_operation_config",
    "create_object_list_config",
    # Exceptions
    "InvalidObjectKeyError",
    "S3BucketPolicyUpdateError",
    "S3BucketPolicyGetError",
    "S3LambdaPermissionAddError",
    "S3LambdaNotificationAddError",
    "S3LambdaNotificationRemoveError",
    "S3MultipartUploadError",
    "S3StreamingError",
]
