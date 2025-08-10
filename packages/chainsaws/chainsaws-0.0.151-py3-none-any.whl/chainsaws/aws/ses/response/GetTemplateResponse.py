from typing_extensions import TypedDict

from .CommonResponse import ResponseMetadata
from .Template import Template


class GetTemplateResponse(TypedDict):
    """Response from SES get_template."""

    Template: Template
    ResponseMetadata: ResponseMetadata
