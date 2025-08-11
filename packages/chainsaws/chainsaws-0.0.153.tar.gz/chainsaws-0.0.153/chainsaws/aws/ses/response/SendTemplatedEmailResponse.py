from typing_extensions import TypedDict

from .CommonResponse import ResponseMetadata


class SendTemplatedEmailResponse(TypedDict):
    """Response from SES send_templated_email."""

    MessageId: str
    ResponseMetadata: ResponseMetadata
