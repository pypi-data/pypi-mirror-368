class S3Error(Exception):
    """Base class for all S3 exceptions."""

    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)


class S3CreateBucketError(S3Error):
    """Exception raised for S3 bucket creation errors."""

    def __init__(self, bucket_name: str, reason: str) -> None:
        message = f"Failed to create bucket '{bucket_name}': {reason}"
        super().__init__(message)
        self.bucket_name = bucket_name
        self.reason = reason


class S3InvalidBucketNameError(S3Error):
    """Exception raised for invalid S3 bucket names."""

    def __init__(self, bucket_name: str, reason: str) -> None:
        message = f"Invalid bucket name '{bucket_name}': {reason}"
        super().__init__(message)
        self.bucket_name = bucket_name
        self.reason = reason


class InvalidObjectKeyError(S3Error):
    """Exception raised for invalid S3 object keys."""

    def __init__(self, object_key: str, reason: str) -> None:
        message = f"Invalid object key '{object_key}': {reason}"
        super().__init__(message)
        self.object_key = object_key
        self.reason = reason


class InvalidFileUploadError(S3Error):
    """Exception raised for invalid S3 file uploads."""

    def __init__(self, file_name: str, reason: str) -> None:
        message = f"Failed to upload file '{file_name}': {reason}"
        super().__init__(message)
        self.file_name = file_name
        self.reason = reason


class S3FileNotFoundError(S3Error, FileNotFoundError):
    """Exception raised for file not found."""

    def __init__(self, file_path: str) -> None:
        message = f"File not found: {file_path}"
        super().__init__(message)
        self.file_path = file_path


class S3BucketPolicyGetError(S3Error):
    """Exception raised for S3 bucket policy get errors."""

    def __init__(self, bucket_name: str, reason: str) -> None:
        message = f"Failed to get bucket policy for '{bucket_name}': {reason}"
        super().__init__(message)
        self.bucket_name = bucket_name
        self.reason = reason


class S3BucketPolicyUpdateError(S3Error):
    """Exception raised for S3 bucket policy update errors."""

    def __init__(self, bucket_name: str, reason: str) -> None:
        message = f"Failed to update bucket policy for '{
            bucket_name}': {reason}"
        super().__init__(message)
        self.bucket_name = bucket_name
        self.reason = reason


class S3LambdaPermissionAddError(S3Error):
    """Exception raised for S3 lambda permission add errors."""

    def __init__(self, function_name: str, reason: str) -> None:
        message = f"Failed to add Lambda permission for '{
            function_name}': {reason}"
        super().__init__(message)
        self.function_name = function_name
        self.reason = reason


class S3LambdaNotificationAddError(S3Error):
    """Exception raised for S3 lambda notification add errors."""

    def __init__(self, bucket_name: str, function_name: str, reason: str) -> None:
        message = f"Failed to add Lambda notification for bucket '{
            bucket_name}' and function '{function_name}': {reason}"
        super().__init__(message)
        self.bucket_name = bucket_name
        self.function_name = function_name
        self.reason = reason


class S3LambdaNotificationRemoveError(S3Error):
    """Exception raised for S3 lambda notification remove errors."""

    def __init__(self, bucket_name: str, function_name: str, reason: str) -> None:
        message = f"Failed to remove Lambda notification for bucket '{
            bucket_name}' and function '{function_name}': {reason}"
        super().__init__(message)
        self.bucket_name = bucket_name
        self.function_name = function_name
        self.reason = reason


class S3MultipartUploadError(S3Error):
    """Exception raised for multipart upload errors."""

    def __init__(self, object_key: str, upload_id: str, reason: str) -> None:
        message = f"Multipart upload failed for '{
            object_key}' (upload_id: {upload_id}): {reason}"
        super().__init__(message)
        self.object_key = object_key
        self.upload_id = upload_id
        self.reason = reason


class S3DownloadError(S3Error):
    """Exception raised for download errors."""

    def __init__(self, object_key: str, reason: str) -> None:
        message = f"Failed to download '{object_key}': {reason}"
        super().__init__(message)
        self.object_key = object_key
        self.reason = reason


class S3StreamingError(S3Error):
    """Exception raised for streaming errors."""

    def __init__(self, object_key: str, reason: str) -> None:
        message = f"Streaming error for '{object_key}': {reason}"
        super().__init__(message)
        self.object_key = object_key
        self.reason = reason


class S3OperationTimeoutError(S3Error):
    """Exception raised when an S3 operation times out."""

    def __init__(self, operation: str, timeout: int) -> None:
        message = f"Operation '{operation}' timed out after {timeout} seconds"
        super().__init__(message)
        self.operation = operation
        self.timeout = timeout


class S3WebsiteConfigurationError(Exception):
    """Exception raised for S3 website configuration errors"""

    def __init__(self, bucket_name: str, message: str) -> None:
        self.bucket_name = bucket_name
        self.message = message
        super().__init__(f"Failed to configure website for bucket '{
            bucket_name}': {message}")


class S3WebsiteConfigurationGetError(Exception):
    """Exception raised when getting S3 website configuration fails"""

    def __init__(self, bucket_name: str, message: str) -> None:
        self.bucket_name = bucket_name
        self.message = message
        super().__init__(f"Failed to get website configuration for bucket '{
            bucket_name}': {message}")


class S3WebsiteConfigurationDeleteError(Exception):
    """Exception raised when deleting S3 website configuration fails"""

    def __init__(self, bucket_name: str, message: str) -> None:
        self.bucket_name = bucket_name
        self.message = message
        super().__init__(f"Failed to delete website configuration for bucket '{
            bucket_name}': {message}")
