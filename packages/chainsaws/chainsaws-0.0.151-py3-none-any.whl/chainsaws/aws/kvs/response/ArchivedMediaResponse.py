from typing import TypedDict, List, Optional
from datetime import datetime
from botocore.response import StreamingBody

class GetClipResponse(TypedDict):
  ContentType: str
  Payload: StreamingBody

class GetDashStreamingSessionUrlResponse(TypedDict):
  DASHStreamingSessionURL: str

class GetHlsStreamingSessionUrlResponse(TypedDict):
  HLSStreamingSessionURL: str

class GetMediaForFragmentListResponse(TypedDict):
  ContentType: str
  Payload: StreamingBody


class Fragment(TypedDict):
  FragmentTimecode: str
  FragmentNumber: str
  ProducerTimestamp: datetime
  ServerTimestamp: datetime
  FragmentLengthInMilliseconds: int

class ListFragmentsResponse(TypedDict):
  Fragments: List[Fragment]
  NextToken: Optional[str]