from typing import TypedDict


class GetBucketPolicyResponse(TypedDict):
    """Response from S3 GetBucketPolicy operation."""
    Policy: str 