from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from typing_extensions import TypedDict, NotRequired, Required

from chainsaws.aws.shared.config import APIConfig


class EmailFormat(str, Enum):
    """Email content format."""

    TEXT = "Text"
    HTML = "Html"
    BOTH = "Both"


class EmailPriority(str, Enum):
    """Email priority level."""

    HIGH = "1"
    NORMAL = "3"
    LOW = "5"


class EmailContent(TypedDict, total=False):
    """Email content configuration."""

    subject: Required[str]
    body_text: NotRequired[Optional[str]]
    body_html: NotRequired[Optional[str]]
    charset: NotRequired[str]


@dataclass
class EmailAddress:
    """Email address with optional name."""

    email: str  # Email address
    name: Optional[str] = None  # Display name

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} <{self.email}>"
        return str(self.email)


@dataclass
class SESAPIConfig(APIConfig):
    """Configuration for SES API."""

    default_region: str = field(default="ap-northeast-2")  # Default AWS region
    default_sender: Optional[EmailAddress] = None  # Default sender address
    default_format: EmailFormat = field(
        default=EmailFormat.BOTH)  # Default email format


class SendEmailConfig(TypedDict, total=False):
    """Configuration for sending email."""

    sender: Required[EmailAddress]
    recipients: Required[list[EmailAddress]]
    content: Required[EmailContent]
    cc: NotRequired[list[EmailAddress]]
    bcc: NotRequired[list[EmailAddress]]
    reply_to: NotRequired[list[EmailAddress]]
    priority: NotRequired[EmailPriority]
    tags: NotRequired[dict[str, str]]


class TemplateContent(TypedDict, total=False):
    """Email template content."""

    subject: Required[str]
    text: NotRequired[Optional[str]]
    html: NotRequired[Optional[str]]


class SendTemplateConfig(TypedDict, total=False):
    """Configuration for sending templated email."""

    template_name: Required[str]
    sender: Required[EmailAddress]
    recipients: Required[list[EmailAddress]]
    template_data: Required[dict[str, Any]]
    cc: NotRequired[list[EmailAddress]]
    bcc: NotRequired[list[EmailAddress]]
    tags: NotRequired[dict[str, str]]


class EmailQuota(TypedDict):
    """SES sending quota information."""

    max_24_hour_send: int
    max_send_rate: float
    sent_last_24_hours: int


class BulkEmailRecipient(TypedDict, total=False):
    """Recipient for bulk email sending."""

    email: Required[EmailAddress]
    template_data: NotRequired[dict[str, Any]]
    tags: NotRequired[dict[str, str]]


class BulkEmailConfig(TypedDict, total=False):
    """Configuration for bulk email sending."""

    sender: Required[EmailAddress]
    recipients: Required[list[BulkEmailRecipient]]
    template_name: NotRequired[str]
    content: NotRequired[EmailContent]
    batch_size: NotRequired[int]
    max_workers: NotRequired[int]
    email_format: NotRequired[EmailFormat]
