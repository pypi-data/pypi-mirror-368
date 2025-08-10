from datetime import datetime
from typing_extensions import TypedDict, NotRequired


class TemplateMetadata(TypedDict, total=False):
    """Metadata for an SES template."""

    Name: NotRequired[str]
    CreatedTimestamp: NotRequired[datetime]
