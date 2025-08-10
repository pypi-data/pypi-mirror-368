from typing_extensions import TypedDict

from .CommonResponse import ResponseMetadata


class SendEmailResponse(TypedDict):
    """Response from SES send_email."""

    MessageId: str
    ResponseMetadata: ResponseMetadata
