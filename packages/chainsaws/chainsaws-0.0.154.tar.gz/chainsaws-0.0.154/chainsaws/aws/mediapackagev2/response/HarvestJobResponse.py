from typing import Literal, TypedDict
from datetime import datetime
from chainsaws.aws.shared.pagination import PaginatedResponse

HarvestJobStatus = Literal['QUEUED', 'IN_PROGRESS', 'CANCELLED', 'COMPLETED', 'FAILED']

class Manifest(TypedDict):
    ManifestName: str

class HarvestedManifests(TypedDict):
    HlsManifests: list[Manifest]
    DashManifests: list[Manifest]
    LowLatencyHlsManifests: list[Manifest]

class ScheduleConfiguration(TypedDict):
    StartTime: datetime
    EndTime: datetime

class S3Destination(TypedDict):
    BucketName: str
    DestinationPath: str

class Destination(TypedDict):
    S3Destination: S3Destination

class HarvestJobResponse(TypedDict):
    ChannelGroupName: str
    ChannelName: str
    OriginEndpointName: str
    Destination: Destination
    HarvestJobName: str
    HarvestedManifests: HarvestedManifests
    Description: str
    ScheduleConfiguration: ScheduleConfiguration
    Arn: str
    CreatedAt: datetime
    ModifiedAt: datetime
    Status: HarvestJobStatus
    ErrorMessage: str
    ETag: str
    Tags: dict[str, str]


CreateHarvestJobResponse = HarvestJobResponse
GetHarvestJobResponse = HarvestJobResponse

class ListHarvestJobsResponse(PaginatedResponse[HarvestJobResponse]):
    pass