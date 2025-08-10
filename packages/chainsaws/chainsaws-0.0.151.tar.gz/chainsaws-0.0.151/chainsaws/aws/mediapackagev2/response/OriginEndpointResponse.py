from typing import TypedDict, Literal, Optional, List, Dict
from datetime import datetime
from chainsaws.aws.shared.pagination import PaginatedResponse

from chainsaws.aws.mediapackagev2.mediapackagev2_models import (
    OriginEndpointSegment,
    HLSManifests,
)

OriginContainerType = Literal["HLS", "CMAF"]

class OriginEndpointHlsManifestResponse(TypedDict):
    ManifestName: str
    ChildManifestName: str
    Url: str


class OriginEndpointDashManifestResponse(TypedDict):
    ManifestName: str
    Url: str


class OriginEndpointForceEndpointErrorConfiguration(TypedDict):
    EndpointErrorCounditions: List[Literal['STALE_MANIFEST','INCOMPLETE_MANIFEST','MISSING_DRM_KEY','SLATE_INPUT']]


class ListOriginEndpointResponseItem(TypedDict):
    Arn: str
    ChannelGroupName: str
    ChannelName: str
    OriginEndpointName: str
    ContainerType: OriginContainerType
    Description: Optional[str]
    CreatedAt: datetime
    ModifiedAt: datetime
    HlsManifests: List[OriginEndpointHlsManifestResponse]
    LowLatencyHlsManifests: List[OriginEndpointHlsManifestResponse]
    DashManifests: List[OriginEndpointDashManifestResponse]
    ForceEndpointErrorConfiguration: OriginEndpointForceEndpointErrorConfiguration


class OriginEndpointResponse(ListOriginEndpointResponseItem):
    Segment: OriginEndpointSegment
    StartOverWindowSeconds: int
    HlsManifests: List[HLSManifests]
    LowLatencyHlsManifests: List[HLSManifests]
    # TODO: Add DashManifests
    ForceEndpointErrorConfiguration: OriginEndpointForceEndpointErrorConfiguration
    ETag: str
    Tags: Optional[Dict[str, str]]


class CreateOriginEndpointResponse(OriginEndpointResponse):
    pass


class UpdateOriginEndpointResponse(OriginEndpointResponse):
    pass


class GetOriginEndpointResponse(OriginEndpointResponse):
    pass


class ListOriginEndpointsResponse(PaginatedResponse[ListOriginEndpointResponseItem]):
    pass


class ResetOriginEndpointStateResponse(TypedDict):
    ChannelGroupName: str
    ChannelName: str
    OriginEndpointName: str
    Arn: str
    ResetAt: datetime