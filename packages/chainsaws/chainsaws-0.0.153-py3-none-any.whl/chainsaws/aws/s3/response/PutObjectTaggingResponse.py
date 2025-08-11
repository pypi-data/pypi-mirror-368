from .CommonResponse import ObjectMetadataResponse


class PutObjectTaggingResponse(ObjectMetadataResponse, total=False):
    """Response from S3 PutObjectTagging operation."""
    pass 