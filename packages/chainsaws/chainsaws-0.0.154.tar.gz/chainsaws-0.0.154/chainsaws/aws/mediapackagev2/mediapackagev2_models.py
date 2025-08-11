from chainsaws.aws.shared.config import APIConfig
from dataclasses import dataclass
from typing import Literal, TypedDict, Dict, List
from datetime import datetime

@dataclass
class MediaPackageV2APIConfig(APIConfig):
    """Configuration for MediaPackageV2."""
    pass


ChannelInputType = Literal["HLS", "CMAF"]


class InputSwitchConfiguration(TypedDict):
    MQCSInputSwitching: bool

class OutputHeaderConfiguration(TypedDict):
    PublishMQCS: bool

# Origin Endpoint
OriginEndpointContainerType = Literal['TS', 'CMAF']

class OriginEndpointSegment(TypedDict):
    SegmentDurationSeconds: int
    SegmentName: str
    TsUseAudioRenditionGroup: bool
    IncludeIframeOnlyStreams: bool
    TsIncludeDvbSubtitles: bool
    Scte: Dict[Literal['ScteFilter'], list[Literal['SPLICE_INSERT', 'BREAK', 'PROVIDER_ADVERTISEMENT', 'DISTRIBUTOR_ADVERTISEMENT', 'PROVIDER_PLACEMENT_OPPORTUNITY', 'DISTRIBUTOR_PLACEMENT_OPPORTUNITY', 'PROVIDER_OVERLAY_PLACEMENT_OPPORTUNITY', 'DISTRIBUTOR_OVERLAY_PLACEMENT_OPPORTUNITY', 'PROGRAM']]]


class OriginEndpointSegmentEncryptionMethod(TypedDict):
    TsEncryptionMethod: Literal['AES_128', 'SAMPLE_AES']
    CmafEncryptionMethod: Literal['CENC', 'CBCS']


class OriginEndpointSegmentSpekeEncryptionContractConfiguration(TypedDict):
    PresetSpeke20Audio: Literal['PRESET_AUDIO_1', 'PRESET_AUDIO_2', 'PRESET_AUDIO_3', 'SHARED', 'UNENCRYPTED']
    PresetSpeke20Video: Literal['PRESET_VIDEO_1', 'PRESET_VIDEO_2', 'PRESET_VIDEO_3', 'PRESET_VIDEO_4', 'PRESET_VIDEO_5', 'PRESET_VIDEO_6', 'PRESET_VIDEO_7', 'PRESET_VIDEO_8', 'SHARED', 'UNENCRYPTED']


class OriginEndpointSegmentSpekeKeyProvider(TypedDict):
    EncryptionContractConfiguration: OriginEndpointSegmentSpekeEncryptionContractConfiguration
    ResourceId: str
    DrmSystems: list[Literal['CLEAR_KEY_AES_128', 'FAIRPLAY', 'PLAYREADY', 'WIDEVINE', 'IRDETO']]
    RoleArn: str
    Url: str


class OriginEndpointSegmentEncryption(TypedDict):
    ConstantInitializationVector: str
    EncryptionMethod: OriginEndpointSegmentEncryptionMethod
    KeyRotationIntervalSeconds: int
    SpekeKeyProvider: OriginEndpointSegmentSpekeKeyProvider

# HLS Manifests

class HLSManifestFilterConfiguration(TypedDict):
    ManifestFilter: str
    Start: datetime
    End: datetime
    TimeDelaySeconds: int
    ClipStartTime: datetime


class HLSManifestsStartTag(TypedDict):
    TimeOffset: float
    Precise: bool


class HLSManifests(TypedDict):
    ManifestName: str
    Url: str
    ChildManifestName: str
    ManifestWindowSeconds: int
    ProgramDateTimeIntervalSeconds: int
    ScteHls: Dict[Literal['AdMarkerHls'], Literal['DATERANGE']]
    FilterConfiguration: HLSManifestFilterConfiguration
    StartTag: HLSManifestsStartTag
    UrlEncodeChildManifest: bool

# Endpoint Error Configuration

class ForceEndpointErrorConfiguration(TypedDict):
    EndpointErrorCounditions: List[Literal['STALE_MANIFEST','INCOMPLETE_MANIFEST','MISSING_DRM_KEY','SLATE_INPUT']]