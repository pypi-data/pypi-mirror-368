import json
import logging
import tempfile
import time
from pathlib import Path
from typing import Any, BinaryIO, Optional, Union, Callable, List, Dict

import boto3
from botocore.exceptions import ClientError
from botocore.response import StreamingBody

from chainsaws.aws.s3.s3_models import (
    BucketACL,
    BucketConfig,
    FileUploadConfig,
    ObjectListConfig,
    PresignedUrlConfig,
    S3APIConfig,
    SelectObjectConfig,
)
from chainsaws.aws.s3.response import ListObjectsResponse
from chainsaws.aws.s3.s3_exception import (
    S3CreateBucketError,
)
from chainsaws.aws.s3.response import (
    CreateBucketResponse,
    CreateMultipartUploadResponse,
    DeleteObjectResponse,
    PutObjectResponse,
    DeleteObjectsResponse,
    HeadObjectResponse,
    GetObjectTaggingResponse,
    PutObjectTaggingResponse,
    CopyObjectResponse,
    UploadPartResponse,
    CompleteMultipartUploadResponse,
    GetBucketPolicyResponse,
    GetBucketNotificationResponse,
    GetBucketAccelerateConfigurationResponse,
    GetObjectResponse,
    GetBucketWebsiteResponse,
)

logger = logging.getLogger(__name__)


class S3:
    def __init__(
        self,
        boto3_session: boto3.Session,
        bucket_name: str,
        config: Optional[S3APIConfig] = None,
    ) -> None:
        self.bucket_name = bucket_name
        self.config = config or S3APIConfig()
        self.region: str = self.config.region
        self.client: boto3.client = boto3_session.client(
            service_name="s3", region_name=self.config.region
        )
        self.resource: boto3.resource = boto3_session.resource(
            service_name="s3", region_name=self.config.region
        )

    def init_bucket(self, config: BucketConfig) -> None:
        """Initialize a bucket, creating it if it doesn't exist.

        Args:
            config: Bucket configuration parameters

        Note:
            If bucket already exists, a warning will be logged

        """
        try:
            try:
                self.client.head_bucket(Bucket=self.bucket_name)
                logger.warning(
                    f"[S3.init_bucket] Bucket '{self.bucket_name}' already exists",
                )
                return
            except ClientError as ex:
                error_code = int(ex.response["Error"]["Code"])
                if error_code == 404:  # If bucket does not exist
                    self.create_bucket()
                    logger.info(
                        f"[S3.init_bucket] Successfully created bucket '{self.bucket_name}'",
                    )

                    if config.get("use_accelerate", True):
                        self.client.put_bucket_accelerate_configuration(
                            Bucket=self.bucket_name,
                            AccelerateConfiguration={"Status": "Enabled"},
                        )
                        logger.info(
                            f"[S3.init_bucket] S3 Transfer Acceleration enabled for bucket '{
                                self.bucket_name
                            }'",
                        )
                else:
                    msg = f"Failed to initialize bucket '{self.bucket_name}': {ex!s}"
                    raise S3CreateBucketError(self.bucket_name, msg) from ex

        except Exception as ex:
            logger.exception(
                f"[S3.init_bucket] Failed to initialize bucket '{self.bucket_name}': {ex!s}"
            )
            raise S3CreateBucketError(self.bucket_name, msg) from ex

    def create_bucket(self) -> CreateBucketResponse:
        """Create a new S3 bucket."""
        try:
            response = self.client.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self.region},
                ACL=self.config.acl,
            )

            return response
        except Exception as ex:
            msg = f"Failed to create bucket '{self.bucket_name}': {ex!s}"
            logger.exception(msg)
            raise S3CreateBucketError(self.bucket_name, msg) from ex

    def update_bucket_acl(self, acl: BucketACL) -> None:
        """Update the ACL for the S3 bucket.

        Args:
            acl: The ACL to apply to the bucket (e.g., 'private', 'public-read').

        """
        try:
            self.client.put_bucket_acl(
                Bucket=self.bucket_name,
                ACL=acl,
            )
            logger.info(
                f"[S3.update_bucket_acl] Updated ACL for bucket '{self.bucket_name}' to '{acl}'"
            )
        except Exception as ex:
            logger.exception(
                f"[S3.update_bucket_acl] Failed to update ACL for bucket '{self.bucket_name}': {
                    ex!s
                }"
            )
            raise

    def update_bucket_policy(self, policy: Union[str, dict]) -> None:
        """Update the bucket policy.

        Args:
            policy: The JSON policy to apply to the bucket.

        """
        bucket_policy = policy
        if isinstance(policy, dict):
            bucket_policy = json.dumps(policy)

        try:
            self.client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=bucket_policy,
            )
            logger.info(f"[S3.update_bucket_policy] Updated policy for bucket '{self.bucket_name}'")
        except Exception as ex:
            logger.exception(
                f"[S3.update_bucket_policy] Failed to update policy for bucket '{
                    self.bucket_name
                }': {ex!s}"
            )
            raise

    def delete_bucket_policy(self) -> None:
        """Delete bucket policy."""
        try:
            self.client.delete_bucket_policy(Bucket=self.bucket_name)
            logger.info(f"[S3.delete_bucket_policy] Deleted policy for bucket '{self.bucket_name}'")
        except Exception as ex:
            logger.exception(f"[S3.delete_bucket_policy] Failed to delete bucket policy: {ex!s}")
            raise

    def upload_binary(self, file_name: str, binary: bytes) -> None:
        # TODO: Appropriate return type
        """Upload binary data to S3."""
        with tempfile.TemporaryFile() as tmp:
            tmp.write(binary)
            tmp.seek(0)
            self.client.upload_fileobj(tmp, self.bucket_name, file_name)

    def delete_binary(self, file_name: str) -> DeleteObjectResponse:
        """Delete an object from S3."""
        return self.resource.Object(self.bucket_name, file_name).delete()

    def download_binary(self, file_name: str) -> bytes:
        """Download binary data from S3."""
        with tempfile.NamedTemporaryFile() as data:
            self.client.download_fileobj(self.bucket_name, file_name, data)
            data.seek(0)
            return data.read()

    def upload_file(
        self, config: FileUploadConfig, file_bytes: Union[bytes, BinaryIO]
    ) -> PutObjectResponse:
        """Upload a file to S3 with content type consideration."""
        return self.client.put_object(
            Bucket=self.bucket_name,
            Key=config["file_name"],
            Body=file_bytes,
            ContentType=config.get("content_type"),
        )

    def select_object_content(self, config: SelectObjectConfig) -> StreamingBody:
        """Execute S3 Select query."""
        return self.client.select_object_content(
            Bucket=self.bucket_name,
            Key=config.object_key,
            RequestProgress={"Enabled": True},
            Expression=config.query,
            ExpressionType="SQL",
            InputSerialization=config.input_serialization,
            OutputSerialization=config.output_serialization,
        )

    def list_objects_v2(self, config: ObjectListConfig) -> ListObjectsResponse:
        """List objects in a bucket with pagination."""
        request_payload = {
            "Bucket": self.bucket_name,
            "Prefix": config.get("prefix", ""),
            "MaxKeys": config.get("limit", 1000),
        }
        if config.get("continuation_token"):
            request_payload["ContinuationToken"] = config["continuation_token"]
        if config.get("start_after"):
            request_payload["StartAfter"] = config["start_after"]

        return self.client.list_objects_v2(**request_payload)

    def delete_object(self, object_key: str) -> bool:
        """Delete an object from S3 bucket.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: The key of the object to delete

        Returns:
            bool: True if deletion was successful, False otherwise

        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )
            return True
        except Exception as ex:
            logger.exception(f"[S3.delete_object] Failed to delete object: {ex!s}")
            return False

    def delete_objects(self, object_keys: List[str]) -> DeleteObjectsResponse:
        """Delete multiple objects from S3 bucket in a single request.

        Args:
            bucket_name: Name of the S3 bucket
            object_keys: List of object keys to delete

        Returns:
            DeleteObjectsResponse: Response containing successful and failed deletions

        """
        objects = [{"Key": key} for key in object_keys]
        try:
            return self.client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    "Objects": objects,
                    "Quiet": False,
                },
            )
        except Exception as ex:
            logger.exception(f"[S3.delete_objects] Failed to delete objects: {ex!s}")
            raise

    def create_presigned_url(self, config: PresignedUrlConfig) -> str:
        """Generate a presigned URL for S3 operations."""
        params = {
            "Bucket": self.bucket_name,
            "Key": config["object_name"],
        }
        if config.get("content_type"):
            params["ContentType"] = config["content_type"]
        if config.get("acl"):
            params["ACL"] = config["acl"]

        return self.client.generate_presigned_url(
            config["client_method"],
            Params=params,
            ExpiresIn=config.get("expiration", 3600),
        )

    def head_object(self, key: str) -> Optional[HeadObjectResponse]:
        """Check if an object exists in S3."""
        try:
            return self.client.head_object(Bucket=self.bucket_name, Key=key)
        except Exception as ex:
            logger.exception(f"[S3.head_object] Failed to head object: {ex!s}")
            return None

    def get_object_tags(self, object_key: str) -> GetObjectTaggingResponse:
        """Get tags for an S3 object.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: The key of the object

        """
        try:
            return self.client.get_object_tagging(
                Bucket=self.bucket_name,
                Key=object_key,
            )
        except Exception as ex:
            logger.exception(f"[S3.get_object_tags] Failed to get object tags: {ex!s}")
            raise

    def put_object_tags(
        self,
        object_key: str,
        tags: Dict[str, str],
    ) -> PutObjectTaggingResponse:
        """Set tags for an S3 object.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: The key of the object
            tags: Dictionary of tag key-value pairs

        """
        tag_set = [{"Key": k, "Value": v} for k, v in tags.items()]
        try:
            return self.client.put_object_tagging(
                Bucket=self.bucket_name,
                Key=object_key,
                Tagging={"TagSet": tag_set},
            )
        except Exception as ex:
            logger.exception(f"[S3.put_object_tags] Failed to put object tags: {ex!s}")
            raise

    def copy_object(
        self,
        source_key: str,
        dest_key: str,
        dest_bucket: Optional[str] = None,
        acl: str = "private",
    ) -> CopyObjectResponse:
        """Copy an object within S3.

        Args:
            source_key: Source object key
            dest_key: Destination object key
            dest_bucket: Optional destination bucket
            acl: Object ACL

        Returns:
            CopyObjectResponse: Copy operation result
        """
        try:
            copy_source = {"Bucket": self.bucket_name, "Key": source_key}

            response = self.client.copy_object(
                CopySource=copy_source,
                Bucket=dest_bucket or self.bucket_name,
                Key=dest_key,
                ACL=acl,
            )

            return response
        except Exception as e:
            logger.error(f"Failed to copy object from {source_key} to {dest_key}: {e}")
            raise

    def get_object_metadata(
        self,
        object_key: str,
        version_id: Optional[str] = None,
    ) -> HeadObjectResponse:
        """Get detailed metadata for an S3 object.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: The key of the object
            version_id: Optional version ID for versioned objects

        """
        try:
            params = {
                "Bucket": self.bucket_name,
                "Key": object_key,
            }
            if version_id:
                params["VersionId"] = version_id

            response = self.client.head_object(**params)
            return response
        except Exception as ex:
            logger.exception(f"[S3.get_object_metadata] Failed to get object metadata: {ex!s}")
            raise

    def create_multipart_upload(
        self,
        object_key: str,
        content_type: Optional[str] = None,
        acl: str = "private",
    ) -> CreateMultipartUploadResponse:
        """Initialize multipart upload.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: The key of the object
            content_type: Optional content type of the file
            acl: Access control list for the object

        Returns:
            CreateMultipartUploadResponse: Multipart upload initialization response

        """
        params = {
            "Bucket": self.bucket_name,
            "Key": object_key,
            "ACL": acl,
        }
        if content_type:
            params["ContentType"] = content_type

        try:
            response = self.client.create_multipart_upload(**params)
            return response
        except Exception as ex:
            logger.exception(
                f"[S3.create_multipart_upload] Failed to create multipart upload: {ex!s}"
            )
            raise

    def upload_part(
        self,
        object_key: str,
        upload_id: str,
        part_number: int,
        body: Union[bytes, BinaryIO],
    ) -> UploadPartResponse:
        """Upload a part in multipart upload.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: The key of the object
            upload_id: Upload ID from create_multipart_upload
            part_number: Part number (1 to 10000)
            body: The data to upload

        """
        try:
            response = self.client.upload_part(
                Bucket=self.bucket_name,
                Key=object_key,
                UploadId=upload_id,
                PartNumber=part_number,
                Body=body,
            )
            return response
        except Exception as ex:
            logger.exception(f"[S3.upload_part] Failed to upload part {part_number}: {ex!s}")
            raise

    def complete_multipart_upload(
        self,
        object_key: str,
        upload_id: str,
        parts: List[Dict],
    ) -> CompleteMultipartUploadResponse:
        """Complete a multipart upload.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: The key of the object
            upload_id: Upload ID from create_multipart_upload
            parts: List of {'PartNumber': int, 'ETag': str} dicts

        """
        try:
            sorted_parts = sorted(parts, key=lambda x: x["PartNumber"])
            formatted_parts = [
                {
                    "PartNumber": part["PartNumber"],
                    "ETag": part["ETag"].strip('"'),
                }
                for part in sorted_parts
            ]

            return self.client.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=object_key,
                UploadId=upload_id,
                MultipartUpload={
                    "Parts": formatted_parts,
                },
            )
        except Exception as ex:
            logger.exception(
                f"[S3.complete_multipart_upload] Failed to complete multipart upload: {ex!s}"
            )
            raise

    def abort_multipart_upload(
        self,
        object_key: str,
        upload_id: str,
    ) -> None:
        """Abort a multipart upload.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: The key of the object
            upload_id: Upload ID to abort

        """
        try:
            self.client.abort_multipart_upload(
                Bucket=self.bucket_name,
                Key=object_key,
                UploadId=upload_id,
            )
        except Exception as ex:
            logger.exception(
                f"[S3.abort_multipart_upload] Failed to abort multipart upload: {ex!s}"
            )
            raise

    def put_bucket_policy(self, policy: str) -> None:
        """Put bucket policy."""
        try:
            return self.client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=policy,
            )
        except self.client.exceptions.NoSuchBucket as e:
            msg = f"Bucket {self.bucket_name} does not exist"
            raise ValueError(msg) from e
        except Exception:
            raise

    def get_bucket_policy(self) -> GetBucketPolicyResponse:
        """Get bucket policy."""
        try:
            return self.client.get_bucket_policy(Bucket=self.bucket_name)
        except self.client.exceptions.NoSuchBucketPolicy:
            return {"Policy": "{}"}
        except self.client.exceptions.NoSuchBucket as e:
            msg = f"Bucket {self.bucket_name} does not exist"
            raise ValueError(msg) from e
        except Exception as ex:
            logger.exception(str(ex))
            raise

    def put_bucket_notification_configuration(
        self,
        config: Dict[str, Any],
    ) -> None:
        """Put bucket notification configuration."""
        try:
            self.client.put_bucket_notification_configuration(
                Bucket=self.bucket_name,
                NotificationConfiguration={"LambdaFunctionConfigurations": [config]},
            )
        except Exception as ex:
            logger.exception(
                f"[S3.put_bucket_notification_configuration] Failed to set notification: {ex!s}"
            )
            raise

    def get_bucket_notification_configuration(
        self,
    ) -> GetBucketNotificationResponse:
        """Get bucket notification configuration."""
        try:
            response = self.client.get_bucket_notification_configuration(
                Bucket=self.bucket_name,
            )
            return response
        except Exception as ex:
            logger.exception(
                f"[S3.get_bucket_notification_configuration] Failed to get notification: {ex!s}"
            )
            raise

    def put_public_access_block(
        self,
        public_access_block_configuration: Dict[str, bool],
    ) -> None:
        """Configure public access block settings for the bucket.

        Args:
            bucket_name: Name of the S3 bucket
            public_access_block_configuration: Dictionary containing the following boolean settings:
                - BlockPublicAcls: Block public access to buckets and objects granted through new ACLs
                - IgnorePublicAcls: Ignore public ACLs on buckets and objects
                - BlockPublicPolicy: Block public bucket policies
                - RestrictPublicBuckets: Block public and cross-account access to buckets with public policies

        Example:
            ```python
            s3.put_public_access_block(
                bucket_name="my-bucket",
                public_access_block_configuration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
            ```

        """
        try:
            self.client.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration=public_access_block_configuration,
            )
            logger.info(
                f"[S3.put_public_access_block] Updated public access block configuration for bucket '{
                    self.bucket_name
                }'",
            )
        except Exception as ex:
            logger.exception(
                f"[S3.put_public_access_block] Failed to update public access block configuration: {
                    ex!s
                }",
            )
            raise

    def get_bucket_accelerate_configuration(self) -> GetBucketAccelerateConfigurationResponse:
        """Get bucket accelerate configuration.

        Returns:
            GetBucketAccelerateConfigurationResponse: Accelerate configuration response
        """
        try:
            return self.client.get_bucket_accelerate_configuration(Bucket=self.bucket_name)
        except Exception as e:
            logger.error(f"Failed to get bucket accelerate configuration: {e!s}")
            raise

    def put_bucket_accelerate_configuration(self, status: str) -> None:
        """Set bucket accelerate configuration.

        Args:
            status: Acceleration status ('Enabled' or 'Suspended')
        """
        try:
            self.client.put_bucket_accelerate_configuration(
                Bucket=self.bucket_name, AccelerateConfiguration={"Status": status}
            )
        except Exception as e:
            logger.error(f"Failed to put bucket accelerate configuration: {e!s}")
            raise

    def download_file(
        self,
        object_key: str,
        file_path: Union[str, Path],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        """Download a file from S3.

        Args:
            object_key: Source object key
            file_path: Target file path
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            progress_callback: Optional callback for progress tracking
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        for attempt in range(max_retries + 1):
            try:
                response = self.client.get_object(Bucket=self.bucket_name, Key=object_key)

                file_size = response["ContentLength"]
                downloaded = 0

                with open(file_path, "wb") as f:
                    while True:
                        chunk = response["Body"].read(8 * 1024 * 1024)  # 8MB chunks
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, file_size)

                return  # 성공적으로 다운로드 완료

            except Exception as e:
                if attempt == max_retries:
                    logger.error(
                        f"Failed to download {object_key} after {max_retries} attempts: {e}"
                    )
                    raise
                else:
                    logger.warning(f"Download attempt {attempt + 1} failed for {object_key}: {e}")
                    time.sleep(retry_delay)

    def get_object(self, object_key: str) -> GetObjectResponse:
        """Get an object from S3.

        Args:
            object_key: The key of the object to get

        Returns:
            GetObjectResponse: The response from S3 containing the object data and metadata

        Raises:
            ClientError: If the object does not exist or other AWS errors occur
        """
        try:
            return self.client.get_object(Bucket=self.bucket_name, Key=object_key)
        except Exception as e:
            logger.error(f"Failed to get object {object_key}: {e}")
            raise

    def check_key_exists(self, object_key: str) -> bool:
        """Check if an object exists in S3.

        Args:
            object_key: The key of the object to check

        Returns:
            bool: True if object exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise
        except Exception:
            return False

    def get_bucket_website(self) -> GetBucketWebsiteResponse:
        """Get website configuration for the bucket."""
        try:
            return self.client.get_bucket_website(Bucket=self.bucket_name)
        except self.client.exceptions.NoSuchWebsiteConfiguration:
            return {}
        except Exception as ex:
            logger.exception(f"[S3.get_bucket_website] Failed to get website configuration: {ex!s}")
            raise

    def put_bucket_website(self, website_config: Dict[str, Any]) -> None:
        """Update website configuration for the bucket."""
        try:
            self.client.put_bucket_website(
                Bucket=self.bucket_name, WebsiteConfiguration=website_config
            )
            logger.info(
                f"[S3.put_bucket_website] Updated website configuration for bucket '{
                    self.bucket_name
                }'"
            )
        except Exception as ex:
            logger.exception(
                f"[S3.put_bucket_website] Failed to update website configuration: {ex!s}"
            )
            raise

    def delete_bucket_website(self) -> None:
        """Delete website configuration for the bucket."""
        try:
            self.client.delete_bucket_website(Bucket=self.bucket_name)
            logger.info(
                f"[S3.delete_bucket_website] Deleted website configuration for bucket '{
                    self.bucket_name
                }'"
            )
        except Exception as ex:
            logger.exception(
                f"[S3.delete_bucket_website] Failed to delete website configuration: {ex!s}"
            )
            raise

    def wait_for_public_access_block_configuration(
        self, max_attempts: int = 10, delay: float = 0.5
    ) -> None:
        """Wait for public access block configuration to be applied.

        Args:
            max_attempts: Maximum number of attempts to check configuration
            delay: Delay between attempts in seconds
        """
        import time
        from botocore.exceptions import ClientError

        for attempt in range(max_attempts):
            try:
                response = self.client.get_public_access_block(Bucket=self.bucket_name)
                config = response["PublicAccessBlockConfiguration"]

                # If all settings are False, configuration is ready
                if not any(config.values()):
                    return

            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                    # If there's no configuration, it means it's been successfully removed
                    return

            if attempt < max_attempts - 1:
                time.sleep(delay)

        msg = f"Timeout waiting for public access block configuration to be applied on bucket '{
            self.bucket_name
        }'"
        raise TimeoutError(msg)
