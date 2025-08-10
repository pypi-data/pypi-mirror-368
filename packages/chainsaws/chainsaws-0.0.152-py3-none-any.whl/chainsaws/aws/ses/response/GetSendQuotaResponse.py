from typing_extensions import TypedDict

from .CommonResponse import ResponseMetadata


class GetSendQuotaResponse(TypedDict):
    """Response from SES get_send_quota."""

    Max24HourSend: float
    MaxSendRate: float
    SentLast24Hours: float
    ResponseMetadata: ResponseMetadata
