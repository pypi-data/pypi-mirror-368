from typing import TypedDict
from botocore.response import StreamingBody

class GetMediaResponse(TypedDict):
    ContentType: str
    Payload: StreamingBody