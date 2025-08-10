"""SES Response Type Definitions."""

from .CommonResponse import ResponseMetadata
from .SendEmailResponse import SendEmailResponse
from .SendTemplatedEmailResponse import SendTemplatedEmailResponse
from .GetSendQuotaResponse import GetSendQuotaResponse
from .TemplateMetadata import TemplateMetadata
from .Template import Template
from .GetTemplateResponse import GetTemplateResponse
from .ListTemplatesResponse import ListTemplatesResponse

__all__ = [
    "ResponseMetadata",
    "SendEmailResponse",
    "SendTemplatedEmailResponse",
    "GetSendQuotaResponse",
    "TemplateMetadata",
    "Template",
    "GetTemplateResponse",
    "ListTemplatesResponse",
]
