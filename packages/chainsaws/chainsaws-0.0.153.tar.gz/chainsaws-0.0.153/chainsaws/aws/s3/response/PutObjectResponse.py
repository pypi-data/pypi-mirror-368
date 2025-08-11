from .CommonResponse import (
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    ObjectMetadataResponse
)


class PutObjectResponse(
    BaseS3Response,
    ServerSideEncryptionResponse,
    ChecksumResponse,
    ObjectMetadataResponse,
    total=False
):
    """Response from S3 PutObject operation."""
    pass 