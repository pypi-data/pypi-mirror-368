from typing import TypedDict
from datetime import datetime

from chainsaws.aws.shared.pagination import PaginatedResponse


class ChannelGroupResponse(TypedDict):
    ChannelGroupName: str
    Arn: str
    EgressDomain: str
    CreatedAt: datetime
    ModifiedAt: datetime
    ETag: str
    Description: str
    Tags: dict[str, str]


CreateChannelGroupResponse = ChannelGroupResponse
GetChannelGroupResponse = ChannelGroupResponse
UpdateChannelGroupResponse = ChannelGroupResponse

class ListChannelGroupsResponse(PaginatedResponse[ChannelGroupResponse]):
    pass