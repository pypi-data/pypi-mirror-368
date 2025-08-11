"""
Lambda Event Types for S3 triggers
"""
from typing import List, TypedDict


class S3UserIdentity(TypedDict):
    principalId: str


class S3RequestParameters(TypedDict):
    sourceIPAddress: str


class S3ResponseElements(TypedDict, total=False):
    x_amz_request_id: str  # alias="x-amz-request-id"
    x_amz_id_2: str  # alias="x-amz-id-2"


class S3OwnerIdentity(TypedDict):
    principalId: str


class S3Bucket(TypedDict):
    name: str
    ownerIdentity: S3OwnerIdentity
    arn: str


class S3Object(TypedDict, total=False):
    key: str
    size: int
    eTag: str
    versionId: str
    sequencer: str


class S3Details(TypedDict):
    s3SchemaVersion: str
    configurationId: str
    bucket: S3Bucket
    object: S3Object


class S3GlacierRestoreEventData(TypedDict):
    lifecycleRestorationExpiryTime: str
    lifecycleRestoreStorageClass: str


class S3GlacierEventData(TypedDict):
    restoreEventData: S3GlacierRestoreEventData


class S3Message(TypedDict, total=False):
    """S3 event message structure"""
    eventVersion: str
    eventSource: str
    awsRegion: str
    eventTime: str
    eventName: str
    userIdentity: S3UserIdentity
    requestParameters: S3RequestParameters
    responseElements: S3ResponseElements
    s3: S3Details
    glacierEventData: S3GlacierEventData


class S3Event(TypedDict):
    Records: List[S3Message]
