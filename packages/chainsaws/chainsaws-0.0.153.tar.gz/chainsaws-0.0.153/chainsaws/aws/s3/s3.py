import io
import os
import json
import logging
import fnmatch
import hashlib
from pathlib import Path
from typing import Any, BinaryIO, Optional, Callable, Union, List, Generator, TypeVar, Literal, Dict
from urllib.parse import urljoin
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed

from chainsaws.aws.s3._s3_internal import S3
from chainsaws.aws.s3.s3_models import (
    BucketConfig,
    BulkUploadItem,
    BulkUploadResult,
    ContentType,
    CopyObjectResult,
    FileUploadConfig,
    FileUploadResult,
    PresignedUrlConfig,
    S3APIConfig,
    S3SelectCSVConfig,
    S3SelectFormat,
    S3SelectJSONType,
    SelectObjectConfig,
    UploadConfig,
    DownloadConfig,
    BatchOperationConfig,
    BulkDownloadResult,
    ObjectTags,
    DirectoryUploadResult,
    DirectorySyncResult,
    WebsiteConfig,
    BucketACL,
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
    S3WebsiteConfigurationError,
    S3WebsiteConfigurationGetError,
    S3WebsiteConfigurationDeleteError,
)
from chainsaws.aws.shared import session
from .stream_manager import StreamManager

logger = logging.getLogger(__name__)

T = TypeVar('T')


class S3API:
    """High-level S3 API for AWS S3 operations."""

    def __init__(self, bucket_name: str, config: Optional[S3APIConfig] = None) -> None:
        """Initialize S3 client.

        Args:
            bucket_name: Target bucket name
            config: Optional S3 configuration
        """
        self.bucket_name = bucket_name
        self.config = config or create_s3_api_config()
        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None,
        )
        self.s3 = S3(
            boto3_session=self.boto3_session,
            bucket_name=bucket_name,
            config=config,
        )
        self.stream = StreamManager(self)  # Initialize StreamManager

    def init_s3_bucket(self) -> None:
        """Initialize S3 bucket."""
        bucket_config: BucketConfig = {
            "bucket_name": self.bucket_name, 
            "acl": self.config.acl, 
            "use_accelerate": self.config.use_accelerate
        }
        return self.s3.init_bucket(config=bucket_config)

    # ========================================
    # 💡 간단하고 직관적인 기본 메서드들
    # ========================================

    def put(
        self, 
        object_key: str, 
        data: Union[bytes, str], 
        content_type: Optional[ContentType] = None,
        acl: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> FileUploadResult:
        """🎯 가장 간단한 업로드 인터페이스
        
        Args:
            object_key: S3 객체 키
            data: 업로드할 데이터 (bytes 또는 str)
            content_type: 컨텐츠 타입 (자동 감지됨)
            acl: 접근 권한 ("private", "public-read" 등)
            progress_callback: 진행상황 콜백 함수
        
        Returns:
            FileUploadResult: 업로드 결과
            
        Example:
            >>> s3.put("hello.txt", "Hello World!")
            >>> s3.put("data.json", json_data, content_type="application/json", acl="public-read")
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        # content_type 자동 감지
        if content_type is None:
            extension = object_key.split(".")[-1] if "." in object_key else ""
            content_type = get_content_type_from_extension(extension)
            
        config = {
            "content_type": content_type,
            "acl": acl or "private",
            "progress_callback": progress_callback
        }
        return self.upload_file(object_key, data, config=config)

    def get(
        self, 
        object_key: str, 
        local_path: Optional[Union[str, Path]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        chunk_size: int = 8 * 1024 * 1024
    ) -> Union[bytes, None]:
        """🎯 가장 간단한 다운로드 인터페이스
        
        Args:
            object_key: S3 객체 키
            local_path: 로컬 저장 경로 (선택사항)
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간격 (초)
            progress_callback: 진행상황 콜백 함수
            chunk_size: 청크 크기 (bytes)
            
        Returns:
            bytes: local_path가 없으면 파일 내용 반환, 있으면 None
            
        Example:
            >>> content = s3.get("hello.txt")  # 메모리로 가져오기
            >>> s3.get("hello.txt", "local.txt", max_retries=5)  # 파일로 저장
        """
        if local_path:
            config = {
                "max_retries": max_retries,
                "retry_delay": retry_delay,
                "progress_callback": progress_callback,
                "chunk_size": chunk_size
            }
            self.download_file(object_key, local_path, config=config)
            return None
        else:
            # 메모리로 가져오기
            response = self.s3.get_object(object_key)
            return response['Body'].read()

    def exists(self, object_key: str) -> bool:
        """🎯 객체 존재 여부 확인
        
        Args:
            object_key: S3 객체 키
            
        Returns:
            bool: 객체 존재 여부
            
        Example:
            >>> if s3.exists("important.txt"):
            >>>     print("파일이 존재합니다!")
        """
        return self.check_key_exists(object_key)

    def delete(self, object_key: str) -> bool:
        """🎯 객체 삭제
        
        Args:
            object_key: S3 객체 키
            
        Returns:
            bool: 삭제 성공 여부
            
        Example:
            >>> s3.delete("old-file.txt")
        """
        return self.delete_object(object_key)

    def list(
        self, 
        prefix: str = "", 
        limit: int = 1000,
        continuation_token: Optional[str] = None,
        start_after: Optional[str] = None
    ) -> Generator[S3Object, None, None]:
        """🎯 객체 목록 조회
        
        Args:
            prefix: 접두사 필터
            limit: 최대 개수
            continuation_token: 페이지네이션 토큰
            start_after: 이 키 이후부터 조회
            
        Yields:
            S3Object: S3 객체 정보
            
        Example:
            >>> for obj in s3.list("logs/", limit=100):
            >>>     print(f"Found: {obj['Key']}")
        """
        config = {
            "prefix": prefix, 
            "limit": limit,
            "continuation_token": continuation_token,
            "start_after": start_after
        }
        return self.generate_object_keys(**config)

    def copy(
        self, 
        source_key: str, 
        dest_key: str,
        dest_bucket: Optional[str] = None,
        acl: str = "private"
    ) -> bool:
        """🎯 객체 복사
        
        Args:
            source_key: 원본 객체 키
            dest_key: 대상 객체 키
            dest_bucket: 대상 버킷 (기본값: 현재 버킷)
            acl: 접근 권한
            
        Returns:
            bool: 복사 성공 여부
            
        Example:
            >>> s3.copy("original.txt", "backup.txt")
            >>> s3.copy("file.txt", "file.txt", dest_bucket="other-bucket")
        """
        try:
            self.s3.copy_object(source_key, dest_key, dest_bucket=dest_bucket, acl=acl)
            return True
        except Exception:
            return False

    def size(self, object_key: str) -> Optional[int]:
        """🎯 객체 크기 조회
        
        Args:
            object_key: S3 객체 키
            
        Returns:
            int: 객체 크기 (bytes), 없으면 None
            
        Example:
            >>> file_size = s3.size("large-file.zip")
            >>> print(f"File size: {file_size / 1024 / 1024:.2f} MB")
        """
        try:
            metadata = self.s3.get_object_metadata(object_key)
            return metadata.get('ContentLength')
        except Exception:
            return None

    def url(self, object_key: str, expiration: int = 3600) -> str:
        """🎯 다운로드용 Presigned URL 생성
        
        Args:
            object_key: S3 객체 키
            expiration: URL 만료 시간 (초)
            
        Returns:
            str: Presigned URL
            
        Example:
            >>> download_url = s3.url("file.pdf", expiration=7200)  # 2시간
        """
        return self.create_presigned_url_get_object(object_key, expiration)

    def upload_url(self, object_key: str, content_type: Optional[ContentType] = None, expiration: int = 3600) -> str:
        """🎯 업로드용 Presigned URL 생성
        
        Args:
            object_key: S3 객체 키
            content_type: 컨텐츠 타입
            expiration: URL 만료 시간 (초)
            
        Returns:
            str: Presigned URL
            
        Example:
            >>> upload_url = s3.upload_url("upload.jpg", "image/jpeg")
        """
        return self.create_presigned_url_put_object(object_key, content_type, expiration=expiration)

    # ========================================
    # 💡 향상된 업로드 메서드들
    # ========================================

    def upload(
        self, 
        object_key: str, 
        data: Union[bytes, str, BinaryIO],
        content_type: Optional[ContentType] = None,
        part_size: int = 5 * 1024 * 1024,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        acl: BucketACL = "private",
        large_file: bool = False
    ) -> FileUploadResult:
        """🎯 통합 업로드 메서드 - 크기에 따라 자동으로 최적화
        
        Args:
            object_key: S3 객체 키
            data: 업로드할 데이터
            content_type: 컨텐츠 타입 (자동 감지됨)
            part_size: 멀티파트 업로드시 파트 크기
            progress_callback: 진행상황 콜백 함수
            acl: 접근 권한
            large_file: 강제로 멀티파트 업로드 사용
            
        Returns:
            FileUploadResult: 업로드 결과
            
        Example:
            >>> s3.upload("file.txt", "Hello")  # 작은 파일
            >>> s3.upload("big.zip", large_data, large_file=True)  # 강제 멀티파트
        """
        # 크기 계산
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        size = len(data) if isinstance(data, bytes) else None
        
        # content_type 자동 감지
        if content_type is None:
            extension = object_key.split(".")[-1] if "." in object_key else ""
            content_type = get_content_type_from_extension(extension)
        
        # 5MB 이상이거나 강제 설정시 멀티파트 업로드
        if large_file or (size and size > 5 * 1024 * 1024):
            return self.upload_large_file(
                object_key=object_key, 
                file_bytes=data,
                content_type=content_type,
                part_size=part_size,
                progress_callback=progress_callback
            )
        else:
            config = {
                "content_type": content_type,
                "part_size": part_size,
                "progress_callback": progress_callback,
                "acl": acl
            }
            return self.upload_file(object_key, data, config=config)

    # ========================================
    # 💡 향상된 쿼리 메서드들  
    # ========================================

    def query_json(self, object_key: str, sql: str, json_type: S3SelectJSONType = "LINES") -> Generator[dict, None, None]:
        """🎯 JSON 파일 쿼리
        
        Args:
            object_key: JSON 파일 키
            sql: SQL 쿼리
            json_type: JSON 타입 ("LINES" 또는 "DOCUMENT")
            
        Yields:
            dict: 쿼리 결과
            
        Example:
            >>> for record in s3.query_json("logs.jsonl", "SELECT * WHERE level='ERROR'"):
            >>>     print(record)
        """
        return self.select_query(
            object_key=object_key,
            query=sql,
            input_format="JSON",
            json_type=json_type
        )

    def query_csv(self, object_key: str, sql: str, has_header: bool = True, delimiter: str = ",") -> Generator[dict, None, None]:
        """🎯 CSV 파일 쿼리
        
        Args:
            object_key: CSV 파일 키
            sql: SQL 쿼리
            has_header: 헤더 포함 여부
            delimiter: 구분자
            
        Yields:
            dict: 쿼리 결과
            
        Example:
            >>> for record in s3.query_csv("users.csv", "SELECT name, email WHERE age > 25"):
            >>>     print(record)
        """
        csv_config = {
            "file_header_info": "USE" if has_header else "NONE",
            "delimiter": delimiter
        }
        return self.select_query(
            object_key=object_key,
            query=sql,
            input_format="CSV",
            csv_input_config=csv_config
        )

    # ========================================
    # 💡 향상된 배치 작업 메서드들
    # ========================================

    def put_many(
        self, 
        items: List[Dict[str, Union[str, bytes]]], 
        max_workers: Optional[int] = None,
        chunk_size: int = 8 * 1024 * 1024,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> BulkUploadResult:
        """🎯 여러 파일 동시 업로드
        
        Args:
            items: 업로드할 아이템 리스트 [{"key": "파일키", "data": "데이터"}, ...]
            max_workers: 최대 워커 수 (기본값: CPU 수에 따라 자동)
            chunk_size: 청크 크기
            progress_callback: 진행상황 콜백 함수 (file_key, current, total)
            
        Returns:
            BulkUploadResult: 업로드 결과
            
        Example:
            >>> items = [
            >>>     {"key": "file1.txt", "data": "content1"},
            >>>     {"key": "file2.txt", "data": "content2"}
            >>> ]
            >>> result = s3.put_many(items, max_workers=4)
        """
        # items를 BulkUploadItem 형태로 변환
        bulk_items = []
        for item in items:
            bulk_item = {
                "object_key": item["key"],
                "data": item["data"]
            }
            # 추가 필드들 복사
            for key, value in item.items():
                if key not in ["key", "data"]:
                    bulk_item[key] = value
            bulk_items.append(bulk_item)
        
        config = {
            "max_workers": max_workers,
            "chunk_size": chunk_size,
            "progress_callback": progress_callback
        }
        return self.bulk_upload(bulk_items, config=config)

    def get_many(
        self, 
        object_keys: List[str], 
        output_dir: Union[str, Path],
        max_workers: Optional[int] = None,
        chunk_size: int = 8 * 1024 * 1024,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> BulkDownloadResult:
        """🎯 여러 파일 동시 다운로드
        
        Args:
            object_keys: 다운로드할 객체 키 리스트
            output_dir: 출력 디렉토리
            max_workers: 최대 워커 수 (기본값: CPU 수에 따라 자동)
            chunk_size: 청크 크기
            progress_callback: 진행상황 콜백 함수 (file_key, current, total)
            
        Returns:
            BulkDownloadResult: 다운로드 결과
            
        Example:
            >>> keys = ["file1.txt", "file2.txt", "file3.txt"]
            >>> result = s3.get_many(keys, "./downloads", max_workers=4)
        """
        config = {
            "max_workers": max_workers,
            "chunk_size": chunk_size,
            "progress_callback": progress_callback
        }
        return self.download_multiple_files(object_keys, output_dir, config=config)

    def delete_many(self, object_keys: List[str]) -> Dict[str, List[str]]:
        """🎯 여러 객체 동시 삭제
        
        Args:
            object_keys: 삭제할 객체 키 리스트
            
        Returns:
            dict: {"successful": [...], "failed": [...]}
            
        Example:
            >>> keys = ["old1.txt", "old2.txt", "old3.txt"]
            >>> result = s3.delete_many(keys)
        """
        try:
            response = self.s3.delete_objects(object_keys)
            
            successful = []
            failed = []
            
            # 성공한 삭제들
            if 'Deleted' in response:
                successful = [obj['Key'] for obj in response['Deleted']]
            
            # 실패한 삭제들
            if 'Errors' in response:
                failed = [f"{err['Key']}: {err['Message']}" for err in response['Errors']]
            
            return {"successful": successful, "failed": failed}
        except Exception as e:
            return {"successful": [], "failed": [f"Batch delete failed: {str(e)}"]}

    # ========================================
    # 💡 편의 메서드들
    # ========================================

    def info(self, object_key: str) -> Optional[Dict[str, Any]]:
        """🎯 객체 상세 정보 조회
        
        Args:
            object_key: S3 객체 키
            
        Returns:
            dict: 객체 메타데이터 정보
            
        Example:
            >>> info = s3.info("file.txt")
            >>> print(f"Size: {info['ContentLength']}, Modified: {info['LastModified']}")
        """
        try:
            return self.s3.get_object_metadata(object_key)
        except Exception:
            return None

    def tags(self, object_key: str, tags: Optional[Dict[str, str]] = None) -> Optional[Dict[str, str]]:
        """🎯 객체 태그 조회/설정
        
        Args:
            object_key: S3 객체 키
            tags: 설정할 태그 (None이면 조회만)
            
        Returns:
            dict: 현재 태그들
            
        Example:
            >>> s3.tags("file.txt", {"env": "prod", "version": "1.0"})  # 태그 설정
            >>> current_tags = s3.tags("file.txt")  # 태그 조회
        """
        if tags is not None:
            # 태그 설정
            self.put_object_tags(object_key, tags)
        
        # 태그 조회
        try:
            response = self.get_object_tags(object_key)
            return {tag['Key']: tag['Value'] for tag in response.get('TagSet', [])}
        except Exception:
            return {}

    # Upload Operations
    def upload_file(
        self,
        object_key: str,
        file_bytes: Union[bytes, BinaryIO],
        config: Optional[UploadConfig] = None,
    ) -> FileUploadResult:
        """Upload a file to S3.

        Args:
            object_key: Target object key
            file_bytes: File content or file-like object
            config: Upload configuration

        Returns:
            FileUploadResult: Upload result with URL
        """
        config = config or create_upload_config()
        upload_config: FileUploadConfig = {
            "bucket_name": self.bucket_name,
            "file_name": object_key,
            "content_type": config.get("content_type"),
        }

        self.s3.upload_file(upload_config, file_bytes)

        base_url = self._get_base_url(
            use_accelerate=self.config.use_accelerate)
        return {
            "url": urljoin(base_url, object_key),
            "object_key": object_key,
        }

    def upload_binary(self, file_name: str, binary: bytes, content_type: Optional[ContentType] = None) -> str:
        """Upload binary data to S3.

        Args:
            file_name: Target file name
            binary: Binary data
            content_type: Optional content type

        Returns:
            str: URL of uploaded object
        """
        if content_type:
            config: FileUploadConfig = {
                "bucket_name": self.bucket_name,
                "file_name": file_name,
                "content_type": content_type,
            }
            self.s3.upload_file(config, binary)
        else:
            self.s3.upload_binary(file_name, binary)
        
        base_url = self._get_base_url(use_accelerate=self.config.use_accelerate)
        return urljoin(base_url, file_name)

    def _get_base_url(self, bucket_name: Optional[str] = None, use_accelerate: bool = False) -> str:
        """Generate base URL for S3 bucket.

        Args:
            bucket_name: Optional bucket name (defaults to self.bucket_name)
            use_accelerate: Whether to use S3 Transfer Acceleration

        Returns:
            str: Base URL for the S3 bucket

        """
        target_bucket = bucket_name or self.bucket_name

        if use_accelerate:
            return f"https://{target_bucket}.s3-accelerate.amazonaws.com/"

        return f"https://{target_bucket}.s3.{self.s3.region}.amazonaws.com/"

    def upload_items_for_select(self, file_name: str, item_list: List[Dict[str, Any]]) -> None:
        """Upload JSON items for S3 Select queries."""
        if not all(isinstance(item, dict) for item in item_list):
            msg = "All items must be dictionaries"
            raise InvalidObjectKeyError(msg)

        json_string = "\n".join(json.dumps(item) for item in item_list)
        return self.upload_binary(file_name, json_string.encode("utf-8"))

    # TODO: Make as typed
    def get_object(self, object_key: str) -> Dict[str, Any]:
        """Get an object from S3.

        Args:
            object_key: The key of the object to get

        Returns:
            dict: The response from S3 containing the object data and metadata
        """
        return self.s3.get_object(object_key)

    def upload_large_file(
        self,
        object_key: str,
        file_bytes: Union[bytes, BinaryIO],
        content_type: Optional[ContentType] = None,
        part_size: int = 5 * 1024 * 1024,  # 5MB
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> FileUploadResult:
        """Upload a large file using multipart upload.

        Args:
            object_key: The key to store the object under
            file_bytes: File data as bytes or file-like object
            content_type: Optional content type
            part_size: Size of each part in bytes (minimum 5MB)
            progress_callback: Optional callback function to monitor progress.
                            Takes (bytes_uploaded, total_bytes) as arguments.

        Returns:
            FileUploadResult: An object containing the public URL and the object key of the uploaded file

        Raises:
            S3MultipartUploadError: If the multipart upload fails
            InvalidObjectKeyError: If the object key is invalid
            InvalidFileUploadError: If the file upload configuration is invalid
        """
        if content_type is None:
            extension = object_key.split(".")[-1] if "." in object_key else ""
            content_type = get_content_type_from_extension(extension)

        if isinstance(file_bytes, bytes):
            file_bytes = io.BytesIO(file_bytes)

        # Get total file size
        file_bytes.seek(0, io.SEEK_END)
        total_size = file_bytes.tell()
        file_bytes.seek(0)

        # If file is smaller than part_size, use regular upload
        if total_size <= part_size:
            return self.upload_file(
                object_key=object_key,
                file_bytes=file_bytes.read(),
                config={"content_type": content_type},
            )

        try:
            upload_id = self.s3.create_multipart_upload(
                object_key=object_key,
                content_type=content_type,
            )

            parts = []
            part_number = 1
            bytes_uploaded = 0

            while True:
                data = file_bytes.read(part_size)
                if not data:
                    break

                part = self.s3.upload_part(
                    object_key=object_key,
                    upload_id=upload_id,
                    part_number=part_number,
                    body=data,
                )
                parts.append({
                    "PartNumber": part_number,
                    "ETag": part["ETag"],
                })

                bytes_uploaded += len(data)
                if progress_callback:
                    progress_callback(bytes_uploaded, total_size)

                part_number += 1

            self.s3.complete_multipart_upload(
                object_key=object_key,
                upload_id=upload_id,
                parts=parts,
            )

            base_url = self._get_base_url(
                use_accelerate=self.config.use_accelerate)

            return FileUploadResult(
                url=urljoin(base_url, object_key),
                object_key=object_key,
            )

        except Exception as ex:
            logger.exception(f"Failed to upload large file: {ex!s}")
            if "upload_id" in locals():
                try:
                    self.s3.abort_multipart_upload(
                        object_key=object_key,
                        upload_id=upload_id,
                    )
                except Exception as abort_ex:
                    logger.error(
                        f"Failed to abort multipart upload: {abort_ex!s}")

            raise S3MultipartUploadError(
                object_key=object_key,
                upload_id=upload_id if "upload_id" in locals() else "N/A",
                reason=str(ex)
            ) from ex

    # Download Operations
    def download_file(
        self,
        object_key: str,
        file_path: Union[str, Path],
        config: Optional[DownloadConfig] = None,
    ) -> None:
        """Download a file from S3.

        Args:
            object_key: Source object key
            file_path: Target file path
            config: Download configuration
        """
        config = config or create_download_config()
        self.s3.download_file(
            object_key=object_key,
            file_path=file_path,
            max_retries=config.get("max_retries", 3),
            retry_delay=config.get("retry_delay", 1),
            progress_callback=config.get("progress_callback"),
        )

    def stream_object(
        self,
        object_key: str,
        chunk_size: int = 8192,
    ) -> Generator[bytes, None, None]:
        """Stream an object from S3 in chunks.

        Args:
            object_key: The key of the object to stream
            chunk_size: Size of each chunk in bytes

        Yields:
            bytes: Chunks of the object data

        Raises:
            S3StreamingError: If streaming fails
        """
        try:
            response = self.s3.get_object(object_key)
            stream = response["Body"]

            while True:
                chunk = stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        except Exception as ex:
            raise S3StreamingError(object_key=object_key,
                                   reason=str(ex)) from ex

    # Batch Operations
    @contextmanager
    def batch_operation(self, config: Optional[BatchOperationConfig] = None) -> Generator["S3API", None, None]:
        """Context manager for batch operations.

        Args:
            config: Batch operation configuration

        Yields:
            S3API: Self for batch operations
        """
        config = config or create_batch_operation_config()
        try:
            yield self
        finally:
            # Cleanup after batch operations
            pass

    def bulk_upload(
        self,
        items: List[BulkUploadItem],
        config: Optional[BatchOperationConfig] = None,
    ) -> BulkUploadResult:
        """Upload multiple files in parallel.

        Args:
            items: List of items to upload
            config: Batch operation configuration

        Returns:
            BulkUploadResult: Upload results
        """

        config = config or create_batch_operation_config()
        max_workers = config.get("max_workers") or min(32, len(items))
        results = {"successful": [], "failed": []}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {
                executor.submit(
                    self.upload_file,
                    item.object_key,
                    item.data,
                    UploadConfig(
                        content_type=item.content_type,
                        part_size=config.get("chunk_size", 5 * 1024 * 1024),
                        progress_callback=lambda current, total: config.get("progress_callback")(
                            item.object_key, current, total) if config.get("progress_callback") else None
                    )
                ): item
                for item in items
            }

            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results["successful"].append({
                        "object_key": item.object_key,
                        "url": result["url"]
                    })
                except Exception as e:
                    results["failed"].append({
                        "object_key": item.object_key,
                        "error": str(e)
                    })

        return results

    def download_multiple_files(
        self,
        object_keys: List[str],
        output_dir: Union[str, Path],
        config: Optional[BatchOperationConfig] = None,
    ) -> BulkDownloadResult:
        """Download multiple files in parallel.

        Args:
            object_keys: List of object keys to download
            output_dir: Target directory
            config: Batch operation configuration

        Returns:
            BulkDownloadResult: Download results with successful and failed downloads
        """
        config = config or create_batch_operation_config()
        max_workers = config.get("max_workers") or min(32, len(object_keys))
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        results: BulkDownloadResult = {"successful": [], "failed": []}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_key = {
                executor.submit(
                    self.download_file,
                    object_key,
                    output_dir / Path(object_key).name,
                    DownloadConfig(
                        chunk_size=config.get("chunk_size", 5 * 1024 * 1024),
                        progress_callback=lambda current, total: config.get("progress_callback")(
                            object_key, current, total) if config.get("progress_callback") else None
                    )
                ): object_key
                for object_key in object_keys
            }

            for future in as_completed(future_to_key):
                object_key = future_to_key[future]
                local_path = str(output_dir / Path(object_key).name)
                try:
                    future.result()
                    results["successful"].append({
                        "object_key": object_key,
                        "local_path": local_path,
                        "success": True,
                        "error": None
                    })
                except Exception as e:
                    logger.error(f"Failed to download {object_key}: {e}")
                    results["failed"].append({
                        "object_key": object_key,
                        "local_path": local_path,
                        "success": False,
                        "error": str(e)
                    })

        return results

    def copy_object(
        self,
        source_key: str,
        dest_key: str,
        dest_bucket: Optional[str] = None,
        acl: BucketACL = "private",
    ) -> CopyObjectResult:
        """Copy an object within S3.

        Args:
            source_key: Source object key
            dest_key: Destination object key
            dest_bucket: Optional destination bucket
            acl: Object ACL

        Returns:
            CopyObjectResult: Copy operation result
        """
        return self.s3.copy_object(
            source_key=source_key,
            dest_key=dest_key,
            dest_bucket=dest_bucket,
            acl=acl,
        )

    def enable_transfer_acceleration(self) -> bool:
        """Enable transfer acceleration for the bucket.

        Returns:
            bool: True if successful
        """
        try:
            self.s3.put_bucket_accelerate_configuration('Enabled')
            return True
        except Exception as e:
            logger.error(f"Failed to enable transfer acceleration: {e}")
            return False

    # Management Operations
    def delete_object(self, object_key: str) -> bool:
        """Delete an object from S3.

        Args:
            object_key: Object key to delete

        Returns:
            bool: True if successful
        """
        return self.s3.delete_object(object_key)

    def delete_objects(self, object_keys: List[str]) -> bool:
        """Delete multiple objects from S3.

        Args:
            object_keys: List of object keys to delete

        Returns:
            bool: True if successful
        """
        return self.s3.delete_objects(object_keys)

    # Utility Operations
    def check_key_exists(self, object_key: str) -> bool:
        """Check if an object exists.

        Args:
            object_key: Object key to check

        Returns:
            bool: True if exists
        """
        return self.s3.check_key_exists(object_key)

    def get_url_by_object_key(self, object_key: str, use_accelerate: bool = False) -> Optional[str]:
        """Get URL for an object.

        Args:
            object_key: Object key
            use_accelerate: Whether to use transfer acceleration

        Returns:
            Optional[str]: Object URL if exists
        """
        return self._get_base_url(use_accelerate=use_accelerate) + object_key if object_key else None

    # Performance Operations
    def optimize_transfer_settings(self) -> None:
        """Optimize transfer settings for better performance."""
        if self._check_transfer_acceleration_eligibility():
            self.enable_transfer_acceleration()
    # Context Managers

    @contextmanager
    def upload_session(self, config: Optional[UploadConfig] = None) -> Generator["S3API", None, None]:
        """Context manager for upload operations.

        Args:
            config: Upload configuration

        Yields:
            S3API: Self for upload operations
        """
        config = config or create_upload_config()
        try:
            yield self
        finally:
            # Cleanup if needed
            pass

    @contextmanager
    def download_session(self, config: Optional[DownloadConfig] = None) -> Generator["S3API", None, None]:
        """Context manager for download operations.

        Args:
            config: Download configuration

        Yields:
            S3API: Self for download operations
        """
        config = config or create_download_config()
        try:
            yield self
        finally:
            # Cleanup if needed
            pass

    def generate_object_keys(
        self,
        prefix: str = '',
        start_after: Optional[str] = None,
        limit: int = 1000,
    ) -> Generator[S3Object, None, None]:
        """Generate object keys with pagination."""
        continuation_token = None

        while True:
            list_config = create_object_list_config(
                prefix=prefix,
                continuation_token=continuation_token,
                start_after=start_after,
                limit=limit,
            )

            response = self.s3.list_objects_v2(list_config)

            yield from response.get("Contents", [])

            continuation_token = response.get("NextContinuationToken")
            if not continuation_token:
                break

    def select_query(
        self,
        object_key: str,
        query: str,
        input_format: S3SelectFormat = "JSON",
        output_format: S3SelectFormat = "JSON",
        json_type: S3SelectJSONType = "LINES",
        compression_type: Optional[str] = None,
        csv_input_config: Optional[S3SelectCSVConfig] = None,
        csv_output_config: Optional[S3SelectCSVConfig] = None,
        max_rows: Optional[int] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Execute S3 Select query with advanced options.

        Args:
            object_key: S3 object key
            query: SQL query to execute
            input_format: Input format (JSON, CSV, PARQUET)
            output_format: Output format (JSON, CSV)
            json_type: JSON type for input (DOCUMENT or LINES)
            compression_type: Input compression type
            csv_input_config: CSV input configuration
            csv_output_config: CSV output configuration
            max_rows: Maximum number of rows to return

        Yields:
            Query results as dictionaries

        Example:
            ```python
            # Query JSON Lines
            results = s3.select_query(
                object_key="data/logs.jsonl",
                query="SELECT * FROM s3object s WHERE s.level = 'ERROR'",
                input_format="JSON",
                json_type="LINES"
            )

            # Query CSV with custom configuration
            results = s3.select_query(
                object_key="data/users.csv",
                query="SELECT name, email FROM s3object WHERE age > 25",
                input_format="CSV",
                csv_input_config=S3SelectCSVConfig(
                    file_header_info="USE",
                    delimiter=","
                )
            )
            ```

        """
        input_serialization = {}
        output_serialization = {}

        # Configure input serialization
        if input_format == "JSON":
            input_serialization["JSON"] = {"Type": json_type}
        elif input_format == "CSV":
            csv_config = csv_input_config or S3SelectCSVConfig()
            input_serialization["CSV"] = csv_config.to_dict(
                exclude_none=True)
        elif input_format == "PARQUET":
            input_serialization["Parquet"] = {}

        # Configure output serialization
        if output_format == "JSON":
            output_serialization["JSON"] = {}
        elif output_format == "CSV":
            csv_config = csv_output_config or S3SelectCSVConfig()
            output_serialization["CSV"] = csv_config.to_dict(
                exclude_none=True)

        if compression_type:
            input_serialization["CompressionType"] = compression_type

        select_config: SelectObjectConfig = {
            "bucket_name": self.bucket_name,
            "object_key": object_key,
            "query": query,
            "input_serialization": input_serialization,
            "output_serialization": output_serialization,
        }

        row_count = 0
        for record in self.s3.select_object_content(select_config):
            if max_rows and row_count >= max_rows:
                break
            yield record
            row_count += 1

    def upload_jsonlines(
        self,
        object_key: str,
        items: List[Dict[str, Any]],
        compression: Optional[Literal["gzip", "bzip2"]] = None,
    ) -> str:
        """Upload items as JSON Lines format for efficient S3 Select queries.

        Args:
            object_key: Target object key
            items: List of dictionaries to upload
            compression: Optional compression (gzip, bzip2)

        Returns:
            URL of uploaded object

        Example:
            ```python
            url = s3.upload_jsonlines(
                "data/logs.jsonl",
                [
                    {"timestamp": "2023-01-01", "level": "INFO", "message": "Started"},
                    {"timestamp": "2023-01-01", "level": "ERROR", "message": "Failed"}
                ],
                compression="gzip"
            )
            ```

        """
        if not all(isinstance(item, dict) for item in items):
            msg = "All items must be dictionaries"
            raise ValueError(msg)

        # Convert to JSON Lines format
        json_lines = "\n".join(json.dumps(item) for item in items)
        data = json_lines.encode("utf-8")

        # Apply compression if requested
        if compression:
            if compression.lower() == "gzip":
                import gzip
                data = gzip.compress(data)
            elif compression.lower() == "bzip2":
                import bz2
                data = bz2.compress(data)
            else:
                msg = "Unsupported compression format"
                raise ValueError(msg)

        # Upload with appropriate content type
        content_type = "application/x-jsonlines"
        if compression:
            content_type += f"+{compression}"

        return self.upload_binary(object_key, data, content_type=content_type)

    def make_bucket_public(self) -> None:
        """Make the S3 bucket publicly accessible.
        This method:
        1. Disables bucket's public access block settings
        2. Updates the bucket policy to allow public access.

        Example:
            ```python
            s3 = S3API(bucket_name="my-bucket")
            s3.make_bucket_public()
            ```

        Raises:
            Exception: If any step of making the bucket public fails

        """
        try:
            logger.info(f"Disabling public access block for bucket '{
                        self.bucket_name}'")
            self.s3.put_public_access_block(
                {
                    "BlockPublicAcls": False,
                    "IgnorePublicAcls": False,
                    "BlockPublicPolicy": False,
                    "RestrictPublicBuckets": False,
                },
            )

            # Wait for public access block configuration to be applied
            self.s3.wait_for_public_access_block_configuration()

            # Update bucket policy to allow public read access
            logger.info("Updating bucket policy to allow public access")
            public_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/*",
                    },
                ],
            }
            self.s3.update_bucket_policy(public_policy)

            logger.info(f"Successfully made bucket '{
                        self.bucket_name}' public")
        except Exception as e:
            logger.exception(f"Failed to make bucket public: {e!s}")
            raise

    def make_bucket_private(self) -> None:
        """Make the S3 bucket private.
        This method:
        1. Removes any bucket policy
        2. Enables bucket's public access block settings.

        Example:
            ```python
            s3 = S3API(bucket_name="my-bucket")
            s3.make_bucket_private()
            ```

        Raises:
            Exception: If any step of making the bucket private fails

        """
        try:
            logger.info(f"Removing bucket policy from '{self.bucket_name}'")
            self.s3.delete_bucket_policy()

            logger.info(f"Enabling public access block for bucket '{
                        self.bucket_name}'")
            self.s3.put_public_access_block(
                {
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True,
                },
            )

            logger.info(f"Successfully made bucket '{
                        self.bucket_name}' private")
        except Exception as e:
            logger.exception(f"Failed to make bucket private: {e!s}")
            raise

    def _check_transfer_acceleration_eligibility(self) -> bool:
        """Check if the bucket is eligible for S3 Transfer Acceleration.

        Returns:
            bool: True if the bucket is eligible for acceleration
        """
        try:
            response = self.s3.get_bucket_accelerate_configuration()
            current_status = response.get('Status', 'Suspended')
            return current_status != 'Suspended'
        except Exception as ex:
            logger.warning(
                f"Failed to check transfer acceleration status: {ex!s}")
            return False

    def upload_directory(
        self,
        local_dir: Union[str, Path],
        prefix: str = "",
        exclude_patterns: Optional[List[str]] = None,
    ) -> DirectoryUploadResult:
        """Upload an entire local directory to S3.

        Args:
            local_dir: Local directory path
            prefix: S3 prefix to prepend to uploaded files
            exclude_patterns: List of glob patterns to exclude

        Returns:
            DirectoryUploadResult: Upload results with successful and failed uploads
        """
        local_dir = Path(local_dir)
        if not local_dir.is_dir():
            raise ValueError(f"'{local_dir}' is not a directory")

        exclude_patterns = exclude_patterns or []
        results: DirectoryUploadResult = {"successful": [], "failed": []}

        for file_path in local_dir.rglob("*"):
            if not file_path.is_file():
                continue

            relative_path = str(file_path.relative_to(local_dir))
            if any(fnmatch.fnmatch(relative_path, pattern) for pattern in exclude_patterns):
                continue

            object_key = f"{prefix.rstrip(
                '/')}/{relative_path}" if prefix else relative_path

            try:
                with open(file_path, "rb") as f:
                    result = self.upload_file(
                        object_key=object_key,
                        file_bytes=f,
                    )
                    results["successful"].append(result)
            except Exception as e:
                results["failed"].append({
                    relative_path: str(e)
                })

        return results

    def download_directory(
        self,
        prefix: str,
        local_dir: Union[str, Path],
        include_patterns: Optional[List[str]] = None,
    ) -> None:
        """Download all files under an S3 prefix to a local directory.

        Args:
            prefix: S3 prefix to download from
            local_dir: Local directory to download to
            include_patterns: List of glob patterns to include
        """
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)

        include_patterns = include_patterns or ["*"]

        # List all objects
        for obj in self.generate_object_keys(prefix=prefix):
            # Check pattern matching
            relative_key = obj["Key"][len(prefix):].lstrip("/")
            if not any(fnmatch.fnmatch(relative_key, pattern) for pattern in include_patterns):
                continue

            # Create download path
            download_path = local_dir / relative_key
            download_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            self.download_file(
                object_key=obj["Key"],
                file_path=download_path,
            )

    def sync_directory(
        self,
        local_dir: Union[str, Path],
        prefix: str = "",
        delete: bool = False,
    ) -> DirectorySyncResult:
        """Sync a local directory with S3 (similar to aws s3 sync).

        Args:
            local_dir: Local directory to sync
            prefix: S3 prefix to sync with
            delete: Whether to delete files that exist in the destination but not in the source

        Returns:
            DirectorySyncResult: Sync results with uploaded, updated, deleted, and failed files
        """
        local_dir = Path(local_dir)
        if not local_dir.is_dir():
            raise ValueError(f"'{local_dir}' is not a directory")

        results: DirectorySyncResult = {
            "uploaded": [],
            "updated": [],
            "deleted": [],
            "failed": []
        }

        local_files = {
            str(f.relative_to(local_dir)): f
            for f in local_dir.rglob("*")
            if f.is_file()
        }

        s3_objects = {
            obj["Key"][len(prefix):].lstrip("/"): obj
            for obj in self.generate_object_keys(prefix=prefix)
        }

        for relative_path, local_file in local_files.items():
            object_key = f"{prefix.rstrip(
                '/')}/{relative_path}" if prefix else relative_path

            try:
                if relative_path not in s3_objects:
                    with open(local_file, "rb") as f:
                        self.upload_file(object_key=object_key, file_bytes=f)
                    results["uploaded"].append(relative_path)
                else:
                    # Compare using strong signal:
                    # - If ETag has '-', it's a multipart upload; compare size only
                    # - Otherwise, ETag is MD5 of object; compare md5
                    s3_obj = s3_objects[relative_path]
                    s3_etag = s3_obj.get("ETag", "").strip('"')
                    s3_size = s3_obj.get("Size")

                    local_size = os.path.getsize(local_file)

                    need_update = False
                    if "-" in s3_etag:
                        # Multipart: ETag is not simple MD5
                        need_update = (s3_size is None) or (local_size != s3_size)
                    else:
                        # Single-part: compare MD5 digest
                        def _md5_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
                            md5 = hashlib.md5()
                            with open(path, "rb") as fh:
                                while True:
                                    chunk = fh.read(chunk_size)
                                    if not chunk:
                                        break
                                    md5.update(chunk)
                            return md5.hexdigest()

                        local_md5 = _md5_file(local_file)
                        need_update = local_md5 != s3_etag

                    if need_update:
                        with open(local_file, "rb") as f:
                            self.upload_file(
                                object_key=object_key, file_bytes=f)
                        results["updated"].append(relative_path)
            except Exception as e:
                results["failed"].append({relative_path: str(e)})

        if delete:
            for relative_path in s3_objects:
                if relative_path not in local_files:
                    object_key = f"{prefix.rstrip(
                        '/')}/{relative_path}" if prefix else relative_path
                    try:
                        self.delete_object(object_key)
                        results["deleted"].append(relative_path)
                    except Exception as e:
                        results["failed"].append({relative_path: str(e)})

        return results

    def find_objects(
        self,
        pattern: str = "*",
        recursive: bool = True,
        max_items: Optional[int] = None,
    ) -> Generator[S3Object, None, None]:
        """Find objects in S3 using glob patterns.

        Args:
            pattern: Glob pattern to match against object keys
            recursive: Whether to search recursively
            max_items: Maximum number of items to return

        Yields:
            S3Object: Matching S3 objects
        """
        import fnmatch
        from pathlib import PurePath

        # 패턴을 prefix와 실제 패턴으로 분리
        pattern_path = PurePath(pattern)
        if pattern_path.is_absolute():
            pattern = str(pattern_path.relative_to(pattern_path.root))

        prefix = str(pattern_path.parent) if str(
            pattern_path.parent) != "." else ""
        name_pattern = pattern_path.name

        # 재귀 검색이 아닌 경우 패턴 조정
        if not recursive and "**" not in pattern:
            name_pattern = f"*/{name_pattern}" if prefix else name_pattern

        count = 0
        for obj in self.generate_object_keys(prefix=prefix):
            if max_items and count >= max_items:
                break

            # 패턴 매칭
            relative_key = obj["Key"][len(prefix):].lstrip(
                "/") if prefix else obj["Key"]
            if fnmatch.fnmatch(relative_key, name_pattern):
                count += 1
                yield obj

    def get_website_configuration(self) -> WebsiteConfig:
        """Get website configuration for the bucket.

        Returns:
            WebsiteConfig: Website configuration information

        Raises:
            S3WebsiteConfigurationGetError: If getting website configuration fails

        Example:
            ```python
            config = s3.get_website_configuration()
            if "IndexDocument" in config:
                print(f"Index document: {config['IndexDocument']['Suffix']}")
            ```
        """
        try:
            return self.s3.get_bucket_website()
        except Exception as ex:
            raise S3WebsiteConfigurationGetError(
                self.bucket_name, str(ex)) from ex

    def configure_website(self, config: WebsiteConfig) -> None:
        """Configure website settings for the bucket.

        Args:
            config: Website configuration information

        Raises:
            S3WebsiteConfigurationError: If website configuration fails

        Example:
            ```python
            # Static website configuration
            s3.configure_website({
                "IndexDocument": {"Suffix": "index.html"},
                "ErrorDocument": {"Key": "error.html"}
            })

            # Redirect all requests configuration
            s3.configure_website({
                "RedirectAllRequestsTo": {
                    "HostName": "www.example.com",
                    "Protocol": "https"
                }
            })

            # Routing rules configuration
            s3.configure_website({
                "IndexDocument": {"Suffix": "index.html"},
                "RoutingRules": [{
                    "Condition": {
                        "KeyPrefixEquals": "docs/"
                    },
                    "Redirect": {
                        "ReplaceKeyPrefixWith": "documents/"
                    }
                }]
            })
            ```
        """
        try:
            self.s3.put_bucket_website(config)
        except Exception as ex:
            raise S3WebsiteConfigurationError(
                self.bucket_name, str(ex)) from ex

    def delete_website_configuration(self) -> None:
        """Delete website configuration for the bucket.

        Raises:
            S3WebsiteConfigurationDeleteError: If deleting website configuration fails

        Example:
            ```python
            s3.delete_website_configuration()
            ```
        """
        try:
            self.s3.delete_bucket_website()
        except Exception as ex:
            raise S3WebsiteConfigurationDeleteError(
                self.bucket_name, str(ex)) from ex

    def get_website_endpoint(self) -> str:
        """Get the website endpoint URL for the bucket.

        Returns:
            str: Website endpoint URL

        Example:
            ```python
            endpoint = s3.get_website_endpoint()
            print(f"Website URL: http://{endpoint}")
            ```
        """
        return f"{self.bucket_name}.s3-website-{self.s3.region}.amazonaws.com"

    def select(self, object_key: str, query: str) -> Dict[str, Any]:
        """Execute S3 Select query."""
        select_config: SelectObjectConfig = {
            "bucket_name": self.bucket_name,
            "object_key": object_key,
            "query": query,
            "input_serialization": {"JSON": {"Type": "DOCUMENT"}},
            "output_serialization": {"JSON": {}},
        }

        return self.s3.select_object_content(select_config)

    def create_presigned_url_put_object(
        self,
        object_key: str,
        content_type: Optional[str] = None,
        acl: Optional[str] = None,
        expiration: Optional[int] = None,
    ) -> str:
        """Generate presigned URL for PUT operation."""

        if not content_type:
            extension = object_key.split(".")[-1] if "." in object_key else ""
            content_type = get_content_type_from_extension(extension)

        config: PresignedUrlConfig = {
            "bucket_name": self.bucket_name,
            "object_name": object_key,
            "client_method": "put_object",
            "content_type": content_type,
            "acl": acl or "private",
            "expiration": expiration or 3600,
        }
        return self.s3.create_presigned_url(config)

    def create_presigned_url_get_object(
        self,
        object_key: str,
        expiration: int = 3600,
    ) -> str:
        """Generate presigned URL for GET operation."""
        config: PresignedUrlConfig = {
            "bucket_name": self.bucket_name,
            "object_name": object_key,
            "client_method": "get_object",
            "expiration": expiration,
        }
        return self.s3.create_presigned_url(config)

    def get_object_tags(self, object_key: str) -> ObjectTags:
        """Get tags for an object."""
        return self.s3.get_object_tags(object_key=object_key)

    def put_object_tags(self, object_key: str, tags: Dict[str, str]) -> Dict:
        """Set tags for an object."""
        return self.s3.put_object_tags(object_key=object_key, tags=tags)

    def get_object_metadata(
        self,
        object_key: str,
        version_id: Optional[str] = None,
    ) -> dict:
        """Get detailed metadata for an object."""
        return self.s3.get_object_metadata(
            object_key=object_key,
            version_id=version_id,
        )

    def put_bucket_policy(self, policy: Dict[str, Any]) -> None:
        """Put/Update bucket policy.

        Args:
            policy: Dictionary containing the bucket policy

        Example:
            ```python
            s3.put_bucket_policy({
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "AllowCloudFrontServicePrincipal",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudfront.amazonaws.com"
                    },
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/*"
                        }
                    }
                }]
            })
            ```

        Raises:
            Exception: If policy update fails

        """
        try:
            return self.s3.put_bucket_policy(policy=json.dumps(policy))
        except Exception as e:
            msg = f"Failed to put bucket policy: {e!s}"
            logger.exception(msg)
            raise S3BucketPolicyUpdateError(
                bucket_name=self.bucket_name,
                reason=msg
            ) from e

    def get_bucket_policy(self) -> Dict[str, Any]:
        """Get current bucket policy.

        Returns:
            Dict containing the bucket policy. Empty dict if no policy exists.

        Raises:
            Exception: If policy retrieval fails

        """
        try:
            policy = self.s3.get_bucket_policy()
            return json.loads(policy.get("Policy", "{}"))
        except Exception as e:
            logger.exception(f"Failed to get bucket policy: {e!s}")
            raise S3BucketPolicyGetError from e

    def add_lambda_notification(
        self,
        lambda_function_arn: str,
        events: Optional[List[str]] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add Lambda function notification configuration to S3 bucket.

        Args:
            lambda_function_arn: Lambda function ARN
            events: List of S3 events to trigger Lambda. Defaults to ['s3:ObjectCreated:*']
            prefix: Optional key prefix filter
            suffix: Optional key suffix filter
            id: Optional configuration ID

        Example:
            ```python
            # Trigger Lambda when PNG files are uploaded to 'images/' prefix
            s3.add_lambda_notification(
                lambda_function_arn="arn:aws:lambda:region:account:function:image-processor",
                events=['s3:ObjectCreated:Put'],
                prefix='images/',
                suffix='.png'
            )
            ```

        """
        from chainsaws.aws.lambda_client.lambda_client import LambdaAPI

        if not events:
            events = ["s3:ObjectCreated:*"]

        if not id:
            import uuid
            id = f"LambdaTrigger-{str(uuid.uuid4())[:8]}"

        try:
            lambda_api = LambdaAPI(self.config)
            try:
                lambda_api.add_permission(
                    function_name=lambda_function_arn,
                    statement_id=f"S3Trigger-{id}",
                    action="lambda:InvokeFunction",
                    principal="s3.amazonaws.com",
                    source_arn=f"arn:aws:s3:::{self.bucket_name}",
                )
            except Exception as e:
                if "ResourceConflictException" not in str(e):
                    raise S3LambdaPermissionAddError from e

            config = {
                "LambdaFunctionArn": lambda_function_arn,
                "Events": events,
            }

            if prefix or suffix:
                filter_rules = []
                if prefix:
                    filter_rules.append({"Name": "prefix", "Value": prefix})
                if suffix:
                    filter_rules.append({"Name": "suffix", "Value": suffix})
                config["Filter"] = {"Key": {"FilterRules": filter_rules}}

            return self.s3.put_bucket_notification_configuration(
                config={id: config},
            )

        except Exception as e:
            logger.exception(f"Failed to add Lambda notification: {e!s}")
            raise S3LambdaNotificationAddError from e

    def remove_lambda_notification(
        self,
        id: str,
        lambda_function_arn: Optional[str] = None,
        remove_permission: bool = True,
    ) -> None:
        """Remove Lambda function notification configuration.

        Args:
            id: Configuration ID to remove
            lambda_function_arn: Optional Lambda ARN (needed for permission removal)
            remove_permission: Whether to remove Lambda permission

        Example:
            ```python
            s3.remove_lambda_notification(
                id="LambdaTrigger-12345678",
                lambda_function_arn="arn:aws:lambda:region:account:function:image-processor"
            )
            ```

        """
        try:
            # Get current configuration
            current_config = self.s3.get_bucket_notification_configuration()

            # Remove specified configuration
            if id in current_config:
                del current_config[id]
                self.s3.put_bucket_notification_configuration(
                    config=current_config,
                )

            # Remove Lambda permission if requested
            if remove_permission and lambda_function_arn:
                from chainsaws.aws.lambda_client.lambda_client import LambdaAPI
                lambda_api = LambdaAPI(self.config)
                try:
                    lambda_api.remove_permission(
                        function_name=lambda_function_arn,
                        statement_id=f"S3Trigger-{id}",
                    )
                except Exception as e:
                    if "ResourceNotFoundException" not in str(e):
                        logger.warning(
                            f"Failed to remove Lambda permission: {e!s}")

        except Exception as e:
            logger.exception(f"Failed to remove Lambda notification: {e!s}")
            raise S3LambdaNotificationRemoveError from e
