from typing import List
from typing_extensions import TypedDict, NotRequired

from .CommonResponse import ResponseMetadata
from .TemplateMetadata import TemplateMetadata


class ListTemplatesResponse(TypedDict):
    """Response from SES list_templates."""

    TemplatesMetadata: List[TemplateMetadata]
    ResponseMetadata: ResponseMetadata
    NextToken: NotRequired[str]
