from typing import TypedDict
from datetime import datetime
from chainsaws.aws.shared.pagination import PaginatedResponse


class IngestEndpoint(TypedDict):
    Id: str
    Url: str

class InputSwitchConfiguration(TypedDict):
    MQCSInputSwitching: bool

class OutputHeaderConfiguration(TypedDict):
    PublishMQCS: bool

class ChannelResponse(TypedDict):
    Arn: str
    ChannelName: str
    ChannelGroupName: str
    CreatedAt: datetime
    ModifiedAt: datetime
    Description: str
    IngestEndpoints: list[IngestEndpoint]
    InputType: str
    ETag: str
    Tags: dict[str, str]
    InputSwitchConfiguration: InputSwitchConfiguration
    OutputHeaderConfiguration: OutputHeaderConfiguration


CreateChannelResponse = ChannelResponse
UpdateChannelResponse = ChannelResponse

class GetChannelResponse(ChannelResponse):
    ResetAt: datetime


class ListChannelsResponse(PaginatedResponse[ChannelResponse]):
    pass


class ResetChannelStatsResponse(ChannelResponse):
    ChannelGroupName: str
    ChannelName: str
    Arn: str
    ResetAt: datetime