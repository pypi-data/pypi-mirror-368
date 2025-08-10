from typing import Any, Literal, TypedDict, List, NotRequired, Callable, Optional, Dict
from dataclasses import dataclass

from chainsaws.aws.shared.config import APIConfig

BucketACL = Literal["private", "public-read",
                    "public-read-write", "authenticated-read"]

ContentType = Literal[
    # Application types
    "application/json",
    "application/pdf", 
    "application/zip",
    "application/gzip",
    "application/x-tar",
    "application/x-rar-compressed",
    "application/x-7z-compressed",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/rtf",
    "application/javascript",
    "application/typescript",
    "application/x-sql",
    "application/x-sh",
    "application/x-bat",
    "application/x-msdownload",  # exe files
    "application/x-apple-diskimage",  # dmg files
    "application/vnd.android.package-archive",  # apk files
    "application/octet-stream",
    
    # Text types
    "text/plain",
    "text/html",
    "text/css",
    "text/csv",
    "text/xml",
    "text/markdown",
    "text/yaml",
    "text/x-log",
    "text/x-python",
    "text/x-java-source",
    "text/x-c",
    "text/x-c++",
    "text/x-csharp",
    "text/x-php",
    "text/x-ruby",
    "text/x-go",
    "text/x-rust",
    "text/x-swift",
    "text/x-kotlin",
    "text/x-scala",
    "text/x-dockerfile",
    
    # Image types
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/svg+xml",
    "image/webp",
    "image/x-icon",
    "image/bmp",
    "image/tiff",
    "image/x-canon-cr2",
    "image/x-canon-crw",
    "image/x-nikon-nef",
    "image/heic",
    "image/avif",
    
    # Audio types
    "audio/mpeg",  # mp3
    "audio/wav",
    "audio/ogg",
    "audio/flac",
    "audio/aac",
    "audio/x-m4a",
    "audio/aiff",
    "audio/x-ms-wma",
    "audio/opus",
    
    # Video types
    "video/mp4",
    "video/mpeg",
    "video/webm",
    "video/avi",
    "video/quicktime",  # mov
    "video/x-ms-wmv",
    "video/x-flv",
    "video/x-matroska",  # mkv
    "video/3gpp",
    "video/x-msvideo",
    
    # Font types
    "font/ttf",
    "font/otf",
    "font/woff",
    "font/woff2",
    
    # Document types
    "application/epub+zip",
    "application/x-mobipocket-ebook",
    
    # Configuration files
    "application/x-yaml",
    "application/toml",
    "application/x-ini",
]

def get_content_type_from_extension(extension: str) -> ContentType:
    """Get content type from file extension."""
    extension = extension.lower().lstrip(".")
    mapping = {
        # Application files
        "json": "application/json",
        "pdf": "application/pdf",
        "zip": "application/zip",
        "gz": "application/gzip",
        "gzip": "application/gzip",
        "tar": "application/x-tar",
        "rar": "application/x-rar-compressed",
        "7z": "application/x-7z-compressed",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "rtf": "application/rtf",
        "js": "application/javascript",
        "mjs": "application/javascript",
        "ts": "application/typescript",
        "sql": "application/x-sql",
        "sh": "application/x-sh",
        "bash": "application/x-sh",
        "bat": "application/x-bat",
        "cmd": "application/x-bat",
        "exe": "application/x-msdownload",
        "msi": "application/x-msdownload",
        "dmg": "application/x-apple-diskimage",
        "apk": "application/vnd.android.package-archive",
        "epub": "application/epub+zip",
        "mobi": "application/x-mobipocket-ebook",

        # Text files
        "txt": "text/plain",
        "text": "text/plain",
        "log": "text/x-log",
        "html": "text/html",
        "htm": "text/html",
        "css": "text/css",
        "csv": "text/csv",
        "xml": "text/xml",
        "md": "text/markdown",
        "markdown": "text/markdown",
        "yaml": "text/yaml",
        "yml": "text/yaml",
        "toml": "application/toml",
        "ini": "application/x-ini",
        "conf": "text/plain",
        "config": "text/plain",
        "cfg": "text/plain",
        
        # Programming languages
        "py": "text/x-python",
        "pyw": "text/x-python",
        "java": "text/x-java-source",
        "c": "text/x-c",
        "h": "text/x-c",
        "cpp": "text/x-c++",
        "cxx": "text/x-c++",
        "cc": "text/x-c++",
        "hpp": "text/x-c++",
        "cs": "text/x-csharp",
        "php": "text/x-php",
        "rb": "text/x-ruby",
        "go": "text/x-go",
        "rs": "text/x-rust",
        "swift": "text/x-swift",
        "kt": "text/x-kotlin",
        "scala": "text/x-scala",
        "dockerfile": "text/x-dockerfile",

        # Image files
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "webp": "image/webp",
        "ico": "image/x-icon",
        "icon": "image/x-icon",
        "bmp": "image/bmp",
        "tiff": "image/tiff",
        "tif": "image/tiff",
        "cr2": "image/x-canon-cr2",
        "crw": "image/x-canon-crw",
        "nef": "image/x-nikon-nef",
        "heic": "image/heic",
        "avif": "image/avif",

        # Audio files
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "wave": "audio/wav",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
        "aac": "audio/aac",
        "m4a": "audio/x-m4a",
        "aiff": "audio/aiff",
        "aif": "audio/aiff",
        "wma": "audio/x-ms-wma",
        "opus": "audio/opus",

        # Video files
        "mp4": "video/mp4",
        "m4v": "video/mp4",
        "mpeg": "video/mpeg",
        "mpg": "video/mpeg",
        "webm": "video/webm",
        "avi": "video/avi",
        "mov": "video/quicktime",
        "qt": "video/quicktime",
        "wmv": "video/x-ms-wmv",
        "flv": "video/x-flv",
        "mkv": "video/x-matroska",
        "3gp": "video/3gpp",
        "3g2": "video/3gpp",

        # Font files
        "ttf": "font/ttf",
        "otf": "font/otf",
        "woff": "font/woff",
        "woff2": "font/woff2",
    }

    return mapping.get(extension, "application/octet-stream")

@dataclass
class S3APIConfig(APIConfig):
    """Configuration for S3API."""
    
    acl: BucketACL = "private"  # Bucket ACL
    use_accelerate: bool = True  # Config for bucket-level data acceleration

class BucketConfig(TypedDict):
    """Bucket creation/management configuration."""
    
    bucket_name: str
    acl: NotRequired[BucketACL]
    use_accelerate: NotRequired[bool]

class FileUploadConfig(TypedDict):
    """File upload configuration."""
    
    bucket_name: str
    file_name: str
    content_type: NotRequired[Optional[ContentType]]

class ObjectListConfig(TypedDict, total=False):
    """Configuration for listing objects."""
    
    prefix: NotRequired[str]
    continuation_token: NotRequired[Optional[str]]
    start_after: NotRequired[Optional[str]]
    limit: NotRequired[int]

class FileUploadResult(TypedDict):
    """Result of file upload operation."""
    url: str
    object_key: str

class PresignedUrlConfig(TypedDict):
    """Configuration for presigned URL generation."""
    
    bucket_name: str
    object_name: str
    client_method: Literal["get_object", "put_object"]
    content_type: NotRequired[Optional[str]]
    acl: NotRequired[BucketACL]
    expiration: NotRequired[int]

class SelectObjectConfig(TypedDict):
    """Configuration for S3 Select operations."""
    
    bucket_name: str
    object_key: str
    query: str
    input_serialization: NotRequired[Dict[str, Any]]
    output_serialization: NotRequired[Dict[str, Any]]

class CopyObjectResult(TypedDict):
    """Result of copy object operation."""
    
    success: bool
    object_key: str
    url: NotRequired[Optional[str]]
    error_message: NotRequired[Optional[str]]

class BulkUploadItem(TypedDict):
    """Configuration for a single file in bulk upload."""
    
    object_key: str
    data: bytes | str
    content_type: NotRequired[Optional[ContentType]]
    acl: NotRequired[str]

class BulkUploadResult(TypedDict):
    """Result of a bulk upload operation."""
    
    successful: List[Dict[str, str]]
    failed: List[Dict[str, str]]

# S3 Select 관련 타입들을 Literal로 변경
S3SelectFormat = Literal["JSON", "CSV", "PARQUET"]
S3SelectJSONType = Literal["DOCUMENT", "LINES"]

class S3SelectCSVConfig(TypedDict, total=False):
    """Configuration for CSV format in S3 Select."""
    
    file_header_info: NotRequired[Optional[str]]
    delimiter: NotRequired[str]
    quote_character: NotRequired[str]
    quote_escape_character: NotRequired[str]
    comments: NotRequired[Optional[str]]
    record_delimiter: NotRequired[str]

class S3SelectConfig(TypedDict, total=False):
    """Configuration for S3 Select operations."""
    
    query: str
    input_format: S3SelectFormat
    output_format: NotRequired[S3SelectFormat]
    compression_type: NotRequired[Optional[str]]
    json_type: NotRequired[Optional[S3SelectJSONType]]
    csv_input_config: NotRequired[Optional[S3SelectCSVConfig]]
    csv_output_config: NotRequired[Optional[S3SelectCSVConfig]]
    max_rows: NotRequired[Optional[int]]


class UploadConfig(TypedDict, total=False):
    """Configuration for file upload operations."""
    content_type: NotRequired[Optional[ContentType]]
    part_size: NotRequired[int]
    progress_callback: NotRequired[Optional[Callable[[int, int], None]]]
    acl: NotRequired[str]

class DownloadConfig(TypedDict, total=False):
    """Configuration for file download operations."""
    max_retries: NotRequired[int]
    retry_delay: NotRequired[float]
    progress_callback: NotRequired[Optional[Callable[[int, int], None]]]
    chunk_size: NotRequired[int]

class BatchOperationConfig(TypedDict, total=False):
    """Configuration for batch operations."""
    max_workers: NotRequired[Optional[int]]
    chunk_size: NotRequired[int]
    progress_callback: NotRequired[Optional[Callable[[str, int, int], None]]]

class DownloadResult(TypedDict):
    """Download result"""
    object_key: str
    local_path: str
    success: bool
    error: Optional[str]

class ObjectTags(TypedDict):
    """S3 object tags"""
    TagSet: List[Dict[Literal["Key", "Value"], str]]

class BulkDownloadResult(TypedDict):
    """Bulk download operation results"""
    successful: List[DownloadResult]
    failed: List[DownloadResult]

class DirectoryUploadResult(TypedDict):
    """Directory upload operation results"""
    successful: List[FileUploadResult]
    failed: List[Dict[str, str]]  # {file_path: error_message}

class DirectorySyncResult(TypedDict):
    """Directory synchronization results"""
    uploaded: List[str]  # List of uploaded files
    updated: List[str]   # List of updated files
    deleted: List[str]   # List of deleted files
    failed: List[Dict[str, str]]  # List of failed operations

class WebsiteRedirectConfig(TypedDict, total=False):
    """S3 website redirect configuration"""
    HostName: str
    Protocol: Literal["http", "https"]

class WebsiteIndexConfig(TypedDict):
    """S3 website index document configuration"""
    Suffix: str

class WebsiteErrorConfig(TypedDict):
    """S3 website error document configuration"""
    Key: str

class WebsiteRoutingRuleCondition(TypedDict, total=False):
    """S3 website routing rule condition"""
    HttpErrorCodeReturnedEquals: str
    KeyPrefixEquals: str

class WebsiteRoutingRuleRedirect(TypedDict, total=False):
    """S3 website routing rule redirect configuration"""
    HostName: str
    HttpRedirectCode: str
    Protocol: Literal["http", "https"]
    ReplaceKeyPrefixWith: str
    ReplaceKeyWith: str

class WebsiteRoutingRule(TypedDict):
    """S3 website routing rule"""
    Condition: Optional[WebsiteRoutingRuleCondition]
    Redirect: WebsiteRoutingRuleRedirect

class WebsiteConfig(TypedDict, total=False):
    """S3 website configuration"""
    RedirectAllRequestsTo: WebsiteRedirectConfig
    IndexDocument: WebsiteIndexConfig
    ErrorDocument: WebsiteErrorConfig
    RoutingRules: list[WebsiteRoutingRule]

# 기본값을 제공하는 헬퍼 함수들
def create_s3_api_config(**kwargs) -> S3APIConfig:
    """Create S3APIConfig with default values."""
    return S3APIConfig(
        region=kwargs.get("region", "ap-northeast-2"),
        credentials=kwargs.get("credentials"),
        acl=kwargs.get("acl", "private"),
        use_accelerate=kwargs.get("use_accelerate", True),
    )

def create_upload_config(**kwargs) -> UploadConfig:
    """Create UploadConfig with default values."""
    return {
        "content_type": kwargs.get("content_type"),
        "part_size": kwargs.get("part_size", 5 * 1024 * 1024),
        "progress_callback": kwargs.get("progress_callback"),
        "acl": kwargs.get("acl", "private"),
    }

def create_download_config(**kwargs) -> DownloadConfig:
    """Create DownloadConfig with default values."""
    return {
        "max_retries": kwargs.get("max_retries", 3),
        "retry_delay": kwargs.get("retry_delay", 1.0),
        "progress_callback": kwargs.get("progress_callback"),
        "chunk_size": kwargs.get("chunk_size", 8 * 1024 * 1024),
    }

def create_batch_operation_config(**kwargs) -> BatchOperationConfig:
    """Create BatchOperationConfig with default values."""
    return {
        "max_workers": kwargs.get("max_workers"),
        "chunk_size": kwargs.get("chunk_size", 8 * 1024 * 1024),
        "progress_callback": kwargs.get("progress_callback"),
    }

def create_object_list_config(**kwargs) -> ObjectListConfig:
    """Create ObjectListConfig with default values."""
    return {
        "prefix": kwargs.get("prefix", ""),
        "continuation_token": kwargs.get("continuation_token"),
        "start_after": kwargs.get("start_after"),
        "limit": kwargs.get("limit", 1000),
    }
