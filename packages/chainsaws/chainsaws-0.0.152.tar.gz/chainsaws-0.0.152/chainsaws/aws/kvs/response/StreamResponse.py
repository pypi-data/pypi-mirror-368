from typing import TypedDict, Literal
from datetime import datetime

from chainsaws.aws.shared.pagination import PaginatedResponse

class CreateStreamResponse(TypedDict):
    StreamARN: str

class StreamInfo(TypedDict):
    DeviceName: str
    StreamName: str
    StreamARN: str
    MediaType: str
    KmsKeyId: str
    Version: str
    Status: Literal["CREATING", "ACTIVE", "UPDATING", "DELETING"]
    CreationTime: datetime
    DataRetentionInHours: int

class GetStreamResponse(TypedDict):
    StreamInfo: StreamInfo


class ListStreamsResponse(PaginatedResponse[StreamInfo]):
    pass